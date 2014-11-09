from distutils.core import setup

import nback

# TODO(niklas9):
# * make this forward compatible with Python 3 etc, see how imports are done in
#   https://github.com/boto/boto/blob/develop/setup.py or
#   https://github.com/kennethreitz/requests/blob/master/setup.py

setup(
    name="nback",
    version=nback.__version__,
    license="MIT",
    author="Niklas Andersson",
    author_email="nandersson900@gmail.com",
    packages=['nback', 'nback/lib', 'nback/lib/db', 'nback/lib/storage'],
    scripts=['nback/nback'],
    include_package_data=True,
    url='https://github.com/Niklas9/nback',
    description='Backups files and databases (MySQL, MongoDB) to AWS S3',
    long_description='',
    platforms='Linux Ubuntu',
    install_requires=[
        "boto",
    ],
)
