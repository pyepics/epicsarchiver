#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: __init__.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to initialize the epicsarchiver cli package.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from dataclasses import dataclass, field

from epicsarchiver.cli.cli_arguments import CLIArguments
from epicsarchiver.cli.cli_menu import CLIMenu


__all__ = ["CLI"]


# ASCII text banner for the CLI application
CLI_BANNER = r"""
$$$$$$$$\ $$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\         $$$$$$\  $$$$$$$\   $$$$$$\  $$\   $$\ $$$$$$\ $$\    $$\ $$$$$$$$\ $$$$$$$\
$$  _____|$$  __$$\\_$$  _|$$  __$$\ $$  __$$\       $$  __$$\ $$  __$$\ $$  __$$\ $$ |  $$ |\_$$  _|$$ |   $$ |$$  _____|$$  __$$\
$$ |      $$ |  $$ | $$ |  $$ /  \__|$$ /  \__|      $$ /  $$ |$$ |  $$ |$$ /  \__|$$ |  $$ |  $$ |  $$ |   $$ |$$ |      $$ |  $$ |
$$$$$\    $$$$$$$  | $$ |  $$ |      \$$$$$$\        $$$$$$$$ |$$$$$$$  |$$ |      $$$$$$$$ |  $$ |  \$$\  $$  |$$$$$\    $$$$$$$  |
$$  __|   $$  ____/  $$ |  $$ |       \____$$\       $$  __$$ |$$  __$$< $$ |      $$  __$$ |  $$ |   \$$\$$  / $$  __|   $$  __$$<
$$ |      $$ |       $$ |  $$ |  $$\ $$\   $$ |      $$ |  $$ |$$ |  $$ |$$ |  $$\ $$ |  $$ |  $$ |    \$$$  /  $$ |      $$ |  $$ |
$$$$$$$$\ $$ |     $$$$$$\ \$$$$$$  |\$$$$$$  |      $$ |  $$ |$$ |  $$ |\$$$$$$  |$$ |  $$ |$$$$$$\    \$  /   $$$$$$$$\ $$ |  $$ |
\________|\__|     \______| \______/  \______/       \__|  \__|\__|  \__| \______/ \__|  \__|\______|    \_/    \________|\__|  \__|
"""  # noqa: E501


@dataclass
class CLI:
    """A dataclass for creating a CLI instance."""

    args: list[str]
    _cli_arguments: CLIArguments = field(init=False, compare=False, repr=False)
    _cli_menu: CLIMenu = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        self._cli_arguments = CLIArguments(args=self.args)
        self._cli_menu = CLIMenu(
            help_function=self._cli_arguments.parser.print_help
        )

    def start(self) -> None:
        """Starts the epicsarchiver CLI application."""
        # Display the CLI banner
        print(CLI_BANNER)

        if len(self.args) >= 1:
            # Parse the command line arguments if there are any
            self._cli_arguments.parse()
        else:
            # Display the default CLI menu if there are no arguments
            self._cli_menu.display()
