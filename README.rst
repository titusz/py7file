==========================================
Py7File - Simple file handling with python
==========================================

*Py7File wraps and unifies the python stdlib file handling modules with a simple
and intuitive high-level api.*

- **Think:** os.path, shutil etc. via object based method access.
- **Author:** *Titusz <tp at py7 de>*
- **PyPi:** http://pypi.python.org/pypi/py7file
- **Source Code**: http://github.com/titusz/py7file
- **License**: BSD

Installation
------------

Use easy_install or pip::

    pip install py7file


Usage
-----
Here some hopefully self explaining examples of Py7File usage::

    from py7file import Py7File

    the_file = Py7File('a_file.txt')

    # Copy and Move
    copied_file = the_file.copy('d_file.txt')  # copied_file is also a Py7file
    the_file.move('moved_file.txt')  # moves the file and mutates the reference

    # Backup and Restore
    the_file.backup()  # creates a_file_backup_001.txt
    the_file.backup()  # creates a_file_backup_002.txt
    the_file.delete()  # removes a_file.txt from disk (ups...)
    the_file.restore() # recovers file from a_file_backup_002.txt

    # Unzip and Rezip
    zfile = Py7File('a_file.zip')
    zfile.unzip() # creates a folder a_file_unzipped with contents of zipfile
    zfile.rezip() # repackages subfolder a_file_unzipped to a_file.zip
    
See test_py7file.py for more examples.

Testing
-------
Py7File is tested against python 2.6 and 2.7

To run the tests::

    python test_py7file.py

Status
------
Well I am using this this file handling library quite extensivly myself and
i got no complaints so far ;). Still please consider this Beta and
use at your own risk...

Background
----------
As I started learning programming with python I found the different modules for
handling files very confusing and cumbersome to use. While writing my first
scripts I found myself writing os.path.join(...) way to often. I still
keep mixing up os and shutil based file operations like copy, move, rename.
So I started this little module to make things easier...