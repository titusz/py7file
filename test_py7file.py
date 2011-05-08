# -*- coding: utf-8 -*-
import codecs
import os
from py7file import Py7File
import zipfile
try:
    import unittest2 as unittest
except ImportError:
    import unittest



class Py7FileTest(unittest.TestCase):

    def setUp(self):
        """Create some files for testing"""

        self.root = os.path.abspath(os.path.dirname(__file__))

        # A normal textfile
        self.test_file = os.path.join(self.root, 'testfile.txt')
        with open(self.test_file, 'w') as testfile:
            testfile.write('This is a file for testing')

        # An utf-8 endoded textfile with special chars in filename and content
        self.test_file_utf8 = os.path.join(self.root, u'mußt be german.txt')
        with codecs.open(self.test_file_utf8, 'w', 'UTF-8') as utf8file:
            utf8file.write(u'Indeed this mußt be german...')

        # File without extension
        self.test_file_noext = os.path.join(self.root, 'noextfile')
        with open(self.test_file_noext, 'w') as testfile:
            testfile.write('This is a file for testing')

        #Create test zipfile
        self.test_file_zip = os.path.join(self.root,'zip_test.zip')
        zip_file = zipfile.ZipFile(self.test_file_zip, 'w', zipfile.ZIP_DEFLATED)
        zip_file.writestr('file_in_root.txt', 'just a testfile')
        zip_file.writestr('subfolder/file_in_subfolder.txt', 'just a testfile')
        zip_file.close()

    def tearDown(self):
        os.remove(self.test_file)
        os.remove(self.test_file_utf8)
        os.remove(self.test_file_noext)
        os.remove(self.test_file_zip)


    @property
    def test_object(self):
        return Py7File(self.test_file)

    def test_from_cwd(self):
        the_file = Py7File(os.path.basename(self.test_file))
        self.assertEqual(os.path.basename(self.test_file), the_file.filename)
        self.assertEqual(self.root, the_file.location)
        self.assertEqual(os.path.splitext(self.test_file)[-1].lstrip('.'),
                         the_file.extension)
        self.assertEqual(os.path.basename(self.test_file).split('.')[0],
                         the_file.trunc)

    def test_file_object(self):
        f_obj = file(self.test_file)
        the_file = Py7File(f_obj)
        self.assertEqual(self.root, the_file.location)

    def test_init(self):
        self.assertEqual(Py7File(self.test_file).filepath, self.test_file)
        self.assertEqual(Py7File(self.test_file_utf8).filepath,
                         self.test_file_utf8)
        self.assertEqual(Py7File(self.test_file_zip).extension, 'zip')
        self.assertRaises(TypeError, Py7File, self.test_file_noext)

    def test_backup(self):
        test_file = Py7File(self.test_file)
        test_file.backup()
        self.assertTrue(os.path.isfile(test_file.trunc + '_backup_001.' +
                                        test_file.extension))
        test_file.backup()
        self.assertTrue(os.path.isfile(test_file.trunc + '_backup_002.' +
                                        test_file.extension))
        test_file.delete_backups()
        self.assertFalse(os.path.isfile(test_file.trunc + '_backup_001.' +
                                        test_file.extension))
        self.assertFalse(os.path.isfile(test_file.trunc + '_backup_002.' +
                                        test_file.extension))

    def test_restore(self):
        test_file = Py7File(self.test_file)
        test_file.backup()
        test_file.backup()
        test_file.delete()
        test_file.restore()
        self.assertTrue(os.path.isfile(self.test_file))
        test_file.cleanup()

    def test_copy(self):
        # create testfile
        test_file = Py7File(self.test_file)
        new_file = test_file.copy('test_copy.txt')
        self.assertTrue(os.path.isfile(os.path.join(self.root,'test_copy.txt')))
        self.assertEqual(new_file.filename, 'test_copy.txt')
        # testing secure default
        self.assertRaises(IOError, test_file.copy, 'test_copy.txt')
        # again with overwrite
        new_file2 = test_file.copy('test_copy.txt', secure=False)
        self.assertTrue(os.path.isfile(os.path.join(self.root,'test_copy.txt')))
        self.assertEqual(new_file2.filename, 'test_copy.txt')
        # cleanup
        new_file.delete()

    def test_move(self):
        file_to_move = self.test_object.copy('file_to_move.txt')
        moved_file = file_to_move.move('moved_file.txt')
        self.assertTrue(os.path.isfile(os.path.join(self.root,'moved_file.txt')))
        self.assertFalse(os.path.isfile(os.path.join(self.root,'file_to_move.txt')))
        self.assertEqual('moved_file.txt', moved_file.filename)
        # test secure default
        file_to_move = self.test_object.copy('file_to_move.txt')
        self.assertRaises(IOError, file_to_move.move, 'moved_file.txt')
        # test overwrite
        moved_file = file_to_move.move('moved_file.txt', secure=False)
        self.assertTrue(os.path.isfile(os.path.join(self.root,'moved_file.txt')))
        moved_file.delete()

    def test_delete(self):
        to_delete = self.test_object.copy('delete_me.txt')
        self.assertTrue(os.path.isfile('delete_me.txt'))
        to_delete.delete()
        self.assertFalse(os.path.isfile('delete_me.txt'))
        self.assertFalse(to_delete.exists())

    def test_get_mimetype(self):
        self.assertEqual('text/plain', self.test_object.get_mimeptype())

    def test_get_md5(self):
        hash = self.test_object.get_md5()
        self.assertTrue(isinstance(hash, str))
        self.assertEqual(len(hash), 32)

    def test_get_filesize(self):
        the_file = Py7File(self.test_file)
        self.assertTrue(the_file.get_filesize())
        self.assertTrue(isinstance(the_file.get_filesize(), long))

    def test_zip(self):
        the_file = Py7File(self.test_file_zip)
        the_file.unzip()
        self.assertTrue(os.path.isdir('zip_test'))
        self.assertTrue((os.path.isfile('zip_test/file_in_root.txt')))
        the_file.rezip()
        self.assertTrue(os.path.exists(self.test_file_zip))
        self.assertFalse(os.path.isdir('zip_test'))

    def test_special_chars(self):
        the_file = Py7File(self.test_file_utf8)
        the_file.backup()
        the_file.cleanup()

if __name__ == "__main__":
    unittest.main()
    

        