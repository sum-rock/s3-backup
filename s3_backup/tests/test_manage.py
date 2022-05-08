import os
import pathlib
from unittest import TestCase, mock

import click

from s3_backup import ManageProfiles

THIS_DIR = pathlib.Path(__file__).parent.resolve()
test_install_path = mock.MagicMock(return_value=f"{THIS_DIR}/home/.s3-backup")


@mock.patch("s3_backup.Installation.is_installed", return_value=True)
@mock.patch("s3_backup.Installation.install_path", test_install_path())
class TestAddProfile(TestCase):
    def test_do_add(self, *args):
        manager = ManageProfiles()
        profile_dir = f"{manager.install_path}/profiles"
        self.assertFalse(os.path.isfile(f"{profile_dir}/my_new_profile.yaml"))

        manager.do_add("my_new_profile")
        self.assertTrue(os.path.isfile(f"{profile_dir}/my_new_profile.yaml"))
        os.remove(f"{profile_dir}/my_new_profile.yaml")

    def test_do_add_error_if_profile_exists(self, *args):
        manager = ManageProfiles()
        profile_dir = f"{manager.install_path}/profiles"
        self.assertTrue(os.path.isfile(f"{profile_dir}/my_profile.yaml"))

        with self.assertRaises(click.BadArgumentUsage):
            manager.do_add("my_profile")
