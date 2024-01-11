#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: cli_arguments.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to create the command line arguments for the epicsarchiver
# application.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from argparse import ArgumentParser
from dataclasses import dataclass, field

from epicsarchiver.cli.utils import start_api


@dataclass
class CLIArguments:
    """A dataclass for creating the command line arguments instance."""

    args: list[str]
    _parser: ArgumentParser = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        """Runs the configuration for the command line arguments."""
        self._configure_parser()

    def _configure_parser(self) -> None:
        """Configures the command line argument parser."""
        # Create the command line argument parser
        self._parser = ArgumentParser(
            prog="epicsarchiver",
            description="A command line interface for epicsarchiver.",
            add_help=False,
        )

        # Add the command line arguments
        self._parser.add_argument(
            "-h",
            "--help",
            dest="help",
            action="store_true",
            help="Displays the help menu.",
        )
        self._parser.add_argument(
            "-a",
            "--api",
            dest="api",
            action="store_true",
            help="Starts the API server.",
        )
        self._parser.add_argument(
            "-d",
            "--devel",
            dest="devel",
            action="store_true",
            help="Starts the API server in development mode.",
        )

    def parse(self) -> None:
        """Parses a command line argument and runs the associated action."""
        # Parse the command line arguments if there are any
        arguments = self._parser.parse_args(self.args)

        # Check the arguments
        if arguments.api:
            # Start the API if the user specifies the "api" command
            start_api()
        elif arguments.devel:
            # Start the API in development mode
            start_api(devel=True)
        elif arguments.help:
            # Display the help menu if the user specifies the "help" command
            self._parser.print_help()
