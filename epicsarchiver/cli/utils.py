#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: utils.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to create utility functions that are used throughout the
# epicsarchiver application.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# ----------------------------------------------------------------------------

from uvicorn import run


# Starts the API server using Uvicorn with an optional development mode.
def start_api(devel: bool = False) -> None:
    """Starts the FastAPI application instance with Uvicorn."""
    run(app="epicsarchiver:app", host="0.0.0.0", port=8000, reload=devel)
