import datetime as dt
import os
import shutil
from unittest import TestCase
from unittest.mock import MagicMock, patch

from s3_backup.commands import Restore
from s3_backup.context import SettingsConstructor

from .profile_mocks import ENV_VALUES, INSTALL_PATH, THIS_DIR, YAML_DATA

install_path = MagicMock(return_value=INSTALL_PATH)
yaml_data = MagicMock(return_value=YAML_DATA)


@patch("s3_backup.context.Installation.is_installed", return_value=True)
@patch("s3_backup.context.Installation.install_path", install_path())
@patch("s3_backup.context.SettingsConstructor.yaml_data", yaml_data())
class TestRestore(TestCase):
    def test_get_command(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()
        s3_url = (
            "s3://s3."
            f"{ENV_VALUES['hosted_region']}.amazonaws.com/"
            f"{ENV_VALUES['bucket_name']}"
            f"/test"
        )

        today = dt.datetime.now().strftime("%Y-%m-%d")
        expected_command = f"duplicity restore {s3_url} {THIS_DIR}/home/restore/{today}"
        with Context():
            r = Restore(profile)
            self.assertEqual(r.get_command(), expected_command)

    def test_restore_successful(self, *args):
        settings = SettingsConstructor(profile_name="my_profile")
        Context = settings.get_context_klass()
        profile = settings.get_profile()

        with Context():
            r = Restore(profile)
            r.do_restore(opts={"--allow-source-mismatch": ""})

        today = dt.datetime.now().strftime("%Y-%m-%d")
        restore_dir = f"{THIS_DIR}/home/restore/{today}"

        self.assertTrue("dickens" in os.listdir(restore_dir))
        self.assertTrue("dracula.txt" in os.listdir(restore_dir))
        self.assertFalse("melville" in os.listdir(restore_dir))
        self.assertTrue(
            "a_tale_of_two_cities.txt" in os.listdir(f"{restore_dir}/dickens")
        )
        self.assertTrue(
            "great_expectations.txt" in os.listdir(f"{restore_dir}/dickens")
        )
        shutil.rmtree(restore_dir)
