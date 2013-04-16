from contextlib import closing
from distutils.dir_util import remove_tree, mkpath
from distutils import log
import os
import subprocess
import tarfile

try:
    from distutils.sysconfig import get_python_version
except ImportError:
    from sysconfig import get_python_version

from pkg_resources import get_build_platform
from setuptools import Command
import virtualenv


class bdist_venv(Command):
    description = 'Bundle a package as a virtualenv.'
    user_options = [
        ('bdist-dir=', 'b',
            'temporary directory for creating the distribution'),
        ('plat-name=', 'p',
                     'platform name to embed in generated filenames '
                     '(default: %s)' % get_build_platform()),
        ('no-plat-name', None,
                     'do not include the platform name in the generated '
                     'filenames'),
        ('keep-temp', 'k',
                     'keep the installation tree around after '
                     'creating the distribution archive'),
        ('dist-dir=', 'd',
                     'directory to put final built distributions in'),
        ('requirements=', 'r',
                     'pip requirements file to use'),
        ('archive-root=', None,
                     'name of the root folder in the archive '
                     '(default: <name>-<version>)'),
        ('no-archive-root', None,
                     'include the virtualenv folders without another parent '
                     'directory at the root of the archive'),
    ]

    boolean_options = [
        'keep-temp', 'no-plat-name', 'no-archive-root'
    ]

    def initialize_options(self):
        self.bdist_dir = None
        self.plat_name = None
        self.no_plat_name = False
        self.keep_temp = False
        self.dist_dir = None
        self.requirements = None
        self.archive_root = None
        self.no_archive_root = False

    def finalize_options(self):
        ei_cmd = self.get_finalized_command('egg_info')
        self.egg_info = ei_cmd.egg_info

        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'venv')

        if self.no_plat_name:
            self.plat_name = ''
        elif self.plat_name is None:
            self.plat_name = get_build_platform()

        if self.requirements is None and os.path.exists('requirements.txt'):
            self.requirements = 'requirements.txt'

        if self.no_archive_root:
            self.archive_root = '.'
        elif self.archive_root is None:
            self.archive_root = self.distribution.get_fullname()
        elif not self.archive_root:
            self.archive_root = '.'

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

        basename = self.distribution.get_fullname()
        if self.plat_name:
            basename = '%s.%s-py%s' % (basename, self.plat_name,
                                       get_python_version())

        self.venv_output = os.path.join(self.dist_dir, basename + '.tar.gz')

    def get_outputs(self):
        return [self.venv_output]

    def run(self):
        venv_dir = self.bdist_dir

        virtualenv.create_environment(
            venv_dir,
            use_distribute=True,
            never_download=True,
        )

        pip_cmd = [os.path.join(venv_dir, 'bin', 'pip'), 'install', '.']
        if self.requirements:
            pip_cmd.extend(['-r', self.requirements])
        subprocess.check_call(pip_cmd)

        self.copy_file(os.path.join(self.egg_info, 'PKG-INFO'), venv_dir)

        virtualenv.make_environment_relocatable(venv_dir)

        log.info("creating '%s' and adding '%s' to it", self.venv_output,
                 venv_dir)
        mkpath(os.path.dirname(self.venv_output))

        with closing(tarfile.open(self.venv_output, 'w:gz')) as tar:
            tar.add(venv_dir, self.archive_root)

        self.distribution.dist_files.append(('bdist_venv', get_python_version(),
                                             self.venv_output))

        if not self.keep_temp:
            remove_tree(venv_dir)
