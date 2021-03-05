import os
import subprocess
import sys

import click
from google.cloud import storage

@click.command()
@click.option("--download_dir", default="")
@click.option(
    "--target_dir", default="", help="(str) Directory to install package into"
)
@click.option("--project_id", help="(str) Name of GCP project")
@click.option("--bucket_name", help="(str) gs://some-bucket")
@click.option("--req_file", help="(str) Name of Python requirements file")
def main(download_dir, target_dir, project_id,bucket_name, req_file):
    """Pip install {pkg_name}/{pkg_name_versioned}.tar.gz to
    current enviroment or a target directory

    (1) Copy package_name.tar.gz from Google Cloud bucket

    (2) Pip Install package_name.tar.gz into staging directory

    (3) Remove the package_name.tar.gz
    """
    download_packages(
        bucket_name=bucket_name,
        project_id=project_id,
        gs_requirements_file=req_file,
        packages_download_dir=download_dir
    )
    install_packages(download_dir,target_dir)

def install_packages(packages_download_dir, target_dir):
    """[summary]

    :param packages_download_dir: [description]
    :type packages_download_dir: [type]
    """
    for gs_package_zip_file in os.listdir(packages_download_dir):
        if target_dir:
            install_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                f"{packages_download_dir}/{gs_package_zip_file}"
            ]
        else:
            install_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--no-deps",
                "-t",
                target_dir,
                f"{packages_download_dir}/{gs_package_zip_file}"
            ]
        try:
            subprocess.check_output(install_command)
        except:
            logging.warning("Attempting pip install with pyenv python")
            install_command[0] = f"{os.environ['HOME']}/.pyenv/shims/python"
            subprocess.check_output(install_command)

    shutil.rmtree(packages_download_dir)


def download_packages(
    packages_download_dir: str,
    bucket_name: str,
    project_id: str,
    gs_requirements_file="requirements/requirements_google_storage.txt",
):
    """[summary]

    :param packages_download_dir: [description]
    :type packages_download_dir: [type]
    :param gs_requirements_file: [description], defaults to "requirements/requirements_google_storage.txt"
    :type gs_requirements_file: str, optional
    :param bucket_name: [description]
    :type bucket_name: str, optional
    """
    # gs_packages_destination = os.path.join(packages_download_dir)
    os.mkdir(packages_download_dir)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    with open(gs_requirements_file) as gs_requirements:
        for package_name in gs_requirements.readlines():
            package_name = package_name.rstrip("\n")

            name_no_version = package_name.split("==")[0]
            name_versioned = package_name.replace("==", "-")

            package_filepath = f"{name_versioned}.tar.gz"
            gs_package_path = f"{name_no_version}/{package_filepath}"

            blob_package = bucket.blob(gs_package_path)
            blob_package.download_to_filename(os.path.join(packages_download_dir, package_filepath))
            # subprocess.call(["gsutil", "cp", gs_package_path, gs_packages_destination])
