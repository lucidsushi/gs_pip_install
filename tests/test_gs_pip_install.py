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

    @mock.patch('gs_pip_install.gs_pip_install.install_packages')
    @mock.patch('gs_pip_install.gs_pip_install.download_packages')
    def test_cli_package_name(self, mock_download, mock_install):
        bucket = 'the-shire'
        pkg_dir_diff = 'gcs_packages'
        package_name = 'one-ring'
        target_dir = 'bullseye'

        install_args = [
            '-b',
            bucket,
            '-r',
            package_name,
            '-t',
            target_dir,
            '-d',
            pkg_dir_diff,
        ]
        runner = CliRunner()
        runner.invoke(gs_pip_install.main, install_args)

        mock_download.assert_called_once_with(
            bucket_name=bucket,
            package_list=[package_name],
            packages_download_dir=pkg_dir_diff,
        )
        mock_install.assert_called_once_with(pkg_dir_diff, target_dir, extras={})

    @mock.patch('gs_pip_install.gs_pip_install.install_packages')
    @mock.patch('gs_pip_install.gs_pip_install.download_packages')
    def test_cli_req_file(self, mock_download, mock_install):
        req_file_path = os.path.join(self.test_dir, self.req_file)
        bucket = 'the-shire'
        pkg_dir_default = 'gcs_packages'

        install_args = ['-b', bucket, '-r', req_file_path]

        runner = CliRunner()
        runner.invoke(gs_pip_install.main, install_args)
        mock_download.assert_called_once_with(
            bucket_name=bucket,
            package_list=self.example_packages,
            packages_download_dir=pkg_dir_default,
        )
        mock_install.assert_called_once_with(pkg_dir_default, '', extras={})

    @mock.patch('google.cloud.storage.Client')
    @mock.patch('os.mkdir')
    def test_download_packages(self, mock_mkdir, mock_gcs):
        with mock.patch('os.path.join') as mock_path:
            gs_pip_install.download_packages(
                packages_download_dir=self.download_dir,
                bucket_name='the-shire',
                package_list=self.example_packages,
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
                    "--upgrade",
                    f"{os.path.join(package_dest, package)}",
                ]
            )

    @mock.patch('subprocess.check_output')
    def test_install_packages_with_target_dir(self, mock_subprocess):
        package_dest = os.path.join(self.test_dir, self.download_dir)
        test_target_dir = 'some_dir'

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
                    '--upgrade',
                    "-t",
                    test_target_dir,
                    f"{os.path.join(package_dest, package)}",
                ]
            )

    @mock.patch('os.listdir')
    @mock.patch('subprocess.check_output')
    def test_install_packages_with_extras(self, mock_subprocess, mock_list_dir):

        mock_list_dir.return_value = ['some_package.tar.gz']
        gs_pip_install.install_packages(
            packages_download_dir='some_download_dest',
            extras={'some_package': '[extra_a, extra_b]'},
        )
        mock_subprocess.assert_called_once_with(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--upgrade",
                "some_download_dest/some_package.tar.gz[extra_a, extra_b]",
            ]
        )

    def test_strip_extras(self):

        # fmt: off
        assert gs_pip_install._strip_extras(
            'some_package.tar.gz[extra_a, extra_b]'
        ) == (
            'some_package.tar.gz', '[extra_a, extra_b]'
        )
        # fmt: on
