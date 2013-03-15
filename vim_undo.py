#!/usr/bin/env python

import os


# vim_undo Python module
# Written by Dylan Steinmetz <dtsteinm@gmail.com>
# Last updated: March 15, 2013


"""Detects unusable undofiles in Vim's undodir; for example""" \
        """user has moved or deleted previously edited files."""


def prune(__start_dir=os.path.join(os.getenv('HOME'), '.vim')):

    """Detects unusable undofiles in user's Vim undodir.

    >>> os.system('dd if=/dev/zero of=' + os.getenv('HOME') + """ \
            """'/.vim/undo/test.vim bs=1024 count=1')
    0
    >>> os.system('dd if=/dev/zero of=' + os.getenv('HOME') + """ \
            """'/.vim/view/test.py bs=1024 count=2')
    0
    >>> prune()
    Cleared 3kb of disc space.
    ...Done!
    >>> prune('/foo/bar')
    '/foo/bar' is not a real directory.
    ...Done!
    """

    # Outer try block
    try:
        # Check to see if provided or default directory exists.
        if not os.path.isdir(__start_dir):
            # Throw custom exception if it does not.
            raise DirError(__start_dir)

        # Initialize __total_size to store the amount of disk space
        # saved by deleting unusable vimfiles.
        __total_size = 0

        # Traverse the file system starting with provided or default
        # directory, looking for unusable undo- and viewfiles.
        for __basedir, __pathnames, __files in os.walk(__start_dir):

            # We're only concerned with files located in undo- and viewdir.
            if os.path.basename(__basedir) in ('undo', 'view'):

                # Check each file in current __basedir for
                # references to non-existant vimfiles.
                for __file in __files:

                    # Undofiles are stored in the form '%path%to%file.ext'
                    # and can be directly translated to a form that Python
                    # can check by replacing all occurences of '%' with
                    # os.sep, f.e. '/' on POSIX systems (NOTE: this test has
                    # not  been verified to work on Windows systems, and
                    # caution is advised as the results of this function
                    # may be irreversible).
                    if os.path.isfile(__file.replace('%', os.sep)) is True:
                        # __file references an existing file,
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
                    elif os.path.isfile(os.path.expanduser(__file.replace('=+',
                        os.sep).strip('='))) is True:
                        # __file references an existing file,
                        # so skip to the next one.
                        continue

                    # __file does not reference an existing file,
                    # so let's try deleting it.
                    else:

                        # Try block for deleting the current __file.
                        try:

                            # Append the current filename to the current
                            # __basedir, using the os.sep, to create an
                            # absolute path to the __file,
                            # f.e. '/home/user/.vim/undo/%path%to%file.ext'
                            __absolute_file = os.path.join(__basedir, __file)

                            # If the file was already removed by something
                            # else, raise a FileError with the path.
                            if not os.path.isfile(__absolute_file):
                                raise FileError(__absolute_file)

                            # Add the size of the file to be deleted to the
                            # size of the files that have already been removed.
                            __total_size += os.path.getsize(__absolute_file)

                            # Delete the vimfile from the filesystem.
                            os.remove(__absolute_file)

                        # Catch the FileError, but don't do anything with it.
                        except FileError:
                            pass

                        # End of try block for deleting the current __file.
                    # End of __file checking if-elif-else block.
                # End of __files for loop.
            # End of 'undo'/'view' if block.
        # End of os.walk() for loop.

    # In the case of the __start_dir being invalid...
    except DirError as e:
        # ...catch fatal custom exception, and report it to the user.
        print "{} is not a real directory.".format(e)

    # Do nothing with any other uncaught exceptions.
    except:
        pass

    # If outer try block executed with no exceptions...
    else:
        # ...report the amount of disk space freed in kilobytes.
        print "Cleared {}kb of disc space.".format(__total_size / 1024)

    # At end of execution, print a message stating we're done.
    finally:
        print "...Done!"

    # End of outer try block.


# Define doctest test here.
# def _test():
    # import doctest
    # doctest.testmod(verbose=True)


# Begin customized module Exceptions.
# TODO: Clean this up to better conform to standard Excetions.
#       Also, fix try...excepts to match same conventions.
class Error(Exception):
    """Base class for exceptions caused by methods in """ \
            """the vim-undo module."""
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


__all__ = ['prune']

# If we were called from command line...
if __name__ == "__main__":
    import sys

    # TODO: Put in some usage message on bad arg list.
    # User can get to work right away number of arguments.
    if len(sys.argv) == 2:
        prune(sys.argv[1])
    # Otherwise, start walking from current working directory.
    else:
        prune()

# vim: set ts=4 sts=4 sw=4:
