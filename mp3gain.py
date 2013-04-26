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
from math import floor
import subprocess as sp
import tempfile as temp

__all__ = ['walk', 'mp3gain']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.9.4'
__license__ = 'WTFPL'


# walk looks for directories containing mp3 files,
# and calls mp3gain() when we have something to do.
# TODO: Add messages displaying progress of entire file structure.
# TODO: Add vorbisgain and aacgain support, look at python-rgain
def walk(start_dir=os.getcwd(), **kwargs):
    """Traverses the filesystem structure, looking for directories """ \
            """containing MP3 files, and calls mp3gain() when appropriate.

    Attributes:
        start_dir -- root directory to begin looking in
        force -- force recalculation on all files
        skip -- skip ReplayGain calculation for files with existing tags
        clear -- delete ReplayGain tags

    Example: mp3gain.walk('/path/to/Music')
    """

    # Clean up supplied directory (whitespace, trailing /).
    start_dir = start_dir.strip()
    start_dir = start_dir.rstrip(os.sep)

    # Get kwargs, using defaults if not specified.
    # TODO: Additional options
    force = kwargs.pop('force', False)
    skip = kwargs.pop('skip', False)
    clear = kwargs.pop('clear', False)

    # Create a dictionary of options to override mp3gain()'s defaults.
    options = {}
    if force:
        options['recalc'] = True
    if skip:
        options['skip'] = True
    if clear:
        options['delete'] = True

    # Flag to indicate work was done.
    flag = False

    # TODO: Allow user to break out of entire program, like <C-c><C-c>
    try:
        # Check to see if the mp3gain utility is installed.
        if sp.call('/usr/bin/mp3gain -v', shell=True,
                stderr=sp.STDOUT, stdout=sp.PIPE) is 127:
            raise NoExecutableError()

        # Check to make sure we're working in a real directory.
        if os.path.isdir(start_dir) is False:
            raise DirectoryError(start_dir)

        # Anonymous function to check for dotfiles
        dot_check = lambda name: name.startswith('.')

        # Need to get a count of how many directories we're traveling.
        # We also have to count which directory we are in.
        total = 0
        count = 0

        # Let's make an initial directory count of the files
        # Pre-emptive walk gathering the numbers of directories
        # (info[1] is equivalent to pathnames in the next for loop).
        for info in os.walk(start_dir):
            total += len(info[1])
        # We need this as a float, otherwise the math will be off.
        total = float(total)

        # Iterate filesystem structure, checking each list of files contained
        # in each directory for anything that resembles an MP3 file.
        for basedir, pathnames, files in os.walk(start_dir):

            # Better safe than sorry: let's verify it's a real directory.
            # And since it was skipped, we can forget about it.
            if os.path.isdir(basedir) is False:
                total -= 1
                raise DirectoryError(basedir)

            # Skip hidden directories (dotfiles)
            # Same as above with hidden files.
            for pathname in pathnames:
                if dot_check(pathname):
                    total -= 1
                    pathnames.remove(pathname)

            # We need to check each file in the current basedir,
            # as the first file_ in our list may not be an MP3.
            for file_ in files:
                try:

                    # Skip to next file_ on hidden files
                    if dot_check(file_):
                        continue

                    # Call mp3gain when we hit a directory containing MP3s.
                    # Passes options as expanded dictionary mapping.
                    # TODO: Look into mutli-threading to speed up this process.
                    if '.mp3' == os.path.splitext(file_)[1]:
                        mp3gain(basedir, **options)
                        # Raise our flag
                        flag = True
                        # This directory is done, so we can go to the next one.
                        break

                # If we looked at a non-existent directory (deleted while
                # running?), just go on to the next one on our walk
                except DirectoryError:
                    pass
                finally:
                    # The directories add up.
                    count += 1
                    print_progress(count, total)

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

    # User hit Ctrl-C outside of

    # Any other errors encountered were too much for us to handle.
    except:
        print '\nSomething went horribly wrong on our walk!'
        raise

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
        # print total, count

    # End of outer isdir() try...except block
# End of walk() function


