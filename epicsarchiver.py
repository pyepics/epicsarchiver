#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: epicsarchiver.py
# -----------------------------------------------------------------------------
# Purpose:
# This is the main entry point for the epicsarchiver application. It is used
# to run the FastAPI application instance with Uvicorn in reload mode. This
# allows the application to be run in a development environment.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from uvicorn import run

from epicsarchiver import app  # noqa: F401


if __name__ == "__main__":
    # Run the FastAPI application instance with Uvicorn in reload mode.
    run(app="epicsarchiver:app", host="0.0.0.0", port=8000, reload=True)
