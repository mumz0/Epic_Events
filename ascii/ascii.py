"""
This module contains the Ascii class which provides ASCII art for Epic Events.
"""


class Ascii:
    """
    A class to generate ASCII art representations.
    This class provides methods to return ASCII art for various purposes,
    such as logos or decorative text.
    """

    def epic_events(self):
        """
        Returns an ASCII art representation of the "Epic Events" logo.

        This method provides a multi-line string containing an ASCII art
        representation of the "Epic Events" logo, which can be used for
        display purposes in the application.

        Returns:
            str: A string containing the ASCII art of the "Epic Events" logo.
        """
        epic_events = r"""
╔────────────────────────────────────────────────────╗
│ _____       _        _____                 _       │
│| ____|_ __ (_) ___  | ____|_   _____ _ __ | |_ ___ │
│|  _| | '_ \| |/ __| |  _| \ \ / / _ \ '_ \| __/ __|│
│| |___| |_) | | (__  | |___ \ V /  __/ | | | |_\__ \│
│|_____| .__/|_|\___| |_____| \_/ \___|_| |_|\__|___/│
│      |_|                                           │
╚────────────────────────────────────────────────────╝
    """
        return epic_events
