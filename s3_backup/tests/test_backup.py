import datetime as dt
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from s3_backup.commands import Backup
from s3_backup.context import SettingsConstructor

from .profile_mocks import ENV_VALUES, INSTALL_PATH, THIS_DIR, YAML_DATA

install_path = MagicMock(return_value=INSTALL_PATH)
yaml_data = MagicMock(return_value=YAML_DATA)


@patch("s3_backup.context.Installation.is_installed", return_value=True)
@patch("s3_backup.context.Installation.install_path", install_path())
@patch("s3_backup.context.SettingsConstructor.yaml_data", yaml_data())
class TestBackup(TestCase):
    def test_get_command(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        s3_url = (
            "s3://s3."
            f"{ENV_VALUES['hosted_region']}.amazonaws.com/"
            f"{ENV_VALUES['bucket_name']}"
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

        # Verify they were deleted
        log_files = os.listdir(profile.log_dir)
        self.assertFalse(f"{old_date_one}.log" in log_files)
        self.assertFalse(f"{old_date_two}.log" in log_files)

    def test_backup_successful(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        with Context():
            b = Backup(profile)
            b.do_backup(opts={"--allow-source-mismatch": ""})

        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        self.assertTrue(today in os.listdir(profile.log_dir))

        with open(f"{profile.log_dir}/{today}", "r") as file:
            log_content = file.read()
            self.assertTrue("Backup Statistics" in log_content)

        os.remove(f"{profile.log_dir}/{today}")
