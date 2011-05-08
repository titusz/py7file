from setuptools import setup
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2'

setup(name='py7file',
    version=version,
    description="Convenient File Handling Library",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Desktop Environment :: File Managers',
      'Topic :: System :: Filesystems',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Utilities'
    ],
    keywords='file copy move backup unzip open os.path shutil wrapper api',
    author='Titusz',
    author_email='tp@py7.de',
    url='http://github.com/titusz/py7file',
    license='BSD',
)
