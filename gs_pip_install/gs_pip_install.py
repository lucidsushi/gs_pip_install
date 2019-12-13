import os
import subprocess
import sys

import click


@click.command()
@click.option('--bucket_url', help='(str) gs://some-bucket')
@click.option('--package_name', help='(str) Name of Python package')
@click.option('--target_dir', default='', help='(str) Directory to install package into')  # noqa: E501
def gs_pip_install(bucket_url, package_name, target_dir):
    """Pip install {bucket_url}/{pkg_name}/{pkg_name_versioned}.tar.gz to
    current enviroment or a target directory

    (0) "gsutil" command line tool must exist

    (1) Copy package_name.tar.gz from Google Cloud bucket

    (2) Pip Install package_name.tar.gz into staging directory

    (3) Remove the package_name.tar.gz
    """

    pkg_name_versioned = package_name.replace('==', '-')
    pkg_name_clean = package_name.split('==')[0]

    gs_package_path = (
        '{bucket_url}/{pkg_name}/{pkg_name_versioned}.tar.gz'.format(
            bucket_url=bucket_url,
            pkg_name=pkg_name_clean,
            pkg_name_versioned=pkg_name_versioned)
    )
    gs_package_name = os.path.basename(gs_package_path)

    if target_dir:
        pip_install = [sys.executable, '-m', 'pip', 'install',
                       '--no-deps', '-t', target_dir, gs_package_name]
    else:
        pip_install = [sys.executable, '-m', 'pip', 'install', gs_package_name]

    for cmd in (
        ['gsutil', 'cp', gs_package_path, '.'],
        pip_install,
        ['rm', gs_package_name]
    ):
        subprocess.call(cmd)
