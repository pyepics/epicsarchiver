#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project: epicsarchiver
# File: cli_menu.py
# -----------------------------------------------------------------------------
# Purpose:
# This file is used to create a CLI menu for the epicsarchiver application.
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
# This software is distributed under the terms of the MIT license.
# -----------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Callable

from epicsarchiver.cli.utils import start_api


@dataclass
class MenuOption:
    """
    A dataclass for creating a menu option. This class is used to store the
    number, description, and action associated with a menu option.
    """

    number: int
    description: str
    action: Callable[[], None]


@dataclass
class CLIMenu:
    """
    A class for creating a CLI menu. This class is used to display a
    menu to the user and run the action associated with the user's choice.
    """

    help_function: Callable[[], None] = field(compare=False)
    _options: list[MenuOption] = field(
        init=False, compare=False, default_factory=list
    )

    def __post_init__(self) -> None:
        """Runs the configuration for the CLI menu."""
        self._configure_cli_menu()

    def _configure_cli_menu(self) -> None:
        """Configures the CLI menu."""
        # Create the menu options
        help_option = MenuOption(
            number=1,
            description="Display the help menu.",
            action=self.help_function,
        )
        api_option = MenuOption(
            number=2,
            description="Start the API.",
            action=start_api,
        )
        api_devel_option = MenuOption(
            number=3,
            description="Start the API in development mode.",
            action=lambda: start_api(devel=True),
        )

        # Add the menu options to the CLI menu
        self._options.append(help_option)
        self._options.append(api_option)
        self._options.append(api_devel_option)

    def _print_options(self) -> None:
        """Prints the menu options."""
        print("Menu Options:")
        for option in self._options:
            print(f"{option.number}. {option.description}")

    def display(self) -> None:
        """Runs the CLI menu until the user enters a valid choice."""
        valid_choice = False

        while not valid_choice:
            # Display the menu options
            self._print_options()
            # Get the user's choice
            choice = input("Please enter your choice: ")
            # Run the action associated with the user's choice if it is valid
            for option in self._options:
                if option.number == int(choice):
                    valid_choice = True
                    option.action()
                    return
            # Display an error message if the user's choice is invalid
            print(f"Invalid choice: {choice}. Please try again.")
