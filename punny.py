#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: April 19, 2013

'''Generate puns for a given phrase.'''
from difflib import SequenceMatcher as seqmatch
from string import punctuation as punc
from re import sub

__all__ = ['PunGenerator']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.4.4'
__license__ = 'WTFPL'


class PunGenerator:
    '''Generate the puns.'''

    # TODO: Add other pun dictionaries
    # TODO: Add automatic words for other puns
    squid = {
            'ink':          [('going', 'goink'),
                             ('invade', 'inkvade'),
                             ('thinking', 'inking')],
            'fin':          [('even', 'efin'), ],
            'sea':          [(None, None), ],
            'gill':         [(None, None), ],
            'kelp':         [('hell', None),
                             ('heck', None), ],
            'keel':         [(None, None), ],
            'beak':         [('mouth', None),
                             ('face', None), ],
            'pier':         [(None, None), ],
            'tide':         [(None, None), ],
            'squid':        [('kidding', 'squidding'), ],
            'shore':        [('sure', None), ],
            'shell':        [(None, None), ],
            'coast':        [(None, None), ],
            'shrimp':       [('runt', None), ],
            'kraken':       [(None, None), ],
            'mollusk':      [('smallest', 'smollusk'), ],
            'tentacle':     [('hand', None), ],
            'tentacles':    [('hands', None), ],
            }

    # TODO: Allow choosing pun list on object creation
    def __init__(self):
        self.puns = self.squid

    def select_pun(self, string):
        '''Choose the best available pun.

        >>> p = PunGenerator()
        >>> p.select_pun('think')
        ('ink', 0.75)
        >>> p.select_pun('think?')
        ('ink?', 0.75)
        >>> p.select_pun('going')
        ('ink', 'goink')
        >>> p.select_pun('going?')
        ('ink?', 'goink?')
        >>> p.select_pun('hell')
        ('kelp', 1)
        >>> p.select_pun('hell?')
        ('kelp?', 1)
        '''

        # Save punctuation marks found in string.
        mark = [x for x in list(punc) if x in string]
        # Clean unwanted punctuation, assuming all punctuation was at
        # the end of the string.
        # FIXME: Will likely break on words like "can't"
        string = string[:(-len(mark) if len(mark) != 0 else None)]

        # Store the currently best pun option, and it's Levenshtein
        # ratio (0-1) in a tuple to compare it to later options.
        best_pun = (None, None)

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
            # Calculate a diff on two strings, without considering
            # anything as junk, and return the ratio.
            current_ratio = seqmatch(None, pun, string).ratio()
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
        best_pun = (None, None)

        # Find the best word to use and it's corresponding best pun.
        for word in self.string.split():
            new_pun = self.select_pun(word)
            # Check if select_pun returned a defined replacement
            # word instead of the usual Levenshtein ratio.
            # Because a specified replacement word (new_pun[1]) can
            # contain punctuation, this test could fail when we want
            # it to pass when checking the full string.
            if str(new_pun[1])[0].isalpha():
                best_pun = new_pun
                to_replace = word
                break
            if new_pun[1] > best_pun[1]:
                best_pun = new_pun
                to_replace = word

        # In order to avoid matching partial words, we're going to
        # specify the beginning and end of the string to match.
        to_replace = to_replace.join((r'\b',) * 2)

        # Use a defined replacement word if available, otherwise
        # just use the dictionary keyword.
        # NOTE: Because a specified replacement word (best_pun[1])
        # can contain punctuation, this test could fail when we want
        # it to pass when checking the full string.
        if str(best_pun[1])[0].isalpha():
            pun = sub(to_replace, best_pun[1], self.string)
        else:
            pun = sub(to_replace, best_pun[0], self.string)
        return pun.capitalize()

    def add_pun(self, pun, word=None, replace=None):
        '''Add a new pun to the list of available puns.'''

        # Add a new pun to the dictionary.
        if pun in self.puns:
            self.puns[pun] += [(word, replace)]
            for i, t in enumerate(self.puns[pun]):
                if self.puns[pun][i] == (None, None):
                    del self.puns[pun][i]
        else:
            self.puns[pun] = [(word, replace)]

    # TODO: PrettyPrint-ing of puns
    def print_puns(self):
        '''Display the current pun dictionary, in a prettily formatted ''' \
                '''manner.'''
        pass

    # TODO: write dump/load/update
    def dump(self, filename):
        '''Save the current pun dictionary to the specified file.'''
        pass

    def load(self, filename):
        '''Load a pun dictionary from the specified pickle file.'''
        # Overwrite or add new values?
        pass

    def update(self, filename):
        '''Update the current pun dictionary with values from the '''\
                '''specified pickle file.'''
        pass


# TODO: Add command line stuff and any exceptions down here
class Error(Exception):
    '''Base exception for the punny module.'''
    pass


if __name__ == '__main__':
    import sys
    print PunGenerator().generate_pun(''.join(sys.argv[1:]))

# vim: set ts=4 sts=4 sw=4 et tw=79:
