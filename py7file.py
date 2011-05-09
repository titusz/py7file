# -*- coding: utf-8 -*-

"""
A module wrapping and unifying the python standard lib file handling modules
and built-in functions with a simple and intuitive high-level api.
Think: os.path, shutil, file, open, ... with convenient method based access.

The Py7File class allows to do simple copy, move, backup, delete, unzip/rezip
operations on files


"""
import codecs
from glob import glob

import os
import shutil
import hashlib
import mimetypes
import zipfile

class Py7File(object):

    """A file on a filesystem with simple handling"""

    def __init__(self, file_or_path):
        """Initialize a Py7File by passing  a file path or file object."""

        if (isinstance(file_or_path, file) and hasattr(file_or_path, 'name')
                and os.path.isfile(file_or_path.name)):
            self._filepath = file_or_path.name
            # Lets have a clean slate
            file_or_path.close()
        elif os.path.isfile(file_or_path):
            self._filepath = file_or_path
        else:
            raise TypeError('Need a valid file object or path!')

    @property
    def filepath(self):
        """Absolute path to the referenced file."""
        return unicode(os.path.abspath(self._filepath))

    @property
    def filename(self):
        """The name of the referenced file."""
        return os.path.basename(self._filepath)

    @property
    def location(self):
        """Absolute path to the folder of the referenced file"""
        return os.path.abspath(os.path.dirname(self._filepath))

    @property
    def extension(self):
        """Filename extension of the referenced file (without ".")."""
        return os.path.splitext(self._filepath)[-1].lstrip('.')

    @property
    def trunc(self):
        """Filename of the referenced file without extension."""
        return os.path.splitext(self.filename)[0]

    @property
    def zipdir(self):
        """Absolute path to folder for unzipped version of referenced file."""
        return os.path.join(self.location, self.trunc + '_unzipped')

    def read(self, size=None):
        """Read file, close and return data."""
        with open(self.filepath) as the_file:
            if size:
                data = the_file.read(size)
            else:
                data = the_file.read()
        return data

    def get_backups(self):
        """Return a sorted list of available backups of the referenced file."""
        return sorted(glob(os.path.join(self.location, (self.trunc +
                                    "_backup_" + "*" + self.extension))))

    def __eq__(self, other):
        """Compare files based on md5 hash"""
        if not isinstance(other, Py7File):
            return NotImplemented
        else:
            return self.get_md5() == other.get_md5()

    def backup(self):
        """Create and return a backup with auto incremented version."""

        version = 1
        out_path = os.path.join(self.location, u"{0}{1}{2:03d}".format(
                            self.trunc, '_backup_', version))

        if len(self.extension):
            out_path += '.' + self.extension

        while os.path.isfile(out_path):
            version += 1
            out_path = os.path.join(self.location, u"{0}{1}{2:03d}".format(
                            self.trunc, '_backup_', version))
            if len(self.extension):
                out_path += '.' + self.extension

        self.copy(out_path)
        return Py7File(out_path)

    def restore(self):
        """Restore referenced file from latest backup"""
        latest_backup = Py7File(self.get_backups()[-1])
        latest_backup.copy(self.filepath)

    def copy(self, dest, secure=True):
        """Copy file to existing destination directory or filepath.

        Returns a PyFile object for the copied file
        """
        if secure and os.path.isfile(dest):
            raise IOError('Destination file already exists')
        else:
            shutil.copy(self.filepath, dest)
            return Py7File(dest)

    def move(self, dest, secure=True):
        """Move file to existing destination directory or filepath.

        This deletes the file that the current Py7File object references.
        So it mutates itself to reference the new file and also returns self.
        """
        if secure and os.path.isfile(dest):
            raise IOError('Destination file already exists')
        else:
            shutil.move(self.filepath, dest)
            self._filepath = dest
            return self

    def delete(self):
        """Delete file from disk but keep object data for eventual restore."""
        os.remove(self.filepath)

    def delete_backups(self):
        """Delete all backups of the referenced file"""
        for backup in self.get_backups():
            os.remove(backup)

    def delete_zip_folder(self):
        """Delete eventual unzipped folder"""
        if os.path.isdir(self.zipdir):
            shutil.rmtree(self.zipdir)

    def get_mimeptype(self):
        """Return mimetype of the file."""
        return mimetypes.guess_type(self.filename)[0]

    def get_md5(self):
        """Return the MD5 hash of the file."""
        file_obj = open(self.filepath, 'rb')
        md5_caldulator = hashlib.md5()
        while True:
            data = file_obj.read(128)
            if not data:
                break
            md5_caldulator.update(data)
        file_obj.close()
        return md5_caldulator.hexdigest()

    def get_filesize(self):
        """Return the size of referenced file in bytes."""
        return os.path.getsize(self.filepath)

    def unzip(self):
        """Unzip the file to [filebane]_unzipped named subfolder."""
        zip_file = zipfile.ZipFile(self.filepath)
        try:
            zip_file.extractall(self.zipdir)
        finally:
            zip_file.close()

    def rezip(self):
        """Re-Zip a previously unzipped file and remove unzipped folder."""
        fzip = zipfile.ZipFile(self.filepath, 'w', zipfile.ZIP_DEFLATED)
        if not os.path.isdir(self.zipdir):
            raise IOError('No "{}" folder to rezip'.format(self.trunc))
        for root, dirs, files in os.walk(self.zipdir):
            dirname = root.replace(self.zipdir, '')
            for the_file  in files:
                fzip.write(root + '/' + the_file, dirname + '/' + the_file)
        fzip.close()
        self.delete_zip_folder()

    def cleanup(self):
        """Remove backups and unzipped files."""
        self.delete_backups()
        self.delete_zip_folder()

    def exists(self):
        """Check if referenced file still exists."""
        return os.path.exists(self.filepath)

    def is_binary(self):
        """Return true if the referenced file is binary.

        @attention: not 100% reliable

        """
        the_file = open(self.filepath, 'rb')

        # Check for Byte-Order-Marker
        fragment = the_file.read(128)
        if fragment.startswith(codecs.BOM):
            return False

        the_file.seek(0)
        try:
            bsize = 1024
            while 1:
                fragment = the_file.read(bsize)
                if '\0' in fragment:
                    return True
                if len(fragment) < bsize:
                    break
        finally:
            the_file.close()
        return False

    def is_zip_file(self):
        """Return true if the referenced file is a zip file"""
        return zipfile.is_zipfile(self.filepath)
