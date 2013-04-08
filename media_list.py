#!/usr/bin/env python2
#
# Copyright (C) 2013 Dylan Steinmetz <dtsteinm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
# Last updated: March 31, 2013

"""Module with functions to simplify the sorting of media files with """\
        """complex filenames, and create playlist files for playback."""
import os
import re

__all__ = ['makeplaylist', 'sortfiles', 'getseqnum', 'mkpls', 'mkm3u']
__author__ = 'Dylan Steinmetz <dtsteinm@gmail.com>'
__version__ = '0.2.2'
__license__ = 'WTFPL'


# TODO: Make playlist_type selection clearer.
# TODO: Add a 'depth' option, or something along those lines.
def makeplaylist(start_dir=os.getcwd(), playlist_type='pls'):
    """Create media playlist(s) for specified directory and playlist """\
            """type.

    Attributes:
        start_dir -- directory from which to start; if None, prompt user?
        playlist_type -- type of playlist to create; 'pls' and/or 'm3u'

    Example: media_list.makeplaylist('/path/to/media', """ \
            """playlist_type=['pls','m3u'])
    """

    # Clean up user input
    start_dir = os.path.expanduser(start_dir.strip())

    try:
        if os.path.isdir(start_dir) is False:
            raise DirectoryError(start_dir)

        # Flags for what kind of playlist file to create.
        # These variables must exist for later execution, so declare
        # them as false for now.
        PLS = False
        M3U = False

        # TODO: There _has_ to be a better way to do this.
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
        # media_exts = ['mkv', 'avi', 'wmv', 'mp4', 'mp3', 'flac', 'ogg']

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
                mkpls(basedir, sortfiles(files))
            if M3U:
                mkm3u(basedir, sortfiles(files))

        # End of os.walk() for loop

    except DirectoryError as e:
        print '\n{} does not exist.'.format(e)
    except:
        pass

    # End of try...except block
# End of makeplaylist function


def mkpls(directory, file_list):
    """Creates a PLS format playlist file from a base directory and a """\
            """list of filenames.

    Attributes:
        directory -- directory in which sorted files are stored
        file_list -- a sorted list of files
    """

    # Retrieve title of media from filesystem structure, and make it
    # more human readable.
    # TODO: Perform more intelligent title extraction
    #       (comparison of start_dir against directory?)
    name = os.path.basename(directory)
    title = re.sub('[._]', ' ', name)

    file_ = name + '.pls'

    try:
        if os.path.isfile(file_):
            raise PlaylistExistsError(file_)
        
        # Open the file using the same basename as used in the filesystem.
        with open(file_, 'w') as f:

            # Used to count extra materials.
            extra = 1

            # Heading for PLS files, skip a line.
            f.write('[playlist]\n\n')

            # Iterate, getting an entry number and filename for each file.
            for i, file_ in enumerate(file_list, 1):

                # Number used for this entry in the PLS file.
                entry_num = str(i)

                # Sequence number for actual content.
                seqnum = getseqnum(file_)

                # Mark unsortable files as an 'Extra' in the playlist.
                if seqnum == 9999:
                    title_num = 'Extra ' + str(extra)
                    extra += 1
                else:
                    title_num = str(seqnum)

                # Absolute path to file.
                f.write('File' + entry_num + '=' +
                        os.path.join(directory, file_) + '\n')
                # Title of file displayed to user.
                f.write('Title' + entry_num + '=' +
                        title + ' ' + title_num + '\n')

            # Standard data for playlist file.
            f.write('\nNumberOfEntries=' + str(i))
            f.write('\nVersion=2\n')

            # End of enumerated for loop
        # End of with block
    except PlaylistExistsError as e:
        print '\n{} already exists.'.format(e)
    except:
        pass
    # End of try...except block
# End of mkpls function


def mkm3u(directory, file_list):
    """Creates a M3U format playlist file from a base directory and a """\
            """list of filenames.

    Attributes:
        directory -- directory in which sorted files are stored
        file_list -- a sorted list of files
    """

    # Retrieve title of media from filesystem structure, and make it
    # more human readable.
    # TODO: Perform more intelligent title extraction
    #       (comparison of start_dir against directory?)
    name = os.path.basename(directory)
    title = re.sub('[._]', ' ', name)

    file_ = name + '.m3u'

    try:
        if os.path.isfile(file_):
            raise PlaylistExistsError(file_)

        # Open the file using the same basename as used in the filesystem.
        with open(file_, 'w') as f:

            # Used to count extra materials.
            extra = 1

            # Heading for M3U files, skip a line.
            f.write('#EXTM3U\n\n')

            # Iterate, getting an entry number and filename for each file.
            for file_ in file_list:

                # Sequence number for actual content.
                seqnum = getseqnum(file_)

                # Mark unsortable files as an 'Extra' in the playlist.
                if seqnum == 9999:
                    title_num = 'Extra ' + str(extra)
                    extra += 1
                else:
                    title_num = str(seqnum)

                # TODO: Make sure this is valid in an m3u
                # Title of file displayed to user.
                f.write('#EXTINF:' + title + ' ' + title_num + '\n')
                # Absolute path to file.
                f.write(os.path.join(directory, file_) + '\n')

            # End of for loop
        # End of with block

    except PlaylistExistsError as e:
        print '\n{} already exists.'.format(e)
    except:
        pass

    # End of try...except block
# End of mkm3u function

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

    # TODO: Allow sorting of files in format SXXEYY
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

    def __str__(self):
        return repr(self.dir_)


class PlaylistExistsError(Error):
    """Exception raised for errors relating to file """ \
            """existence.

    Attributes:
        file_ -- file which caused the error
    """

    def __init__(self, file_):
        Exception.__init__(self)
        self.file_ = file_

    def __str__(self):
        return repr(self.file_)


# If we were called from command line...
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create PLS or M3U \
            playlists")
    parser.add_argument('-v', '--version', action='version',
            version='%(prog)s ' + __version__)
    parser.add_argument('-t','--playlist-type', default='pls',
            choices=['pls','m3u'], help='type of playlist to create')
    parser.add_argument('directory', nargs='?',
            help='starting directory')
    args = parser.parse_args()

    # FIXME: makeplaylist does not like non-default values of 
    #        args.playlist_type
    if args.directory is not None:
        makeplaylist(args.directory, args.playlist_type)
    else:
        makeplaylist(playlist_type=args.playlist_type)


# vim: set ts=4 sts=4 sw=4 et:
