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
        if os.path.isfile(requirement):
            with open(requirement) as gs_requirements:
                for package_name in gs_requirements.readlines():
                    packages.append(package_name.strip())
        else:
            packages.append(requirement)

        download_packages(
            bucket_name=bucket_name,
            package_list=packages,
            packages_download_dir=download_dir,
        )
        logging.info('download done')
        install_packages(download_dir, target)
    finally:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)


def install_packages(packages_download_dir: str, target_dir: Optional[str] = None):
    """Install packages found in local directory. Do not install dependencies if
    target directory is specified.

    Args:
        packages_download_dir (str): Directory containing packages
        target_dir (str): Destination to install packages
    """
    for gs_package_zip_file in os.listdir(packages_download_dir):
        if not target_dir:
            install_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--upgrade",
                f"{packages_download_dir}/{gs_package_zip_file}",
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
                f"{packages_download_dir}/{gs_package_zip_file}",
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

    for package_name in package_list:
        name_no_version = package_name.split("==")[0]
        name_versioned = package_name.replace("==", "-")

        package_filepath = f"{name_versioned}.tar.gz"
        gs_package_path = f"{name_no_version}/{package_filepath}"

        blob_package = bucket.blob(gs_package_path)
        blob_package.download_to_filename(
            os.path.join(packages_download_dir, package_filepath)
        )
