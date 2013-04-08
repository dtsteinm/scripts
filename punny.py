#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: April 7, 2013

"""Generate puns for a given phrase."""
import Levenshtein

__all__ = ['PunGenerator']

class PunGenerator:
    """Generate the puns."""

    squid = ['ink','fin','gill','beak','kraken','mollusk']

    def __init__(self):
        self.puns = self.squid

    def select_pun(self, string):
        """Choose the best available pun."""
        
        best_pun = ('',0)

        for pun in self.puns:
            current_ratio = Levenshtein.ratio(pun, string)
            if current_ratio > best_pun[1]:
                best_pun = pun, current_ratio

        return best_pun[0]
