import os
import re
import sys
from setuptools import setup

setup(name='sync-file-tool',
		description='Sync file to remote',
		version='0.1.0',
		package_dir={'': 'lib'},
		packages=[
				'syncfile',
		],
		author='Candy.Jheng',
		author_email='mary250278@gmail.com',
		install_requires=[
				'PyYAML >= 3.12',
				'paramiko >= 2.0.2',
		],
		entry_points={
				'console_scripts': ['synctool-npd=syncfile.synctool:main', ],
		})