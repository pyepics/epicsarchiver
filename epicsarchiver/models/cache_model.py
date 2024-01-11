#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: cache_model.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to define the PVs model for the epicsarchiver package. It
# creates all of the necessary SQLAlchemy model classes for the PVs tables.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from sqlalchemy import Enum, Float, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicsarchiver.database import BASE


class PV(BASE):
    """Model for the pvs table."""

    __tablename__ = "pv"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(128))
    data_table: Mapped[str] = mapped_column(String(16))
    deadtime: Mapped[float] = mapped_column(Float, default=10.0)
    deadband: Mapped[float] = mapped_column(Float, default=0.00000001)
    graph_hi: Mapped[bytes] = mapped_column(LargeBinary)
    graph_lo: Mapped[bytes] = mapped_column(LargeBinary)
    graph_type: Mapped[str] = mapped_column(
        Enum("normal", "log", "discrete", name="graph_type_enum")
    )
    type: Mapped[str] = mapped_column(
        Enum("int", "double", "string", "enum", name="type_enum"),
        nullable=False,
    )
    active: Mapped[str] = mapped_column(
        Enum("yes", "no", name="active_enum"), default="yes"
    )

    # Relationship to the PVData model, Cache and Alert model
    pvdata = relationship("PVData", back_populates="pv")
    cache = relationship("Cache", back_populates="pv", uselist=False)
    alert = relationship("Alert", back_populates="pv", uselist=False)


class PVData(BASE):
    """Model for the pvdat table."""

    __tablename__ = "pvdata"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    time: Mapped[float] = mapped_column(Float, nullable=False)
    pv_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pv.id"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(String(4096))

    # Relationship to the PV model
    pv = relationship("PV", back_populates="pvdata")


class Cache(BASE):
    """Model for the cache table."""

    __tablename__ = "cache"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pvname: Mapped[str] = mapped_column(String(128), index=True)
    type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="int"
    )
    value: Mapped[str] = mapped_column(String(4096))
    cvalue: Mapped[str] = mapped_column(String(4096))
    ts: Mapped[float] = mapped_column(Float)
    active: Mapped[str] = mapped_column(
        Enum("yes", "no", name="active_enum"), default="yes"
    )

    # Relationship to the PV model
    pv_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pv.id"), nullable=False, index=True
    )


class Alert(BASE):
    """Model for the alert table."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pvname: Mapped[str] = mapped_column(
        String(128), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    mailto: Mapped[str] = mapped_column(String(1024))
    mailmsg: Mapped[str] = mapped_column(String(32768))
    trippoint: Mapped[bytes] = mapped_column(LargeBinary)
    timeout: Mapped[float] = mapped_column(Float, default=30.0)
    compare: Mapped[str] = mapped_column(
        Enum("eq", "ne", "le", "lt", "ge", "gt", name="compare_enum"),
        nullable=False,
        default="eq",
    )
    status: Mapped[str] = mapped_column(
        Enum("alarm", "ok", name="compare_enum"), nullable=False, default="ok"
    )
    active: Mapped[str] = mapped_column(
        Enum("yes", "no", name="compare_enum"), nullable=False, default="yes"
    )

    # Relationship to the PV model
    pv_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pv.id"), nullable=False, index=True
    )