# mp3gain is where we do our actual work.
def mp3gain(directory=os.getcwd(), **kwargs):
    """Attach IDv3 ReplayGain tags for the MP3 files in """ \
            """the specified directory.

    Example: mp3gain.mp3gain('/path/to/Music/Artist/Album')

    Attributes:
      directory -- Directory on which to apply ReplayGain
      allowclip -- Ignore warnings about track clipping (False)
      noclip -- Automatically lower gain to avoid clipping (True)
      recalc -- Force re-calculation of ReplayGain tags (False)
      delete -- Delete current ReplayGain tags (False)
      skip -- Do not read/write ReplayGain tags (False)
      preserve -- Preserve timestamps on current file (True)
    """

    # Assign attributes from kwargs, applying a default value as needed.
    # TODO: Look into other possible options, like 'undo'
    # TODO: User may prefer APE over ID3v2, for whatever reason
    allowclip = kwargs.pop('noclip', False)
    noclip = kwargs.pop('noclip', True)
    recalc = kwargs.pop('recalc', False)
    delete = kwargs.pop('delete', False)
    skip = kwargs.pop('skip', False)
    preserve = kwargs.pop('preserve', True)

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
        # Ignore or lower gain if clipping warning
        if allowclip:
            command += '-c '
        if noclip:
            command += '-k '
        # Preserve access/creation/modified times from file
        if preserve:
            command += '-p '
        command += '*.mp3'

        # TODO: os.path.abspath/normpath
        dirbase = os.path.basename(directory)

        # Display message when we start a directory
        # print 'Starting:', dirbase,
        # Flush stdout in order to force Python to print the previous
        # line with a trailing comma/no newline; otherwise, it waits
        # for the rest of the line, which, is usually a return.
        # sys.stdout.flush()

        # mp3gain can produce a lot of output, and sp.PIPE only takes
        # about 65kb of data before it shuts down. This TemporaryFile
        # object should take as much data as we can through at it,
        # and discard it on close.
        tmp = temp.TemporaryFile()

        # Create a subprocess, and call the command inside of a shell.
        proc = sp.Popen(command, cwd=directory, shell=True,
                stderr=sp.STDOUT, stdout=tmp)
        proc.wait()

        # 127 is the specific return code from the Linux shell
        # to indicate the command was not found.
        if proc.poll() is 127:
            raise NoExecutableError()
        # Return code of 1 indicates no files were processed.
        # TODO: Check for mpeg layer I files
        if proc.poll() is 1:
            raise NoMP3Error(directory)
        # If /usr/bin/mp3gain returned something other
        # than a 0, something went wrong with the process.
        elif proc.poll() is not 0:
            raise ProcessingError(directory)

    # Raised when  directory does not contain any MP3s.
    except NoMP3Error as e:
        print '\r{} did not contain any MP3s.'.format(e)
    # Raised when the sp.Popen() does not execute successfully.
    except ProcessingError as e:
        print '\rThere was an error processing {}.'.format(e)
    # Since this can be called by itself, let's also
    # raise directory errors right here, too.
    except DirectoryError as e:
        print '\r{} is not a real directory.'.format(e)

    # Catch KeyboardInterrupts as a cue to cancel processing the current dir.
    except KeyboardInterrupt:
        print '\rSkipping: {}'.format(dirbase)

    # TODO: Has to be some way to suppress this output when mp3gain()
    # is not called from walk().
    except NoExecutableError:
        raise

    # Any other errors are not expected.
    except:
        print '\nSomething went horribly wrong processing our files!'

    # Everything went according to plan.
    else:
        pass
        # print '\rFinished with:', dirbase,

    # Close our temporary file as we leave the try block.
    finally:
        tmp.close()

    # End of isdir()|Popen() try...except block
# End of mp3gain() function


def print_progress(current, total, length=50):
    '''Prints a simple progress bar indicating progress.'''
    # TODO: Add a doctest

    # Calculates what percentage of work has been finished.
    ratio = (current / total)

    # Determines how long the line must be to represent work done.
    # Subract one for our greater than symbol.
    size = int(floor(ratio * length)) - 1

    # Prints our bar and a percentage of progress.
    # The trailing null string and comma ensures a new line is not printed.
    print '\r{0:000.2f}% |{1}|'.format(ratio * 100, '=' * size +
            '>' + ('-' * (length - size))) + '',

# End of print_progress function

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


class NoMP3Error(Error):
    """Exception raised while attempting to process a directory """ \
            """containing no MP3 files.

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

    # TODO: Add other options
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

# vim: set ts=4 sts=4 sw=4 et tw=79:
