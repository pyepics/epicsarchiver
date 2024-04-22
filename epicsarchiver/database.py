import os
import toml
import time
from datetime import datetime
from random import randint

from sqlalchemy import (MetaData, create_engine, and_, text, Table,
                        Column, ForeignKey, Integer, Float, String,
                        Text, DateTime, Enum, Boolean)

from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from .util import get_credentials, isotime

CREDENTIALS_ENVVAR = 'PVARCH_CREDENTIALS'

CONN_DEFAULT = {'server':'postgres', 'dialect':None,
                'host':'localhost', 'port':None, 'user':'',
                'password':'', 'pvarch_main': None}

def flush(engine):
    "flush session"
    with Session(engine) as session, session.begin():
        session.flush()

def get_all_dbs(engine):
    """get list of all DBs from engine"""
    if engine is None:
        return None
    if engine.name.startswith('post'):
        query = text("select datname from pg_database")
    elif engine.name.startswith('m'):
        query = text("show databases")
    return [row[0] for row in engine.connect().execute(query).fetchall()]


class SimpleDB:
    """ simple, non-orm sqlalchemy interface"""
    def __init__(self, dbname=None, warn_missing=True, **kws):
        
        conn = {k: v for k, v in CONN_DEFAULT.items()}
        conn.update(kws)
        if len(conn['user']) < 1:
            credfile = os.environ.get(CREDENTIALS_ENVVAR, None)
            if credfile is None:
                print(f"Warning: could not get DB user or credentials file: '{CREDENTIALS_ENVVAR}' not set")
            conn.update(get_credentials(CREDENTIALS_ENVVAR))
            
        conn_db = conn.pop('pvarch_main')
        if dbname is None:
            dbname = conn_db
        if dbname is None:
            raise ValueError('no database named')

        self.engine = self.connect(dbname, **conn)
        self.dbname = dbname
        self.connection_args = conn
        self.metadata = MetaData()
        self.tables = None
        self.conn = None
        try:
            self.metadata.reflect(self.engine)
            self.conn    = self.engine.connect()              
            self.tables  = self.metadata.tables
        except:
            if warn_missing:
                print(f"Warning: database '{dbname}' appears to not exist")

    def connect(self, dbname, server='sqlite', host='localhost',
                port=None, dialect=None, user='', password=''):
        """create database engine"""
        server = server.lower()
        if server.startswith('my'):
            if dialect is None:
                dialect = 'pymysql'
            if port is None:
                port = 3306
        elif server.startswith('maria'):
            if dialect is None:
                dialect = 'pymysql'
            if port is None:
                port = 3306
        elif server.startswith('post') or server.startswith('pg'):
            server = 'postgresql'
            if dialect is None:
                dialect = 'psycopg2'
            if port is None:
                port = 5432
        #
        if server == 'sqlite':
            conn_str = f'{server}:///{dbname}'
        else:
            conn = f'{user}:{password}@{host}:{port}/{dbname}'
            if dialect is None:
                conn_str = f'{server}://{conn}'
            else:
                conn_str= f'{server}+{dialect}://{conn}'

        return create_engine(conn_str)
        

    def close(self):
        "close session"
        flush(self.engine)

    def execute(self, query, flush=True):
        """general execute of query"""
        result = None
        with Session(self.engine) as session, session.begin():
            result = session.execute(query)
            if flush:
                session.flush()
        return result

    def insert(self, tablename, **kws):
        """insert to a table with keyword/value pairs"""
        tab = self.tables[tablename]
        self.execute(tab.insert().values(**kws))

    def set_info(self, key, value, set_modify_time=True, do_execute=True):
        """set key / alue in the info table
        do_execute=False to avoid executing, and only return query
        """
        tab = self.tables['info']
        val = self.get_rows('info', where={'key': key}, none_if_empty=True)
        ivals = {'value': value}
        if set_modify_time:
            ivals['modify_time'] = datetime.now()
        if val is None:
            ivals['key'] = key
            query = tab.insert().values(**ivals)
        else:
            query = tab.update().where(tab.c.key==key).values(**ivals)
        if do_execute:
            self.execute(query)
        return query

    def get_info(self, key=None, default=None, prefix=None, as_int=False,
                 as_bool=False, order_by='modify_time', full=False):
        """
        returns key: value dictionary from info table
        """
        where = {}
        if key is not None:
            where['key'] = key

        allrows = self.get_rows('info', where, order_by=order_by)
        def cast(val, as_int, as_bool):
            if (as_int or as_bool):
                if val is None:
                    val = 0
                try:
                    val = int(float(val))
                    if as_bool:
                        val = bool(val)
                except (ValueError, TypeError):
                    pass
            return val

        if prefix is None:
            if full:
                out = [(row.key, row) for row in allrows]                
            else:
                out = [(row.key, cast(row.value, as_int, as_bool)) for row in allrows]
        else:
            out = []
            for row in allrows:
                if row.key.startswith(prefix):
                    if full:
                        out.append((row.key, row))
                    else:
                        out.append((row.key, cast(row.value, as_int, as_bool)))                        
        return dict(out)

    def set_modify_time(self):
        """set modify_time in info table"""
        self.set_info('modify_time', isotime(), do_execute=True)

    def add_row(self, tablename, **kws):
        """add row to a table with keyword/value pairs  == insert()"""
        self.insert(tablename, **kws)

    def insert(self, tablename, **kws):
        """insert to a table with keyword/value pairs"""
        tab = self.tables[tablename]
        self.execute(tab.insert().values(**kws), set_modify_time=True)

    def table_error(self, message, tablename, funcname):
        raise ValueError(f"{message} for table '{tablename}' in {funcname}()")

    def handle_where(self, tablename, where=None, funcname=None, **kws):
        if funcname is None:
            funcname = 'handle_where'
        tab = self.tables.get(tablename, None)
        if tab is None:
            self.table_error(f"no table found", tablename, funcname)

        filters = []
        if where is None or isinstance(where, bool) and where:
            where = {}
            if len(kws) == 0:
                filters.append(True)

        if isinstance(where, int):
            if 'id' in tab.c:
                filters.append(tab.c.id==where)
            else:
                for colname, coldat in tab.columns.items():
                    if coldat.primary_key and isinstance(coldat.type, INTEGER):
                        filters.append(getattr(tab.c, colname)==where)
            if len(filters) == 0:
                self.table_error(f"could not interpret integer `where` value",
                                      tablename, funcname)
        elif isinstance(where, dict):
            where.update(kws)
            for keyname, val in where.items():
                key = getattr(tab.c, keyname, None)
                if key is None:
                    key = getattr(tab.c, "%s_id" % keyname, None)
                if key is None:
                    self.table_error(f"no column '{keyname}'", tablename, funcname)
                filters.append(key==val)
        return and_(*filters)

    def get_rows(self, tablename, where=None, order_by=None, limit_one=False,
                none_if_empty=False, **kws):
        """general-purpose select of row data:

        Arguments
        ----------
        tablename    name of table
        where        dict of key/value pairs for where clause [None]
        order_by     name of column to order by [None]
        limit_one    whether to limit result to 1 row [False[
        none_if_empty whether to return None for an empty row [False]
        kwargs        other keyword/value pairs are included in the `where` dictionary
        Returns
        -------
        rows matching `where` (all if `where=None`) optionally ordered by order_by

        Examples
        --------
        >>> db.get_rows('element', where{'z': 30})
        """
        tab = self.tables.get(tablename, None)
        if tab is None:
            self.table_error(f"no table found", tablename, 'get_rows')

        where = self.handle_where(tablename, where=where, funcname='get_rows', **kws)
        query = tab.select().where(where)

        order_key = None
        if order_by is None:
            order_key = getattr(tab.c, "id", None)
        else:
            order_key = getattr(tab.c, order_by, None)
            if order_key is None:
                order_key = getattr(tab.c, f"{order_by}_id", None)
            if order_key is None:
                self.table_error(f"no column '{order_by}'", tablename, 'get_rows')
        if order_key is not None:
            query = query.order_by(order_key)

        result = self.execute(query)
        if limit_one:
            result = result.fetchone()
        else:
            result = result.fetchall()

        if result is not None and len(result) == 0 and none_if_empty:
            result = None
        return result

    def lookup(self, tablename, **kws):
        """
        simple select of table with any equality filter on columns by name

        a simple wrapper for
           self.get_rows(tablename, limit_one=False, none_if_empty=False, **kws)
        """
        return self.get_rows(tablename, limit_one=False, none_if_empty=False, **kws)

    def update(self, tablename, where=None, **kws):
        """update a row (with where in a table
        using keyword args

        Arguments
        ----------
        tablename   name of table
        where       select row to update, either int for id or dict for key/val

        kws          values to update


        """
        tab = self.tables.get(tablename, None)
        if tab is None:
            self.table_error(f"no table found", tablename, 'update')

        where = self.handle_where(tablename, where=where, funcname='update')
        self.execute(tab.update().where(where).values(**kws), set_modify_time=True)

    def delete_rows(self, tablename, where):
        """delete rows from table

        Arguments
        ----------
        tablename   name of table
        where       rows to delete, either int for id or dict for key/val
        """
        tab = self.tables.get(tablename, None)
        if tab is None:
            self.table_error(f"no table found", tablename, 'delete')

        where = self.handle_where(tablename, where=where, funcname='delete')
        self.execute(tab.delete().where(where), set_modify_time=True)
    

