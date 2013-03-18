#!/usr/bin/env python2

import os


# media_list Python module
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 18, 2013


"""Explanation here."""
# TODO: Consider writing this OO with class


def make_playlist(start_dir=os.getcwd(), playlist_type='pls'):
    """Create media playlist(s) for specified directory and playlist"""\
            """type.
    
    Attributes:
        start_dir -- directory from which to start; if None, prompt user?
        playlist_type -- type of playlist to create; either 'pls' or 'm3u'
    """

def find_files(dir_=os.getcwd()):
    """Finds directories that contain media files from a given starting"""\
            """point, and tracks the lists.

    Attributes:
        dir_ -- directory in which to search for media files; cwd by default
    """
    pass


def mkpls(file_list):
    """Creates a PLS format playlist file from a list of filenames."""\

    """Attributes:
        file_list -- sorted list of files
    """
    pass


def mkm3u(file_list):
    """Creates a M3U format playlist file from a list of filenames."""\

    """Attributes:
        file_list -- sorted list of files
    """
    pass


# TODO: The looping sorting should probably be split up so that
#       we get a list for each directory that contains media files,
#       rather the the list from the final directory.
# FIXME: We also need to return the basedir associated with each list
#        in order to get absolute paths in the mkpls and mkm3u functions.
def sort_files(current_dir):
    """Returns sorted list of files in passed directory.

    Attributes:
        current_dir -- directory from which we should look for files
    """
    for basedir, pathnames, files in os.walk(current_dir):
        sorted_list = sorted(files, key=lambda number: tryconvert(number))
    return sorted_list


def tryconvert(filename):
    """Extracts a sequence number from a complex filename, ignoring"""\
            """CRC checksums, and returns result as an integer.

    Attributes:
        filename -- Filename from which sequence is to be extracted

    Examples:
    >>> tryconvert('Testfile_No._22_[CRC32CRC].ext')
    22
    """

    # If filename does not contain a non-CRC number, re.findall(...)[0]
    # will throw an IndexError exception for the empty list produced.
    # TODO: Optional user-specified sorting, maybe?
    try:

        # Finds and returns (as an integer) a sequence number from
        # a complex filename. NOTE: May not work with all formats.
        # Explanation:
        # - filename[::-1]: reverse the string; essentially starts
        #                     re.sub from last character
        # - re.sub(..., 1)[::-1]: replace CRC32s with a single 'X'
        #                         and un-reverse string
        # - int.findall(...)[0]: find all occurences of one or more
        #                        numbers, and reference only the first
        # - int(...): cast string from re.findall() to int; key in
        #             sorted() only takes an integer?
        return int(re.findall('([0-9]+)', re.sub('[0-9A-Fa-f]{8}',
            'X', filename[::-1], 1)[::-1])[0])

    # If the filename did not contain a sequence number, return
    # something unreasonably large to place it at the end of the
    # sorted list.
    except IndexError:
        return 9999


# Begin customized module Exceptions.
# TODO: Clean this up to better conform to standard Excetions.
#       Also, fix try...excepts to match same conventions.
class Error(Exception):
    """Base class for exceptions caused by methods in """ \
            """the media_list module."""
    pass


class DirError(Error):
    """Exception raised for errors relating to directory """ \
            """existence.

    Attributes:
        dir_ -- directory which caused the error
    """

    def __init__(self, dir_):
        self.dir_ = dir_
        # print '\nException: DirError:'
        # print 'Directory does not exist:', self.dir_

    def __str__(self):
        return repr(self.dir_)


class FileError(Error):
    """Exception raised for errors relating to file """ \
            """existence.

    Attributes:
        file_ -- directory which caused the error
    """

    def __init__(self, file_):
        self.file_ = file_
        # print '\nException: FileError:'
        # print 'File does not exist:', self.file_

    def __str__(self):
        return repr(self.file_)


__all__ = []
__version__ = '0.01'

# If we were called from command line...
if __name__ == "__main__":
    import sys
    import os

    # TODO: Put in some usage message on bad arg list.
    # User can get to work right away number of arguments.
    if len(sys.argv) == 2:
        #prune(sys.argv[1])
        pass
    # Otherwise, start walking from current working directory.
    else:
        #prune()
        pass

# vim: set ts=4 sts=4 sw=4:
