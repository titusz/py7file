# -*- coding: utf-8 -*-
"""
=======
py7file
=======

A module wrapping and unifying the python standard lib file handling modules
and built-in functions with a simple and intuitive high-level api.
Think: os.path, shutil, file, open, ... with convenient method based access.

The Py7File class allows to do simple copy, move, backup, delete, unzip/rezip
operations on files
"""
import codecs
from glob import glob
import gzip

import os
import re
import shutil
import hashlib
import mimetypes
import string
import zipfile
import filecmp


class Py7File(object):

    """
    A file on a filesystem with many convenience mathods.

    :param file_or_path: A path to a file or an actual file object.
    """

    def __init__(self, file_or_path):
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
        """Absolute path to the folder of the referenced file."""
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
        """Absolute path to folder for unzipped version of referenced file.
        """
        return os.path.join(self.location, self.trunc + '_unzipped')

    def __repr__(self):
        return "{0}(r'{1}')".format(self.__class__.__name__, self.filepath)

    def __str__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.filename)

    def __eq__(self, other):
        """Compare file contents with other file.

        Accepts Py7File objects, file objects and strings that are a path to
        another file.
        """
        if isinstance(other, (Py7File, EpubFile)):
            return filecmp.cmp(self.filepath, other.filepath, shallow=False)
        elif isinstance(other, file):
            return filecmp.cmp(self.filepath, other.name, shallow=False)
        elif isinstance(other, (str, unicode)) and os.path.isfile(other):
            return filecmp.cmp(self.filepath, other, shallow=False)
        else:
            return NotImplemented

    def read(self, size=None):
        """Read file, close and return data."""
        with open(self.filepath) as the_file:
            if size:
                data = the_file.read(size)
            else:
                data = the_file.read()
        return data

    def backup(self):
        """Create a backup with auto incremented version number in filename.

        :rtype: :class:`py7file.Py7File` instance of backup file.
        """

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
        return self.__class__(out_path)

    def restore(self):
        """Restore referenced file from latest backup"""
        latest_backup = self.__class__(self.get_backups()[-1])
        latest_backup.copy(self.filepath)

    def copy(self, dest, secure=True):
        """Copy file to existing destination directory or filepath.

        :rtype: :class:`py7file.Py7File` instance of copied file.
        """
        if secure and os.path.isfile(dest):
            raise IOError('Destination file already exists')
        else:
            shutil.copy(self.filepath, dest)
            return self.__class__(dest)

    def move(self, dest, secure=True):
        """Move file to existing destination directory or filepath.

        This deletes the file that the current Py7File object references.
        So it mutates itself to reference the new file and also returns self.

        :rtype: :class:`py7file.Py7File` instance of moved file.
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
            shutil.rmtree(self.zipdir, ignore_errors=True)

    def get_backups(self):
        """
        :return: A sorted list of available backups of the referenced file.
        :rtype: `list`
        """
        return sorted(glob(os.path.join(self.location, (self.trunc +
                                        "_backup_" + "*" + self.extension))))

    def get_filesize(self):
        """
        :return: The size of referenced file in bytes.
        """
        return os.path.getsize(self.filepath)

    def get_md5(self):
        """
        :return: MD5 hash of the file.
        """
        file_obj = open(self.filepath, 'rb')
        md5_caldulator = hashlib.md5()
        while True:
            data = file_obj.read(128)
            if not data:
                break
            md5_caldulator.update(data)
        file_obj.close()
        return md5_caldulator.hexdigest()

    def get_mimeptype(self):
        """
        :return: Mimetype of the file.
        """
        return mimetypes.guess_type(self.filename)[0]

    def get_number(self):
        """Scan filename for numbering.

        :return: The file number as an integer or None
        :rtype: int, None
        """
        number = [n for n in self.trunc if n in string.digits]
        number = ''.join(number)
        if number:
            return int(number)
        else:
            return None

    def get_sanitized_filename(self):
        """Create a sanatized version of the filename.

        :return: Portable and secure version of filename.
        """
        codecs.register_error("replace_", self._replace_under_error_handler)
        ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
        windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4',
                                'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')

        if isinstance(self.filename, unicode):
            from unicodedata import normalize
            filename = normalize('NFKD', self.filename).encode('ascii',
                                                               'replace_')
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = self.filename.replace(sep, ' ')
        filename = str(ascii_strip_re.sub('_', '_'.join(
            filename.split()))).strip('._')

        if os.name == 'nt' and filename and\
           filename.split('.')[0].upper() in windows_device_files:
            filename = '_' + filename

        return filename

    def unzip(self):
        """Unzip the file to [filename]_unzipped named subfolder.

        :returns: list of Py7File objects for all extracted files
        """
        unzipped_files = list()
        if self.extension in ['zip','epub','']:
            zip_file = zipfile.ZipFile(self.filepath)
            try:
                zip_file.extractall(self.zipdir)
            finally:
                zip_file.close()

            for root, subFolders, files in os.walk(self.zipdir):
                for f in files:
                    unzipped_files.append(Py7File(os.path.join(root, f)))
        elif self.extension == 'gz':
            gz_file = gzip.GzipFile(self.filepath, 'rb')
            if not os.path.isdir(self.zipdir):
                os.mkdir(self.zipdir)
            outpath = os.path.join(self.zipdir, self.trunc)
            unzipped_file = file(outpath, 'wb')
            while 1:
                lines = gz_file.readline()
                if lines == '': break
                unzipped_file.write(lines)
            gz_file.close()
            unzipped_file.close()
            unzipped_files.append(Py7File(outpath))
        return unzipped_files
        

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
        """Check if referenced file still exists.

        :rtype: boolean
        """
        return os.path.exists(self.filepath)

    def is_binary(self):
        """Check if file is binary.

        .. warning::
            not 100% reliable

        :rtype: boolean

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
        """Check if the referenced file is a zip file

        :rtype: boolean
        """
        return zipfile.is_zipfile(self.filepath)

    def _replace_under_error_handler(self, error):
        """Handle encoding errors with '_' replacement"""
        return u'_' * (error.end - error.start), error.end


class EpubFile(Py7File):
    """An ePub file with special rezip handling"""

    def rezip(self):
        """Re-Zip a previously unzipped epub and remove unzipped folder."""

        exclude_files = ['.DS_Store', 'mimetype', 'iTunesMetadata.plist']
        parent_dir, dir_to_zip = os.path.split(self.zipdir)

        def trim(path):
            """Prepare archive path"""
            zip_path = path.replace(parent_dir, "", 1)
            if parent_dir:
                zip_path = zip_path.replace(os.path.sep, "", 1)
            zip_path = zip_path.replace(dir_to_zip + os.path.sep, "", 1)
            return zip_path

        outfile = zipfile.ZipFile(self.filepath, "w",
                                  compression=zipfile.ZIP_DEFLATED)

        # ePub Zips need uncompressed mimetype-file as first file
        outfile.write(os.path.join(self.zipdir, 'mimetype'), 'mimetype',
                      compress_type=0)

        for root, dirs, files in os.walk(self.zipdir):
            for file_name in files:
                if file_name in exclude_files:
                    continue
                file_path = os.path.join(root, file_name)
                outfile.write(file_path, trim(file_path))
            # Also add empty directories
            if not files and not dirs:
                zip_info = zipfile.ZipInfo(trim(root) + "/")
                outfile.writestr(zip_info, "")
        outfile.close()
        self.delete_zip_folder()
