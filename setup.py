from distutils.core import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'datatables_server_side_django_3',
  packages = ['_dt_server_side'],
  version = '0.2',
  license='MIT',
  description = 'Datatables Server Side package for django 3',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Onesinus SPT',
  author_email = 'onesinus231@gmail.com',
  url = 'https://github.com/onesinus/datatable-server-side-django3',
  download_url = 'https://github.com/onesinus/datatable-server-side-django3/archive/0.2.zip',
  keywords = ['DATATABLES', 'PYTHON', 'DJANGO', 'DJANGO3', 'SERVERSIDE', 'DJANGO-DATATABLES'],
  install_requires=[
    'six'
  ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)