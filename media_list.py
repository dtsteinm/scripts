#!/usr/bin/env python2

import os
import re


# media_list Python module
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 26, 2013


"""Module with functions to simplify the sorting of media files with """\
        """complex filenames, and create playlist files for playback."""

# NOTE: Consider writing this OO with class (might be too late for that)
#       Map out functions to ensure flow is logical
#class MediaList():
#    def __init__(self, start_dir=os.getcwd()):
#        self.start_dir = start_dir


# TODO: Accept multiple values for playlist type.
def makeplaylist(start_dir=os.getcwd(), playlist_type='pls'):
    """Create media playlist(s) for specified directory and playlist """\
            """type.

    Attributes:
        start_dir -- directory from which to start; if None, prompt user?
        playlist_type -- type of playlist to create; 'pls' and/or 'm3u'
    """

    # Clean up user input
    start_dir = start_dir.strip()

    # TODO: Verify start_dir exists (start a try...except block)
    if os.path.isdir(start_dir) is False:
        pass

    # Flags for what kind of playlist file to create.
    # These variables must exist for later execution, so declare
    # them as false for now.
    PLS = False
    M3U = False

    # FIXME: There _has_ to be a better way to do this.
    # Check to see if playlist_type was passed as a string or list
    # and set the appropriate flag in either case. Also clean up input.
    if type(playlist_type) is str:
        playlist_type.strip()
        if playlist_type is 'pls':
            PLS = True
        if playlist_type is 'm3u':
            M3U = True
    elif type(playlist_type) is list:
        for type_ in playlist_type:
            type_.strip()
            if type_ is 'pls':
                PLS = True
            if type_ is 'm3u':
                M3U = True
    # Default to a PLS file if no valid filetype was specified.
    else:
        PLS = True

    # Anonymous function to check for dotfiles
    dot_check = lambda name: re.match(r'^\..*$', name)

    # List of known media file extensions for later use.
    media_exts = ['mkv', 'avi', 'wmv', 'mp4', 'mp3', 'flac', 'ogg']

    # TODO: Throw this in a try...except
    # Start in startdir, and create a pls and/or m3u playlist
    # file for directories containing valid media files. Send the
    # current basedir and the list returned from sortedfiles()
    # for the creation of playlist files with absolute paths.
    for basedir, pathnames, files in os.walk(start_dir):
        # Skip hidden directories (pathnames) and files in current basedir
        for pathname in pathnames:
            if dot_check(pathname):
                pathnames.remove(pathname)
            for file_ in files:
                if dot_check(file_):
                    files.remove(file_)
        # TODO: throw some checking in here to only make a playlist
        #       if basedir contains media files (mkv, avi, mp3, etc.)
        if PLS:
            mkpls([basedir, sortfiles(files)])
        if M3U:
            mkm3u([basedir, sortfiles(files)])


# FIXME: Write mkpls function
def mkpls(file_list):
    """Creates a PLS format playlist file from a base directory and a """\
            """list of filenames.

    Attributes:
        file_list -- tuple containing base directory and sorted list of files
    """

    print 'making pls'
    print file_list
    pass


# FIXME: Write mkm3u function
def mkm3u(file_list):
    """Creates a M3U format playlist file from a base directory and a """\
            """list of filenames.

    Attributes:
        file_list -- tuple containg base directory and sorted list of files
    """

    print 'making m3u'
    print file_list
    pass


# TODO: Make it easier to get a list from sortfiles (?)
def sortfiles(files):
    """Returns sorted list of files in passed directory.

    Attributes:
        files -- unsorted list of filenames
    >>> sortfiles(['Another_Testfile_No._23_[CRC32CRC].ext',"""\
            """'Testfile_No._22_[CRC32CRC].ext'])
    ['Testfile_No._22_[CRC32CRC].ext', """\
            """'Another_Testfile_No._23_[CRC32CRC].ext']
    """

    return sorted(files, key=lambda number: getseqnum(number))


def getseqnum(filename):
    """Extracts a sequence number from a complex filename, ignoring """\
            """CRC checksums, and returns result as an integer.

    Attributes:
        filename -- Filename from which sequence is to be extracted

    Examples:
    >>> getseqnum('Testfile_No._22_[CRC32CRC].ext')
    22
    >>> getseqnum('Another_Testfile_No._23_[CRC32CRC].ext')
    23
    """

    # If filename does not contain a non-CRC number, re.findall(...)[0]
    # will throw an IndexError exception for the empty list produced.
    # TODO: Optional user-specified sorting, maybe?
    try:

        # Finds and returns (as an integer) a sequence number from
        # a complex filename. NOTE: May not work with all formats.
        # NOTE: This can probably be cleaned up for readability.
        # Explanation:
        # - filename[::-1]: reverse the string; essentially starts
        #                     re.sub from last character
        # - re.sub(..., 1)[::-1]: replace CRC32s with a single 'X'
        #                         and unreverse string
        # - int.findall(...)[0]: find all occurrences of one or more
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
# TODO: Clean this up to better conform to standard Exceptions.
#       Also, fix try...excepts to match same conventions.
class Error(Exception):
    """Base class for exceptions caused by methods in """ \
            """the media_list module.
    """
    pass


class DirectoryError(Error):
    """Exception raised for errors relating to directory """ \
            """existence.

    Attributes:
        dir_ -- directory which caused the error
    """

    def __init__(self, dir_):
        Exception.__init__(self)
        self.dir_ = dir_
        # print '\nException: DirError:'
        # print 'Directory does not exist:', self.dir_

    def __str__(self):
        return repr(self.dir_)


class PlaylistExistsError(Error):
    """Exception raised for errors relating to file """ \
            """existence.

    Attributes:
        file_ -- directory which caused the error
    """

    def __init__(self, file_):
        Exception.__init__(self)
        self.file_ = file_
        # print '\nException: FileError:'
        # print 'File does not exist:', self.file_

    def __str__(self):
        return repr(self.file_)


__all__ = ['makeplaylist', 'findfiles', 'sortfiles',
           'getseqnum', 'mkpls', 'mkm3u']
__version__ = '0.07'

# If we were called from command line...
if __name__ == "__main__":
    import os
    import re
    import sys

    # TODO: Put in some usage message on bad arg list.
    # User can get to work right away number of arguments.
    if len(sys.argv) == 3:
        makeplaylist(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 2:
        makeplaylist(sys.argv[1])
    # Otherwise, start walking from current working directory.
    else:
        makeplaylist()

# vim: set ts=4 sts=4 sw=4 et:
