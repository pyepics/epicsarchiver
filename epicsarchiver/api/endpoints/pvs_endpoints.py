#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: pvs_endpoints.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to define the API routes for the alerts functionality of
# the epicsarchiver application. It creates a FastAPI router instance and adds
# the necessary routes to it.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from epicsarchiver.database import get_database
from epicsarchiver.schemas import PV
from epicsarchiver.crud import get_pvs


pvs_router = APIRouter()

# parent route: /pvs


@pvs_router.get("/", response_model=list[PV], tags=["pvs"])
async def get_some_pvs(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_database)
) -> list[PV]:
    """Returns a list of PVs."""
    return get_pvs(db, skip=skip, limit=limit)
