#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: __init__.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to initialize the epicsarchiver package. It creates the
# FastAPI application and adds the necessary components to it.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from epicsarchiver.api import api_router
from epicsarchiver.database import ENGINE, BASE
from epicsarchiver.models import cache_model  # noqa: F401


# Expose the FastAPI application instance
__all__ = ["app"]


# Lifespan event handler for creating all database tables
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    async with ENGINE.begin() as conn:
        await conn.run_sync(BASE.metadata.create_all)
    yield


# Create the FastAPI application
app = FastAPI(
    title="EPICS Archiver",
    description="Archiving Epics PVs with Python and SQL",
    version="0.1.0",
    license_info={
        "name": "MIT",
        "url": "https://github.com/pyepics/epicsarchiver/blob/main/LICENSE",
    },
    docs_url="/api",
    lifespan=lifespan,
)

# Add the routers to the application
app.include_router(api_router, prefix="/api")
