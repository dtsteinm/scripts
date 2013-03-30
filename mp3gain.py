#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 28, 2013

"""Recursively tag MP3 files with ReplayGain attributes """ \
        """using the mp3gain utility."""
import os
import re
import sys
import subprocess

__all__ = ['walk', 'mp3gain']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.7.3'
__license__ = 'WTFPL'


# walk looks for directories containing mp3 files,
# and calls mp3gain() when we have something to do.
# TODO: Add messages displaying progress of entire file structure.
# TODO: Allow settings to be passed to mp3gain(); possibly 'force' and 'skip'?
def walk(start_dir=os.getcwd()):
    """Traverses the filesystem structure, looking for directories """ \
            """containing MP3 files, and calls mp3gain() when appropriate.

    Example: mp3gain.walk('/path/to/Music')
    """

    # Clean up supplied directory (whitespace, trailing /).
    start_dir = start_dir.strip()
    if start_dir[-1] is os.sep:
        start_dir = start_dir[:-1]

    # Flag to indicate work was done.
    flag = False

    try:
        # Check to see if the mp3gain utility is installed.
        if subprocess.call('/usr/bin/mp3gain -v', shell=True,
                stderr=subprocess.STDOUT, stdout=subprocess.PIPE) is 127:
            raise NoExecutableError()

        # Check to make sure we're working in a real directory.
        if os.path.isdir(start_dir) is False:
            raise DirectoryError(start_dir)

        # Anonymous function to check for dotfiles
        dot_check = lambda name: re.match(r'^\..*$', name)

        # Iterate filesystem structure, checking each list of files contained
        # in each directory for anything that resembles an MP3 file.
        for basedir, pathnames, files in os.walk(start_dir):

            # Better safe than sorry: let's verify it's a real directory.
            if os.path.isdir(basedir) is False:
                raise DirectoryError(basedir)

            # Skip hidden directories (dotfiles)
            for pathname in pathnames:
                if dot_check(pathname):
                    pathnames.remove(pathname)

            # We need to check each file in the current basedir,
            # as the first file_ in our list may not be an MP3.
            for file_ in files:
                try:

                    # Skip to next file_ on hidden files
                    if dot_check(file_):
                        continue

                    # Call mp3gain when we hit a directory containing MP3s.
                    # TODO: Look into mutli-threading to speed up this process.
                    if re.match(r'^.*\.mp3$', file_) is not None:
                        mp3gain(basedir)
                        # Raise our flag
                        flag = True
                        # This directory is done, so we can go to the next one.
                        break

                # If we looked at a non-existent directory (deleted while
                # running?), just go on to the next one on our walk
                except DirectoryError:
                    pass

                # End of inner isdir() try...except
            # End of files loop
        # End of os.walk() loop

    # Quit on DirectoryError not caught inside for loop.
    # Initial directory doesn't exist, so there's nothing to do.
    except DirectoryError as e:
        print '{} is not a real directory.'.format(e)

    # If mp3gain is not installed where we expected it, nothing to do.
    except NoExecutableError:
        print 'Quitting...'

    # Any other errors encountered were too much for us to handle.
    except:
        print '\nSomething went horribly wrong on our walk!'

    # Made it out of the for loop with no additional errors.
    else:
        # Print a message indicating whether or not files had been processed.
        if flag is True:
            print '\nFinished processing files!'
        else:
            print '\nNo files to process!'

    # Generic completion block for messages like '...done!' after
    # try block has finished. (currently empty)
    finally:
        pass

    # End of outer isdir() try...except block
# End of walk() function


