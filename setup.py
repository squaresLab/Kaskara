import os
import glob
import setuptools

path = os.path.join(os.path.dirname(__file__), 'python/kaskara/version.py')
with open(path, 'r') as f:
    exec(f.read())

setuptools.setup(
    name='kaskara',
    version=__version__,
    description='A simple static analyer for C++',
    long_description='TBA',
    author='Chris Timperley',
    author_email='christimperley@gmail.com',
    url='https://github.com/ChrisTimperley/Bond',
    license='Apache-2.0',
    python_requires='>=3.5',
    install_requires=[
        'bugzoo>=2.1.20',
        'rooibos>=0.3.0',
        'boggart>=0.1.8',
        'attrs>=17.2.0',
        'requests>=2.0.0'
    ],
    packages=['kaskara'],
    package_dir={'': 'python'},
    entry_points = {
        'console_scripts': [ 'kaskara-test = kaskara.test:test' ]
    }
)
