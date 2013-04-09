#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: April 7, 2013

'''Generate puns for a given phrase.'''
# TODO: difflib might be good enough...
import Levenshtein as leven

__all__ = ['PunGenerator']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.2.6'
__license__ = 'WTFPL'


class PunGenerator:
    '''Generate the puns.'''

    # TODO: Add other pun dictionaries
    # TODO: Add automatic words for other puns
    squid = {
            'ink':      [('going', 'goink'), ('invade', 'inkvade')],
            'fin':      [('', None), ],
            'gill':     [('', None), ],
            'kelp':     [('hell', None), ('heck', None)],
            'keel':     [('', None), ],
            'beak':     [('mouth', None), ('face', None)],
            'shrimp':   [('', None), ],
            'kraken':   [('', None), ],
            'mollusk':  [('', None), ],
            'squid':    [('kidding', 'squidding'), ],
            }

    # TODO: Allow choosing pun list on object creation
    def __init__(self):
        self.puns = self.squid

    def select_pun(self, string):
        '''Choose the best available pun.'''

        # Clean unwanted punctuation.
        string = string.strip('''.,;:?!/'" ''').lower()

        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = ('', 0)

        # Compare each pun option; better puns replace earlier options.
        for pun in self.puns:
            # Check to see if there is a defined replacement in the
            # pun dictionary.
            for word, replace in self.puns[pun]:
                if string == word:
                    if replace is None:
                        return pun, 1
                    else:
                        return pun, replace
            current_ratio = leven.ratio(pun, string)
            if current_ratio > best_pun[1]:
                best_pun = pun, current_ratio

        # Return both the pun itself, and the ratio so that
        # generate_pun() can find the best pun for a phrase.
        return best_pun

    def generate_pun(self, string):
        '''Given a phrase, replace the best pun possibility.'''
        # TODO: Multiple puns per line

        self.string = string.strip()

        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = ('', 0)

        # Find the best word to use and it's corresponding best pun.
        for word in self.string.split():
            new_pun = self.select_pun(word)
            # Check if select_pun returned a defined replacement
            # word instead of the usual Levenshtein ratio.
            if str(new_pun[1]).isalpha():
                best_pun = new_pun
                to_replace = word
                break
            if new_pun[1] > best_pun[1]:
                best_pun = new_pun
                to_replace = word

        # Use a defined replacement word if available, otherwise
        # just use the dictionary keyword.
        if str(best_pun[1]).isalpha():
            pun = self.string.replace(to_replace, best_pun[1])
        else:
            pun = self.string.replace(to_replace, best_pun[0])
        return pun.capitalize()

    def add_pun(self, string):
        '''Add a new pun to the list of available puns.'''

        # Add a new pun to the dictionary.
        # TODO: Add corresponding words as well
        self.puns[string] = ('', None)

# TODO: Add command line stuff and any exceptions down here

# vim: set ts=4 sts=4 sw=4 et:
