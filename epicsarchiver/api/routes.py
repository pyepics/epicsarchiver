#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: routes.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to create the API router for the epicsarchiver application.
# This allows to split the FastAPI application instance into multiple smaller
# routers.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from fastapi import APIRouter


# Create the API router
api_router = APIRouter()
