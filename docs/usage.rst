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