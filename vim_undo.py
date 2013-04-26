#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 28, 2013

# TODO: Add function to refactor files

"""Detects unusable undo and view files in Vim directory; for """ \
        """example user has moved or deleted previously edited files."""
import os

__all__ = ['prune']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.4'
__license__ = 'WTFPL'


def prune(start_dir=os.path.join(os.getenv('HOME'), '.vim'), confirm=False):

    # TODO: Rewrite doctests to not output on system() calls.
    """Detects unusable undofiles in user's Vim undodir.

    Attributes:
        start_dir -- vim directory
        confirm -- confirm deletion of each file (Default: False)

    >>> os.system('dd if=/dev/zero of=' + os.getenv('HOME') + """ \
            """'/.vim/undo/test.vim bs=1024 count=1')
    0
    >>> os.system('dd if=/dev/zero of=' + os.getenv('HOME') + """ \
            """'/.vim/view/test.py bs=1024 count=2')
    0
    >>> prune()
    Cleared 3kb of disc space.
    ...Done!
    >>> prune()
    Cleared 0kb of disc space.
    ...Done!
    >>> prune('/foo/bar')
    '/foo/bar' is not a real directory.
    """

    # Outer try block
    try:
        # Check to see if provided or default directory exists.
        if not os.path.isdir(start_dir):
            # Throw custom exception if it does not.
            raise DirectoryError(start_dir)

        # Initialize total_size to store the amount of disk space
        # saved by deleting unusable vimfiles.
        total_size = 0

        # Traverse the file system starting with provided or default
        # directory, looking for unusable undo- and viewfiles.
        for basedir, pathnames, files in os.walk(start_dir):

            # We're only concerned with files located in undo- and viewdir.
            if os.path.basename(basedir) in ('undo', 'view'):

                # Check each file in current basedir for
                # references to non-existent vimfiles.
                for file_ in files:

                    # Undofiles are stored in the form '%path%to%file.ext'
                    # and can be directly translated to a form that Python
                    # can check by replacing all occurrences of '%' with
                    # os.sep, f.e. '/' on POSIX systems (NOTE: this test has
                    # not  been verified to work on Windows systems, and
                    # caution is advised as the results of this function
                    # may be irreversible).
                    if os.path.isfile(file_.replace('%', os.sep)) is True:
                        # file_ references an existing file,
                        # so skip to the next one.
                        continue

                    # Viewfiles are a bit more complicated, but not by much.
                    # These files are stored in the form of
                    # '~=+path=+to=+file.ext=' so are first task is to replace
                    # those '=+' with the appropriate separator for the OS,
                    # followed by stripping the trailing '=' from the end of
                    # the filename. Because os.path.isfile() cannot into user
                    # home directories, we'll expand that to the real path here
                    # for the sake of later simplicity (NOTE: Again, this has
                    # not been tested to work as expected on non-POSIX systems,
                    # and caution is advised).
                    elif os.path.isfile(os.path.expanduser(file_.replace('=+',
                        os.sep).strip('='))) is True:
                        # file_ references an existing file,
                        # so skip to the next one.
                        continue

                    # file_ does not reference an existing file,
                    # so let's try deleting it.
                    else:
                        total_size = _try_delete(basedir,
                                file_, total_size, confirm)

                    # End of file_ checking if-elif-else block.
                # End of files for loop.
            # End of 'undo'/'view' if block.
        # End of os.walk() for loop.

    # In the case of the start_dir being invalid...
    except DirectoryError as e:
        # ...catch fatal custom exception, and report it to the user.
        print "{} is not a real directory.".format(e)

    # Do nothing with any other uncaught exceptions.
    except:
        pass

    # If outer try block executed with no exceptions...
    else:
        # ...report the amount of disk space freed in kilobytes.
        print "Cleared {}kb of disc space.".format(total_size / 1024)
        print "...Done!"

    # At end of execution
    finally:
        pass

    # End of outer try block.
# End of prune function


def _try_delete(basedir, file_, total_size, confirm):
    '''Function that performs the actual deletion of files.

    Attributes:
        basedir -- directory in which file exists
        file_ -- filename
        total_size -- size of files deleted so far

    Returns:
        total_size -- total_size plus size of file_
    '''

    # Try block for deleting the current file_.
    try:

        # Append the current filename to the current
        # basedir, using the os.sep, to create an
        # absolute path to the file_,
        # f.e. '/home/user/.vim/undo/%path%to%file.ext'
        absolute_file = os.path.join(basedir, file_)

        # If the file was already removed by something
        # else, raise a FileError with the path.
        if not os.path.isfile(absolute_file):
            raise FileError(absolute_file)

        if confirm:
            if raw_input('Delete {}? [y/N]: '.format(file_)).lower()\
                    not in ['yes', 'yeah', 'yea', 'ye', 'y']:
                        return total_size

        # Add the size of the file to be deleted to the
        # size of the files that have already been removed.
        total_size += os.path.getsize(absolute_file)

        # Delete the vimfile from the filesystem.
        os.remove(absolute_file)

        # Pass the new total_size back to the prune block.
        return total_size

    # Catch the FileError, but don't do anything with it.
    except FileError:
        return total_size

    # End of try block for deleting the current file_
# End of _try_delete function

# End of logic


# Begin customized module Exceptions.
class Error(Exception):
    """Base class for exceptions caused by methods in """ \
            """the vim-undo module."""
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

    def __str__(self):
        return repr(self.dir_)


class FileError(Error):
    """Exception raised for errors relating to file """ \
            """existence.

    Attributes:
        file_ -- filename which caused the error
    """

    def __init__(self, file_):
        Exception.__init__(self)
        self.file_ = file_

    def __str__(self):
        return repr(self.file_)


# If we were called from command line...
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="deletes unusable \
            undo and view files in user's vim directory")
    parser.add_argument('directory', nargs='?', help="user's vim directory")
    parser.add_argument('-v', '--version', action='version',
            version='%(prog)s ' + __version__)
    args = parser.parse_args()

    if args.directory is not None:
        prune(args.directory)
    else:
        prune()

# vim: set ts=4 sts=4 sw=4 et tw=79:
