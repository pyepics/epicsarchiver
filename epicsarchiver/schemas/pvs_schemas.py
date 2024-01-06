#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: pvs_schemas.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to define the Pydantic schemas for the pvs functionality of
# the epicsarchiver application. It creates a Pydantic model for each database
# table and defines the necessary fields.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from pydantic import BaseModel, Field


class PVBase(BaseModel):
    """Base class for PV models."""

    name: str = Field(..., description="The name of the PV.")
    description: str = Field(..., description="The description of the PV.")
    data_table: str = Field(..., description="The name of the data table.")
    deadtime: float = Field(..., description="The deadtime of the PV.")
    deadband: float = Field(..., description="The deadband of the PV.")
    graph_hi: bytes = Field(..., description="The high graph of the PV.")
    graph_lo: bytes = Field(..., description="The low graph of the PV.")
    graph_type: str = Field(..., description="The graph type of the PV.")
    type: str = Field(..., description="The type of the PV.")


class PV(PVBase):
    """Class for retrieving PV models."""

    id: int = Field(..., description="The ID of the PV.")
    active: str = Field(..., description="The active status of the PV.")

    class Config:
        orm_mode = True
