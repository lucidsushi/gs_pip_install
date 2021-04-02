import os
import subprocess
import sys
import shutil
import logging
from typing import Optional, List

import click
from google.cloud import storage


@click.command()
@click.option('-b', "--bucket_name", help="(str) Name of GCS bucket")
@click.option(
    '-r',
    "--requirement",
    help="(str) Name of Python package or requirements file",
)
@click.option(
    '-d',
    "--download_dir",
    default="gcs_packages",
    help="(optional, str) File download destination",
)
@click.option("-t", "--target", default="", help="(str) Package install destination")
def main(bucket_name, requirement, download_dir, target):
    """Pip install {pkg_name}/{pkg_name_versioned}.tar.gz to
    current enviroment or a target directory

    (1) Copy package_name.tar.gz from Google Cloud bucket

    (2) Pip Install package_name.tar.gz into staging directory

    (3) Remove the package_name.tar.gz
    """
    try:
        packages = []
        extras = {}
        
        if os.path.isfile(requirement):
            with open(requirement) as gs_requirements:
                for package_name in gs_requirements.readlines():
                    
                    package, package_extras = _strip_extras(package_name.strip())
                    
                    packages.append(package)
                    extras[package] = package_extras
        else:
            # Split package from extras
            package, extras = _strip_extras(requirement)
            
            packages.append(package)
            extras[package] = package_extras
            

        download_packages(
            bucket_name=bucket_name,
            package_list=packages,
            packages_download_dir=download_dir,
        )
        logging.info('download done')
        install_packages(download_dir, target, extras=extras)
    finally:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)


def install_packages(packages_download_dir: str, target_dir: Optional[str] = None, 
                     extras: dict = {}):
    """Install packages found in local directory. Do not install dependencies if
    target directory is specified.

    Args:
        packages_download_dir (str): Directory containing packages
        target_dir (str): Destination to install packages
        extras (dict): Dicctionary of extras to install per package
    """
    for gs_package_zip_file in os.listdir(packages_download_dir):
        
        package = gs_package_zip_file.split('.')[0]
        install_path = f"{packages_download_dir}/{gs_package_zip_file}"
        
        # Support installation of extras
        if extras.get(package) is not None:               
            package_extras = extras[package]
            install_path = f"{install_path}[{package_extras}]"
        
        if not target_dir:
            install_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--upgrade",
                install_path,
            ]
        else:
            install_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--no-deps",
                "--upgrade",
                "-t",
                target_dir,
                install_path,
            ]
        try:
            subprocess.check_output(install_command)
        except Exception:
            logging.warning("Attempting pip install with pyenv python")
            install_command[0] = f"{os.environ['HOME']}/.pyenv/shims/python"
            subprocess.check_output(install_command)


def download_packages(
    packages_download_dir: str,
    bucket_name: str,
    package_list: List[str],
):
    """Download Python packages from GCS into a local directory.

    Args:
        packages_download_dir (str): Local directory to download packages into
        bucket_name (str): Name of GCS bucket to download packages from
        packages list(str): Names of packages found in bucket
    """
    os.mkdir(packages_download_dir)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # TODO: Allow for []

    for package_name in package_list:
        
        name_no_version = package_name.split("==")[0]
        name_versioned = package_name.replace("==", "-")

        package_filepath = f"{name_versioned}.tar.gz"
        gs_package_path = f"{name_no_version}/{package_filepath}"

        blob_package = bucket.blob(gs_package_path)
        blob_package.download_to_filename(
            os.path.join(packages_download_dir, package_filepath)
        )
        
        
def _strip_extras(path):
    """
        The function splits a package name into package without extras
        and extras.
        Function obtained from PIP Source Code
        https://github.com/pypa/pip/blob/5bc7b33d41546c218e2ae786b02a7d30c2d1723c/src/pip/_internal/req/constructors.py#L42   
    """
    
    
    # type: (str) -> Tuple[str, Optional[str]]
    m = re.match(r'^(.+)(\[[^\]]+\])$', path)
    extras = None
    if m:
        path_no_extras = m.group(1)
        extras = m.group(2)
    else:
        path_no_extras = path

    return path_no_extras, extras

