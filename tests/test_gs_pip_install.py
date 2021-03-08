#!/usr/bin/env python
"""Tests for `gs_pip_install` package."""

import unittest
import tempfile
import shutil
import os
import sys
from unittest import mock

from click.testing import CliRunner

from gs_pip_install import gs_pip_install


class TestInstall(unittest.TestCase):

    example_packages = ['package', 'versioned_package==1.3.1']
    download_dir = 'gs_packages'
    req_dir = 'requirements'
    req_file = os.path.join(req_dir, 'requirements_gcs.txt')

    def setUp(self):
        mock.patch('google.cloud')
        self.test_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.test_dir, self.req_dir))
        os.mkdir(os.path.join(self.test_dir, self.download_dir))
        for package in self.example_packages:
            with open(os.path.join(self.test_dir, self.req_file), 'a') as f:
                f.write(f'{package}\n')
            # Create empty files for packages
            with open(os.path.join(self.test_dir, self.download_dir, package), 'x'):
                pass

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @mock.patch('gs_pip_install.gs_pip_install.download_packages')
    @mock.patch('gs_pip_install.gs_pip_install.install_packages')
    def test_cli_default_args(self, mock_install, mock_download):
        project = 'middle_earth'
        bucket = 'the-shire'
        pkg_dir_default = 'gcs_packages'
        req_file_default = 'requirements_google_storage.txt'

        install_args = ['--project_id', project, '--bucket_name', bucket]

        runner = CliRunner()
        runner.invoke(gs_pip_install.main, install_args)
        mock_download.assert_called_once_with(
            project_id=project,
            bucket_name=bucket,
            gs_requirements_file=req_file_default,
            packages_download_dir=pkg_dir_default,
        )
        mock_install.assert_called_once_with(pkg_dir_default, '')

        req_file_new = 'req.txt'
        pkg_dir_new = 'down_dir'
        target_dir_new = 'bullseye'
        install_args += [
            '--req_file',
            req_file_new,
            '--download_dir',
            pkg_dir_new,
            '--target_dir',
            target_dir_new,
        ]
        runner.invoke(
            gs_pip_install.main,
            install_args,
        )
        mock_download.assert_called_with(
            project_id=project,
            bucket_name=bucket,
            gs_requirements_file=req_file_new,
            packages_download_dir=pkg_dir_new,
        )
        mock_install.assert_called_with(pkg_dir_new, target_dir_new)

    @mock.patch('google.cloud.storage.Client')
    @mock.patch('os.mkdir')
    def test_download_packages(self, mock_mkdir, mock_gcs):
        req_filepath = os.path.join(self.test_dir, self.req_file)
        with mock.patch('os.path.join') as mock_path:
            gs_pip_install.download_packages(
                packages_download_dir=self.download_dir,
                bucket_name='the-shire',
                project_id='middle-earth',
                gs_requirements_file=req_filepath,
            )

            expected_path_calls = [
                mock.call(self.download_dir, 'package.tar.gz'),
                mock.call(self.download_dir, 'versioned_package-1.3.1.tar.gz'),
            ]
            assert mock_path.call_count == 2
            mock_path.assert_has_calls(expected_path_calls)

    @mock.patch('subprocess.check_output')
    def test_install_packages_no_target_dir(self, mock_subprocess):
        package_dest = os.path.join(self.test_dir, self.download_dir)
        gs_pip_install.install_packages(packages_download_dir=package_dest)
        for package in self.example_packages:
            mock_subprocess.call_count == 2
            mock_subprocess.assert_any_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--quiet",
                    f"{os.path.join(package_dest, package)}",
                ]
            )

    @mock.patch('subprocess.check_output')
    def test_install_packages_with_target_dir(self, mock_subprocess):
        package_dest = os.path.join(self.test_dir, self.download_dir)
        test_target_dir = 'some_dir'

        # mock_bucket = storage_client.get_bucket('test-bucket')
        # mock_blob = mock_bucket.blob('blob1')
        gs_pip_install.install_packages(
            packages_download_dir=package_dest, target_dir=test_target_dir
        )
        for package in self.example_packages:
            mock_subprocess.call_count == 2
            mock_subprocess.assert_any_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--quiet",
                    "--no-deps",
                    "-t",
                    test_target_dir,
                    f"{os.path.join(package_dest, package)}",
                ]
            )
