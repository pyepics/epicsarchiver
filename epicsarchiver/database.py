#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: database.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to manage the database connections for the epicsarchiver
# package. It creates and configures the database engine and session, and
# provides a utility function for getting a database session.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

# Load the environment variables from the .env file
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Create the async engine for SQLAlchemy
ENGINE = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}, echo=True, future=True
)

# Create the sessionmaker with the async engine
SESSION = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=ENGINE,
    expire_on_commit=False,
    future=True,
)

# Base for all models
BASE = declarative_base()
