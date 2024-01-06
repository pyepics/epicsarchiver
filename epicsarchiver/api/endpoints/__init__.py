#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: __init__.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to initialize the epicsarchiver.api.endpoints package.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from epicsarchiver.api.endpoints.pvs_endpoints import pvs_router


__all__ = ["pvs_router"]
