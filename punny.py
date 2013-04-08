#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: April 7, 2013

'''Generate puns for a given phrase.'''
import Levenshtein

__all__ = ['PunGenerator']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.1'
__license__ = 'WTFPL'

class PunGenerator:
    '''Generate the puns.'''

    # TODO: Add other pun lists
    # TODO: Use dictionaries with preferred replacements:
    #       f.e. 'mouth' -> 'beak'
    squid = ['ink','fin','gill','beak','kraken','mollusk']

    # TODO: Allow choosing pun list on object creation
    def __init__(self):
        # Sort the list of puns by length; might come in handy 
        # if we want to try to optimize the comparisons.
        self.puns = sorted(self.squid, key=lambda pun: len(pun))

    def select_pun(self, string):
        '''Choose the best available pun.'''
        
        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = ('',0)

        # Compare each pun option; better puns replace earlier options.
        for pun in self.puns:
            current_ratio = Levenshtein.ratio(pun, string)
            if current_ratio > best_pun[1]:
                best_pun = pun, current_ratio

        # Return both the pun itself, and the ratio so that 
        # generate_pun() can find the best pun for a phrase.
        return best_pun

    def generate_pun(self, string):
        '''Given a phrase, replace the best pun possibility.'''

        self.string = string.strip()

        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = ('',0)

        # Find the best word to use and it's corresponding best pun.
        # TODO: Allow for sub-string replacements, f.e. 'ink-vade'
        for word in self.string.split():
            new_pun = self.select_pun(word)
            if new_pun[1] > best_pun[1]:
                best_pun = new_pun
                to_replace = word

        pun = self.string.replace(to_replace, best_pun[0])
        return pun.capitalize()

    def add_pun(self, string):
        '''Add a new pun to the list of available puns.'''

        # Add a new pun to the list, and re-sort it by length.
        self.puns.append(string)
        self.puns = sorted(self.puns, key=lambda pun: len(pun))
