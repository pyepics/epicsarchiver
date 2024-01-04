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

from fastapi import FastAPI


# Expose the FastAPI application instance
__all__ = ["app"]


# Create the FastAPI application
app = FastAPI(
    title="EPICS Archiver",
    description="Archiving Epics PVs with Python and SQL",
    version="0.1.0",
    license_info={
        "name": "MIT",
        "url": "https://github.com/pyepics/epicsarchiver/blob/main/LICENSE",
    },
)