def create_pvarch_main(dbname='pvarch_main', **kws):
    """Create pvarch_main database

    arguments:
    ---------
    dbname    name of database (filename for sqlite server)

    optional keywords:
    ------------------
    server    type of database server ([sqlite], mysql, postgresql)
    host      host serving database   (mysql,postgresql only)
    port      port number for database (mysql,postgresql only)
    user      user name for database (mysql,postgresql only)
    password  password for database (mysql,postgresql only)
    """
    
    db = SimpleDB(dbname, warn_missing=False, **kws)

    if database_exists(db.engine.url):
        raise ValueError(f"database {dbname} exists: cannot create")
    
    print(f"creating database '{dbname}'")
    create_database(db.engine.url)
           
    info = Table('info', db.metadata,
                 Column('key', String(256), primary_key=True, unique=True),
                 Column('value', Text),
                 Column('modify_time', DateTime, default=datetime.now),
                 Column('notes', Text))

    alerts = Table('alerts', db.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String(256), nullable=False, unique=True),
                   Column('pvname', String(128)),
                   Column('mailto', Text),
                   Column('mailmsg', Text),
                   Column('trippoint', Text),
                   Column('timeout', Float, default=30.0),
                   Column('compare',
                          Enum('eq','ne','le','lt','ge','gt', name='compare', create=True),
                          default='eq'),
                   Column('active', Boolean,  default=True))

    cache = Table('cache', db.metadata,
                  Column('id', Integer, primary_key=True),
                  Column('pvname', String(128)),
                  Column('value', Text),
                  Column('cvalue', Text),
                  Column('type', Text, default='int'),
                  Column('timestamp', Float),
                  Column('notes', Text),
                  Column('active', Boolean,  default=True))
    

    pairs = Table('pairs', db.metadata,
                  Column('pv1', None, ForeignKey('cache.id')),
                  Column('pv2', None, ForeignKey('cache.id')),
                  Column('score', Integer, default=1)
                  )
                  
    requests = Table('requests', db.metadata,
                     Column('pvname', String(128)),
                     Column('request_time', DateTime, default=datetime.now),
                     Column('action',
                            Enum('add','drop','ignore', name='action', create=True),
                            default='add'),
                     )
    
    runs = Table('runs', db.metadata,
                 Column('id', Integer, primary_key=True),
                 Column('dbname', Text),
                 Column('notes', Text),
                 Column('start_time', DateTime), 
                 Column('stop_time', DateTime)
                 )

    db.metadata.create_all(bind=db.engine)
    flush(db.engine)
    time.sleep(0.25)

    odb = SimpleDB(dbname, warn_missing=True,  **db.connection_args)
    
    for key, value in (("version", "3.0"),
                       ("cache_status", "offline"),
                       ("cache_pid", "0"),
                       ("cache_timestamp", "0"),
                       ("archiver_status",  "offline"),
                       ("archiver_dbname",  "pvdat_00001"),
                       ("archiver_prefix",  "pvdat"),
                       ("archiver_pid", "0"),
                       ("archiver_timestamp", "0"),
                       ("mail_server",    ""),
                       ("mail_from",    ""),
                       ("logdir",       ""),
                       ("cache_alert_period", "30"),
                       ("cache_report_period", "300")):
        odb.set_info(key, value, set_modify_time=True)

    return odb

