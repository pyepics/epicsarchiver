#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: epicsarchiver.py
# -----------------------------------------------------------------------------
# Purpose:
# This is the main entry point for the epicsarchiver application. This file
# starts the command line interface for running the cli application.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

import sys

from epicsarchiver.cli import CLI


def main() -> None:
    """The main entry point for the epicsarchiver application."""
    epicsarchiver_cli = CLI(args=sys.argv[1:])
    epicsarchiver_cli.start()


if __name__ == "__main__":
    main()
