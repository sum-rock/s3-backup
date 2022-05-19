from unittest import TestCase, mock

import click

from s3_backup import Installation

from .profile_mocks import INSTALL_PATH

test_install_path = mock.MagicMock(return_value=INSTALL_PATH)


@mock.patch("s3_backup.Installation.is_installed", return_value=True)
@mock.patch("s3_backup.Installation.install_path", test_install_path())
class TestInstallation(TestCase):
    def test_verify_profile(self, *args):
        i = Installation()
        with self.assertRaises(click.BadArgumentUsage):
            i.verify_profile(name="This does not exist")