def create_pvarch_data(maindb='pvarch_main'):
    """Create the next pvdata table for archiver

    arguments:
    ---------
    maindb    name of main EpicsArchiver databae
    """
    pvarch = SimpleDB(maindb)
    if pvarch.tables is None or 'info' not in pvarch.tables:  # not connected!
        raise ValueError(f"could not connect to main EpicsArchiver database {maindb}")
    
    info = pvarch.get_info(prefix='archiver_')
    main_data = info.get('archiver_dbname', None)
    main_prefix = info.get('archiver_prefix', 'pvdat')
    if main_prefix.endswith('_'):
        main_prefix = main_prefix[:-1]
        
    alldbs = get_all_dbs(pvarch.engine)

    dbname = None
    if main_data is not None:
        current_db = SimpleDB(main_data, warn_missing=False,
                              **pvarch.connection_args)
        if current_db.tables is None:  # db does not exist : needs to be created
            dbname = main_data
        else: 
            this_prefix, sindex = main_data.split('_', 1)
            try:
                index = int(sindex) + 1
            except:
                index = 0
            i, dbname = 0, alldbs[0]
            while dbname in alldbs and i < 10000:
                i += 1
                dbname =  f'{main_prefix:s}_{i+1:05d}'                
            if dbname in alldbs:
                raise ValueError(f"exhausted database names '{dbname}'")

    db = SimpleDB(dbname, warn_missing=False,
                   **pvarch.connection_args)

    if database_exists(db.engine.url):
        raise ValueError(f"database {dbname} exists: cannot create")

    print(f"Creating EpicsArchiver Database '{dbname}'")
    create_database(db.engine.url)

    pv = Table('pv', db.metadata,
               Column('id', Integer, primary_key=True),               
               Column('pvname', String(128), unique=True),
               Column('description', String(256)),
               Column('data_table', String(16), nullable=False),
               Column('active', Boolean,  default=True),
               Column('deadtime',  Float, default=10.0),
               Column('deadband',  Float, default=1.e-5),
               Column('data_type',
                      Enum('int','double','string','enum',
                           name='pvtype', create=True),
                          default='double'),
               Column('graph_type',
                      Enum('continuous','log','discrete',
                           name='graphtype', create=True),
                          default='continuous'),                      
               Column('graph_hi', Text),
               Column('graph_lo', Text),
               )

    dtabs = []
    for i in range(128):
        t = Table(f'pvdat{(i+1):03d}', db.metadata, 
                  Column('time', Float),
                  Column('pv_id', ForeignKey('pv.id')),
                  Column('value', Text))
        dtabs.append(t)
    
    db.metadata.create_all(bind=db.engine)
    flush(db.engine)

    time.sleep(0.25)
    return SimpleDB(dbname, **pvarch.connection_args)    
