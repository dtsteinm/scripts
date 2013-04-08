#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: April 7, 2013

'''Generate puns for a given phrase.'''
import Levenshtein as leven

__all__ = ['PunGenerator']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.2.1'
__license__ = 'WTFPL'


class PunGenerator:
    '''Generate the puns.'''

    # TODO: Add other pun lists
    # TODO: Add automatic words for other puns
    squid = {
            'ink':      ['going', 'invade'],
            'fin':      ['', ],
            'gill':     ['', ],
            'kelp':     ['hell', 'heck'],
            'keel':     ['', ],
            'beak':     ['mouth', 'face'],
            'shrimp':   ['', ],
            'kraken':   ['', ],
            'mollusk':  ['', ]
            }

    # TODO: Allow choosing pun list on object creation
    def __init__(self):
        self.puns = self.squid

    def select_pun(self, string):
        '''Choose the best available pun.'''

        # Clean unwanted punctuation.
        string = string.strip('''.,;:?!/'"''')

        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = ('', 0)

        # Compare each pun option; better puns replace earlier options.
        for pun in self.puns:
            # Check to see if there is a defined replacement in the
            # pun dictionary.
            if string in self.puns[pun]:
                # TODO: If I'm able to implement a substring replacement,
                #       this 1 will guarantee that doesn't happen;
                #       might need to include desired ratio in dictionary,
                #       f.e. {'beak':('mouth',1),
                #             'ink':[('think',1),('invade',.5)]}
                #       No wonder I couldn't find a pun generator for squids
                return pun, 1
            current_ratio = leven.ratio(pun, string)
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
        best_pun = ('', 0)

        # Find the best word to use and it's corresponding best pun.
        for word in self.string.split():
            new_pun = self.select_pun(word)
            if new_pun[1] > best_pun[1]:
                best_pun = new_pun
                to_replace = word

        if best_pun[1] <= 0.5:
            pun = self.string.replace(to_replace, best_pun[0])
            # TODO: what we really want to do is sub-string replacements
            #       f.e. 'invade' -> 'ink-vade'
            # edit = leven.editops(best_pun[0], to_replace)
            # replace = leven.apply_edit(edit[:1], best_pun[0],
                    # to_replace)
            # pun = self.string.replace(to_replace, replace)
        else:
            pun = self.string.replace(to_replace, best_pun[0])
        return pun.capitalize()

    def add_pun(self, string):
        '''Add a new pun to the list of available puns.'''

        # Add a new pun to the dictionary.
        # TODO: Add corresponding words as well
        self.puns[string] = ''

# TODO: Add command line stuff and any exceptions down here

# vim: set ts=4 sts=4 sw=4 et:
