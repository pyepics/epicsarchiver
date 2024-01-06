#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: crud.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to manage the database connections for the epicsarchiver
# package. It creates, reads, updates, and deletes the database entries.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from epicsarchiver.models import PV


async def get_pvs(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[PV]:
    """Returns a list of PVs."""
    result = await db.execute(select(PV).offset(skip).limit(limit))
    return result
