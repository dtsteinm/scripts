#!/usr/bin/env python2

import os


# media_list Python module
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 18, 2013


"""Explanation here."""

def tryconvert(episode):
    """Explanation here."""
    try:
        return int(re.findall('([0-9]+)',re.sub('([0-9]|[A-Z]){8}','X',episode[::-1], 1)[::-1])[0])
    except IndexError:
        return 9999

def list(files):
    """Explanation here."""
    for base, paths, files in os.walk(os.getcwd()):
        sorted(files, key=lambda number: tryconvert(number))

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
