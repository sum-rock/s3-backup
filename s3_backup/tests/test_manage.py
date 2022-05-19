import os
import pathlib
import shutil
from unittest import TestCase, mock

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
        self.assertTrue(os.path.isdir(manager.get_log_path("my_new_profile")))

        os.remove(f"{profile_dir}/my_new_profile.yaml")
        shutil.rmtree(manager.get_log_path("my_new_profile"))
