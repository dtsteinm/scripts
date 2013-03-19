#!/usr/bin/env python2

import os
import subprocess
import re

# mp3gain Python module
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 5, 2013

""" Recursively tag MP3 files with ReplayGain attributes """ \
        """using the mp3gain utility."""


# walk looks for directories containing mp3 files,
# and calls mp3gain() when we have something to do.
# TODO: Add messages displaying progress of entire file structure.
def walk(start_dir):
    """Traverses the filesystem structure, looking for """ \
            """directories containing MP3 files, and """ \
            """calls mp3gain() when appropriate.

    Example: mp3gain.walk('/path/to/Music')
    """

    # Clean up supplied directory (whitespace, trailing /).
    start_dir = start_dir.strip()
    if start_dir[-1] is os.sep:
        start_dir = start_dir[:-1]

    # Since this can run for a while, let's make a private
    # copy of our starting directory variable.
    __start_dir = start_dir

    # Flag to indicate work was done.
    __flag = False

    try:
        # Check to see if the mp3gain utility is installed.
        if os.system('mp3gain -v') is not 0:
            raise ExecError()
        # Check to make sure we're working in a real directory.
        if os.path.isdir(__start_dir) is False:
            raise DirError(__start_dir)

        # Iterate filesystem structure, checking each
        # list of files contained in each directory
        # for anything that resembles an MP3 file.
        for __basedir, __pathnames, __files in os.walk(__start_dir):
            for __file_ in __files:
                try:
                    # Better safe than sorry: let's verify
                    # is a real directory (it should be)
                    if os.path.isdir(__basedir) is False:
                        raise DirError(__basedir)
                    # Call mp3gain when we hit a
                    # directory containing MP3s.
                    if re.match('^.*mp3$', __file_) is not None:
                        mp3gain(__basedir)
                        # Raise our flag
                        __flag = True
                        # Keep walking...
                        continue
                # If we looked at a non-existent directory
                # (deleted while running?), just go on to
                # the next one on our walk
                except DirError:
                    pass
                # End of inner isdir() try...except
            # End of __files loop
        # End of os.walk() loop
    # Quit on DirError not caught inside for loop.
    # Initial directory doesn't exist, so there's nothing to do.
    except (DirError, ExecError):
        return 1
    # Unexpected error; let's find out what it is.
    except:
        print '\nSomething went horribly wrong on our walk!'
        raise
    # Made it out of the for loop with no additional errors.
    else:
        # Print a message indicating whether
        # or not files had been processed.
        if __flag is True:
            print '\nFinished processing files!'
        else:
            print '\nNo files to process!'
    # Generic completion block for messages like
    # '...done!' after try block has finished.
    # (currently empty)
    finally:
        pass
    # End of outer isdir() try...except block
# End of walk() function


# mp3gain is where we do our actual work.
# TODO: Add messages for progress on a directory.
def mp3gain(directory):
    """Attach IDv3 ReplayGain tags for the MP3 files in """ \
            """the specified directory.

    Example: mp3gain.mp3gain('/path/to/Music/Artist/Album')
    """

    try:
        # Check to make sure we're working in a real directory.
        if os.path.isdir(directory) is False:
            raise DirError(directory)

        # Create a subprocess, and call the command
        # inside of a shell. Command will: Calculate
        # ReplayGain if tag does not exist, and insert
        # it into music file as an IDv3 tag (and update
        # any APEv2 ReplayGain tags to IDv3 tags),
        # preserving original files' ctime, etc.
        # TODO: Really want to see if this changes files
        # NOTE: Use subprocess.check_output() instead of .call()
        proc = subprocess.call(['/usr/bin/mp3gain -s i -p ',
            directory, '/*.mp3'], shell=True)
        # If /usr/bin/mp3gain returned something other
        # than a 0, something went wrong with the process.
        # TODO: Currently, mp3gain seems to _always_
        #       return a zero on exit; I need to use
        #       something along the lines of Popen
        #       and parse the output to display any
        #       meaningful messages to the user.
        if proc is not 0:
            raise ProcError(directory)
        print 'Finished with:', directory
    # Raised when the subprocess.call() does not execute
    # successfully (i.e. directory does not contain any MP3s).
    # Since this can be called by itself, let's also
    # raise directory errors right here, too.
    except (ProcError, DirError):
        # Return a non-zero result to indicate failure.
        return 1
    # Unexpected error, raise it for details.
    except:
        print '\nSomething went horribly wrong processing our files!'
        raise
    # End of isdir()|call() try...except block
# End of mp3gain() function

# End of module logic


# Begin customized module Exceptions.
# TODO: Clean this up to better conform to standard Excetions.
#       Also, fix try...excepts to match same conventions.
class Error(Exception):
    """Base class for exceptions caused by methods in """ \
            """the mp3gain module."""
    pass


class DirError(Error):
    """Exception raised for errors relating to directory """ \
            """existence.

    Attributes:
        dir_ -- directory which caused the error
    """

    def __init__(self, dir_):
        self.dir_ = dir_
        print '\nException: DirError:'
        print 'Directory does not exist:', self.dir_

    def __str__(self):
        return repr(self.dir_)


class ProcError(Error):
    """Exception raised while attempting to process files """ \
            """with the mp3gain utility.

    Attributes:
        dir_ -- directory in which the error occured
    """

    def __init__(self, dir_):
        self.dir_ = dir_
        print '\nException: ProcError:'
        print 'There was an error while processing:'
        print self.dir_

    def __str__(self):
        return repr(self.dir_)


class ExecError(Error):
    """Exception raised when mp3gain utility is not installed on system.

    Attributes:
    """

    def __init__(self):
        print '\nException: ExecError:'
        print 'The mp3gain utility is not installed on this system.'

# End of customized module Exceptions.

# What do we want to import using 'from mp3gain import *'
__all__ = ['walk', 'mp3gain']
__version__ = '0.2'

# If we were called from command line...
if __name__ == "__main__":
    import sys
    import os

    # TODO: Put in some usage message on bad arg list.
    # User can get to work right away number of arguments.
    if len(sys.argv) == 2:
        walk(sys.argv[1])
    # Otherwise, start walking from current working directory.
    else:
        walk(os.getcwd())

# vim: set ts=4 sts=4 sw=4:
