import datetime as dt
import os
import pathlib
from unittest import TestCase, mock

from dotenv import dotenv_values

from s3_backup import Backup, SettingsConstructor

THIS_DIR = pathlib.Path(__file__).parent.resolve()


def get_test_yaml_data():
    env_values = dotenv_values(".env")
    return {
        "amazon": {
            "aws_access_key_id": env_values.get("aws_access_key_id"),
            "aws_secret_access_key": env_values.get("aws_secret_access_key"),
            "bucket_name": env_values.get("bucket_name"),
            "hosted_region": env_values.get("hosted_region"),
            "folder_path": "/test",
        },
        "backups": {
            "restore_dir": f"{THIS_DIR}/home/restore",
            "sources_dir": f"{THIS_DIR}/home/source",
            "include_dirs": [None],
            "exclude_dirs": [f"{THIS_DIR}/home/source/melville"],
        },
        "options": {
            "weeks_until_log_purge": 5,
            "weeks_until_full_backup": 4,
            "passphrase": "cyGficReKVrd.R4drrqvb*-Y",
        },
    }


test_install_path = mock.MagicMock(return_value=f"{THIS_DIR}/home/.s3-backup")
test_yaml_data = mock.MagicMock(return_value=get_test_yaml_data())


@mock.patch("s3_backup.SettingsConstructor.is_installed", return_value=True)
@mock.patch("s3_backup.SettingsConstructor.install_path", test_install_path())
@mock.patch("s3_backup.SettingsConstructor.yaml_data", test_yaml_data())
class TestBackup(TestCase):
    def test_get_command(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        env_values = dotenv_values(".env")
        s3_url = (
            "s3://s3."
            f"{env_values['hosted_region']}.amazonaws.com/"
            f"{env_values['bucket_name']}"
            f"/test"
        )
        expected_command = (
            "duplicity "
            "--full-if-older-than 4W "
            f"--log-file {THIS_DIR}/home/.s3-backup/logs/my_profile/{today} "
            f"--exclude {THIS_DIR}/home/source/melville "
            f"{THIS_DIR}/home/source "
            f"{s3_url}"
        )

        with Context():
            b = Backup(profile)
            self.maxDiff = None
            self.assertEqual(b.get_command(), expected_command)

    def test_prune_logs(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        # Create some old logs
        old_date_one = (
            (dt.datetime.now() - dt.timedelta(weeks=5, days=1))
            .date()
            .strftime("%Y-%m-%d")
        )
        old_date_two = (
            (dt.datetime.now() - dt.timedelta(weeks=5, days=2))
            .date()
            .strftime("%Y-%m-%d")
        )
        os.system(f"touch {profile.log_dir}/{old_date_one}.log")
        os.system(f"touch {profile.log_dir}/{old_date_two}.log")

        # Verify they were created
        log_files = os.listdir(profile.log_dir)
        self.assertTrue(f"{old_date_one}.log" in log_files)
        self.assertTrue(f"{old_date_two}.log" in log_files)

        with Context():
            Backup(profile)

        # Verify they were created
        log_files = os.listdir(profile.log_dir)
        self.assertFalse(f"{old_date_one}.log" in log_files)
        self.assertFalse(f"{old_date_two}.log" in log_files)

    def test_backup_successful(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        with Context():
            b = Backup(profile)
            b.do_backup()

        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        self.assertTrue(today in os.listdir(profile.log_dir))

        with open(f"{profile.log_dir}/{today}", "r") as file:
            log_content = file.read()
            self.assertTrue("Backup Statistics" in log_content)

        os.remove(f"{profile.log_dir}/{today}")
