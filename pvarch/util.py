#!/usr/bin/env python

import os
import toml
import time
from datetime import datetime
from random import randint
from charset_normalizer import from_bytes

from sqlalchemy import (MetaData, and_, create_engine, text, func,
                        Table, Column, ColumnDefault, ForeignKey,
                        Integer, Float, String, Text, DateTime,
                        UniqueConstraint, Enum, Boolean)

from sqlalchemy.orm import Session, mapper, relationship

from sqlalchemy_utils import database_exists, create_database


string_literal = str

MAX_EPOCH = 2147483647.0   # =  2**31 - 1.0 (max unix timestamp)
SEC_DAY   = 86400.0

motor_fields = ('.VAL','.OFF','.FOFF','.SET','.HLS','.LLS',
                '.DIR','_able.VAL','.SPMG')

valid_pvstr = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:._-+:[]<>;{}'

class Config:
    def __init__(self, **kws):
        self.logdir =  '/var/log/pvarch'

        self.server = 'postgres'  # or 'mariadb'
        self.host = 'localhost'
        self.user = 'epics'
        self.password = 'change_this_password!'
        self.sql_dump = '/usr/bin/maridb-dump'

        self.mail_server =  'localhost'
        self.mail_from = 'pvarch@aps.anl.gov'
        self.cache_db = 'pvarch_main'
        self.dat_prefix = 'pvdata'

        for key, val in kws.items():
            setattr(self, key, val)

    def asdict(self):
        out = {}
        for k in dir(self):
            if (k.startswith('__') and k.endswith('__')) or  k in ('asdict', ):
                continue
            out[k] = getattr(self, k)
        return out

def get_config(envvar='PVARCH_CONFIG', **kws):
    """read config file defined by environmental variable PVARCH_CONFIG"""
    fconf = os.environ.get(envvar, None)
    conf = {}
    if fconf is not None and os.path.exists(fconf):
        conf.update(toml.load(open(fconf)))
    conf.update(kws)
    return Config(**conf)

def isotime(dtime=None, sep=' '):
    if dtime is None:
        dtime = datetime.now()
    return datetime.isoformat(dtime, sep=sep)

def get_credentials(envvar):
    """look up credentials environment variable or filename"""
    conn = {}
    credfile = os.environ.get(envvar, None)
    if credfile is not None and os.path.exists(credfile):
        return read_credentials_file(credfile)
    elif os.path.exists(envvar):
        return read_credentials_file(envvar)        

def read_credentials_file(fname):
    """read credentials file"""
    with open(fname, 'rb') as fh:
        text = str(from_bytes(fh.read()).best())            
    return toml.loads(text)


def None_or_one(result):
    """expect result (as from query.fetchall() to return
    either None or exactly one result
    """
    if len(result) == 1:
        return result[0]
    elif len(result) ==  0:
        return None
    try:
        return result[0]
    except:
        return None


def clean_bytes(x, maxlen=4090, encoding='utf-8'):
    """
    clean data as a string with comments stripped,
    guarding against extra sql statements,
    and force back to bytes object / utf-8
    """
    if isinstance(x, bytes):
        x = x.decode(encoding)
    if not isinstance(x, str):
        x = str(x)
    for char in (';', '#'):
        eol = x.find(char)
        if eol > -1:
            x = x[:eol]
    return x.strip().encode(encoding)

def clean_string(x, maxlen=4090):
    return clean_bytes(x, maxlen=maxlen).decode('utf-8')

def safe_string(x):
    return string_literal(x)

def clean_mail_message(s):
    "cleans a stored escaped mail message for real delivery"
    s = s.strip()
    s = s.replace("\\r","\r").replace("\\n","\n")
    s = s.replace("\\'","\'").replace("\\","").replace('\\"','\"')
    return s


def valid_pvname(pvname):
    return all([c in valid_pvstr for c in pvname])

def normalize_pvname(p):
    """ normalizes a PV name (so that it ends in .VAL if needed)."""
    pvname = clean_string(p, maxlen=128).strip()
    if '.' not in pvname:
        pvname = "%s.VAL" % pvname
    return pvname

def get_pvpair(pv1, pv2):
    "fix and sort 2 pvs for use in the pairs tables"
    p = [normalize_pvname(pv1), normalize_pvname(pv2)]
    p.sort()
    return tuple(p)

def clean_mail_message(s):
    "cleans a stored escaped mail message for real delivery"
    s = s.strip()
    s = s.replace("\\r","\r").replace("\\n","\n")
    s = s.replace("\\'","\'").replace("\\","").replace('\\"','\"')
    return s

def get_force_update_time():
    """ inserts will be forced into the Archives for stale values
    between 17 and 24 hours after last insert.
    This will spread out forced inserts, but still mean that each
    PV is recorded at least once in any 24 hour period.
    """
    return randint(17*3600, 23*3600)

def timehash2timestamp(thash):
    """ convert timehash to timestamp"""
    return int(thash, 16)/5.e3


def tformat(t=None,format="%Y-%b-%d %H:%M:%S"):
    """ time formatting"""
    if t is None: t = time.time()
    return time.strftime(format, time.localtime(t))

def time_sec2str(sec=None):
    return tformat(t=sec,format="%Y-%m-%d %H:%M:%S")

def time_str2sec(s):
    s = s.replace('_',' ')
    xdat,xtim=s.split(' ')
    dates = xdat.split('-')
    times = xtim.split(':')

    (yr,mon,day,hr,min,sec,x,y,tz) = time.localtime()
    if   len(dates)>=3:  yr,mon,day = dates
    elif len(dates)==2:  mon,day = dates
    elif len(dates)==1:  day = dates[0]

    min,sec = 0,0
    if   len(times)>=3:  hr,min,sec = times
    elif len(times)==2:  hr,min  = times
    elif len(times)==1:  hr  = times[0]

    return time.mktime((int(yr),int(mon),int(day),int(hr),int(min), int(sec),0,0,tz))


def write_saverestore(pvvals, format='plain', header=None):
    """ generate a save/restore file for a set of PV values

    pvvals is a dict, list, or tuple of (pvname,value) pairs
    format can be
        plain   plain save/restore file
        python  python script
    header: list of additional header/comment lines
    """
    out = []
    if format.lower().startswith('py'):
        out.append(f"#!/usr/bin/env python")
        out.append("#  Python save restore script")
        out.append("from epics import caput")
        xfmt = "caput('%s', %s)"
    else:
        out.append("# Plain Save/Restore script")
        xfmt = "%s  %s"

    if header is not None:
        for h in header:
            out.append(f"# {h}")

    if isinstance(pvvals, dict):
        pvvals = pvvals.items()
           
    for pv, val in pvvals:
        out.append(xfmt  % (pv, val))
    out.append('')
    return '\n'.join(out)

