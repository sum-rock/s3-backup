import os
import pathlib
from typing import Set
from unittest import TestCase, mock

from click import BadOptionUsage

from s3_backup import SettingsConstructor

THIS_DIR = pathlib.Path(__file__).parent.resolve()
test_install_path = mock.MagicMock(return_value=f"{THIS_DIR}/home/.s3-backup")


@mock.patch("s3_backup.SettingsConstructor.is_installed", return_value=True)
@mock.patch("s3_backup.SettingsConstructor.install_path", test_install_path())
class TestSettingsConstructor(TestCase):
    def setUp(self):
        self.expected_yaml_data = {
            "amazon": {
                "aws_access_key_id": "aws-access-99999999",
                "aws_secret_access_key": "aws-secret-88888888",
                "bucket_name": "test-bucket",
                "hosted_region": "us-east-1",
                "folder_path": "/test-bucket-folder",
            },
            "backups": {
                "restore_dir": "tests/home/restore",
                "sources_dir": "tests/home/source",
                "include_dirs": [None],
                "exclude_dirs": ["tests/home/source/melville"],
            },
            "options": {
                "weeks_until_log_purge": 5,
                "weeks_until_full_backup": 4,
                "passphrase": "cyGficReKVrd.R4drrqvb*-Y",
            },
        }

        amazon = self.expected_yaml_data["amazon"]
        self.expected_log_dir = f"{THIS_DIR}/home/.s3-backup/logs/my_profile"
        self.expected_s3_url = (
            "s3://s3."
            f"{amazon['hosted_region']}.amazonaws.com/"
            f"{amazon['bucket_name']}"
            f"{amazon['folder_path']}"
        )

    def test_list_installed_profiles(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        self.assertEqual(s.installed_profiles, ["my_profile"])

    def test_yaml_data(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        self.assertEqual(s.yaml_data, self.expected_yaml_data)

    def test_yaml_data_error_when_no_profile(self, *args):
        s = SettingsConstructor(profile_name="this_does_not_exist")
        with self.assertRaises(BadOptionUsage):
            s.get_profile()

    def test_get_profile(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        profile = s.get_profile()

        self.assertEqual(self.expected_s3_url, profile.s3_url)
        self.assertEqual(self.expected_log_dir, profile.log_dir)

        backups = self.expected_yaml_data["backups"]
        self.assertEqual(backups["restore_dir"], profile.restore_dir)
        self.assertEqual(backups["sources_dir"], profile.sources_dir)
        self.assertEqual(backups["include_dirs"], profile.include_dirs)
        self.assertEqual(backups["exclude_dirs"], profile.exclude_dirs)

        options = self.expected_yaml_data["options"]
        self.assertEqual(
            options["weeks_until_log_purge"], profile.weeks_until_log_purge
        )
        self.assertEqual(
            options["weeks_until_full_backup"], profile.weeks_until_full_backup
        )

    def test_s3_url(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        self.assertEqual(s._s3_url, self.expected_s3_url)

    def test_log_dir(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        self.assertEqual(s._log_dir, self.expected_log_dir)

    def test_context_manager(self, *args):
        s = SettingsConstructor(profile_name="my_profile")
        Context = s.get_context_klass()

        expected_vars = {
            "AWS_ACCESS_KEY_ID": "aws-access-99999999",
            "AWS_SECRET_ACCESS_KEY": "aws-secret-88888888",
            "PASSPHRASE": "cyGficReKVrd.R4drrqvb*-Y",
        }

        with Context():
            for key, expected_value in expected_vars.items():
                observed_value = os.environ.get(key)
                self.assertEqual(observed_value, expected_value)

        for key, _ in expected_vars.items():
            observed_value = os.environ.get(key, "missing")
            self.assertEqual(observed_value, "missing")
