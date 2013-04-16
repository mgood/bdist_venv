import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''


setup(
    name='bdist_venv',
    version='0.1.0',
    url='http://github.com/mgood/bdist_venv',
    license='BSD',
    author='Matt Good',
    author_email='matt@matt-good.net',
    description='Python distutils extension to bundle package as a virtualenv.',
    long_description=README + '\n\n' + CHANGES,
    zip_safe=True,
    platforms='any',
    py_modules=['bdist_venv'],
    install_requires=[
        'virtualenv',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'distutils.commands': [
            'bdist_venv = bdist_venv:bdist_venv',
        ],
    },
)