# mp3gain is where we do our actual work.
def mp3gain(directory=os.getcwd(), recalc=False, delete=False,
        skip=False, preserve=True):
    """Attach IDv3 ReplayGain tags for the MP3 files in """ \
            """the specified directory.

    Example: mp3gain.mp3gain('/path/to/Music/Artist/Album')

    Attributes:
      directory -- Directory on which to apply ReplayGain
      recalc -- Force re-calculation of ReplayGain tags (False)
      delete -- Delete current ReplayGain tags (False)
      skip -- Do not read/write ReplayGain tags (False)
      preserve -- Preserve timestamps on current file (True)
    """

    try:
        # Check to make sure we're working in a real directory.
        if os.path.isdir(directory) is False:
            raise DirectoryError(directory)

        # Set our command and options to use here.
        # Make changes to IDv3 tags only
        command = '/usr/bin/mp3gain -s i '
        # Recalculate ReplayGain, regardless of current RG tags
        if recalc:
            command += '-s r '
        # Delete current ReplayGain tags from file
        if delete:
            command += '-s d '
        # Skip reading/writing of ReplayGain tags
        if skip:
            command += '-s s '
        # Preserve access/creation/modified times from file
        if preserve:
            command += '-p '
        command += '*.mp3'

        # Display message when we start a directory
        print 'Starting:', directory,
        # Flush stdout in order to force Python to print the previous
        # line with a trailing comma/no newline; otherwise, it waits
        # for the rest of the line, which, is usually a return.
        sys.stdout.flush()

        # Create a subprocess, and call the command inside of a shell.
        proc = subprocess.Popen(command, cwd=directory, shell=True,
                stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        proc.wait()

        # 127 is the specific return code from the Linux shell
        # to indicate the command was not found.
        if proc.poll() is 127:
            raise NoExecutableError()
        # If /usr/bin/mp3gain returned something other
        # than a 0, something went wrong with the process.
        elif proc.poll() is not 0:
            raise ProcessingError(directory)

    # Raised when the subprocess.Popen() does not execute
    # successfully (i.e. directory does not contain any MP3s).
    # Since this can be called by itself, let's also
    # raise directory errors right here, too.
    except ProcessingError as e:
        print '\rThere was an error processing {}.'.format(e)
    except DirectoryError as e:
        print '\r{} is not a real directory.'.format(e)

    # Catch KeyboardInterrupts as a cue to cancel processing the current dir.
    except KeyboardInterrupt:
        print '\rSkipping: {}'.format(directory)

    # TODO: Has to be some way to suppress this output when mp3gain()
    # is not called from walk().
    except NoExecutableError:
        raise

    # Any other errors are not expected.
    except:
        print '\nSomething went horribly wrong processing our files!'

    # Everything went according to plan.
    else:
        print '\rFinished with:', directory

    # End of isdir()|Popen() try...except block
# End of mp3gain() function

# End of module logic


# Begin customized module Exceptions.
class Error(Exception):
    """Base class for exceptions caused by methods in the mp3gain module.
    """
    pass


class DirectoryError(Error):
    """Exception raised for errors relating to directory existence.

    Attributes:
        dir_ -- directory which caused the error
    """

    def __init__(self, dir_):
        Exception.__init__(self)
        self.dir_ = dir_

    def __str__(self):
        return repr(self.dir_)


class ProcessingError(Error):
    """Exception raised while attempting to process files """ \
            """with the mp3gain utility.

    Attributes:
        dir_ -- directory in which the error occured
    """

    def __init__(self, dir_):
        Exception.__init__(self)
        self.dir_ = dir_

    def __str__(self):
        return repr(self.dir_)


class NoExecutableError(Error):
    """Exception raised when mp3gain utility is not installed on system.

    Attributes:
    """

    def __init__(self):
        print '\nException: NoExecutableError:'
        print 'The mp3gain utility is not installed on this system.'

# End of customized module Exceptions.

# If we were called from command line...
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Applies ReplayGain \
            tags to MP3 files, normalizing volume")
    parser.add_argument('directory', nargs='?',
            help='directory to begin searching')
    parser.add_argument('-v', '--version', action='version',
            version='%(prog)s ' + __version__)
    args = parser.parse_args()

    if args.directory is not None:
        walk(args.directory)
    else:
        walk()

# vim: set ts=4 sts=4 sw=4 et:
