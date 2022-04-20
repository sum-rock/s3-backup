import os
import pathlib
import re
from unittest import TestCase, mock

from s3_backup.settings import Configs, configs

THIS_DIR = pathlib.Path(__file__).parent.resolve()
test_config_dir_mock = mock.MagicMock(return_value=f"{THIS_DIR}/config")


@mock.patch("s3_backup.settings.Configs.config_dir", test_config_dir_mock())
class TestConfigs(TestCase):
    def setUp(self):
        self.keys_expected = {
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "PASSPHRASE",
        }

    def test_environment_variables(self, *args):
        with Configs():
            for key in self.keys_expected:
                self.assertTrue(isinstance(os.environ.get(key), str))

        for key in self.keys_expected:
            self.assertEqual(os.environ.get(key, "gone"), "gone")

    def test_s3_url(self, *args):
        c = Configs()
        self.assertTrue(re.match(r"^s3://s3\..*\.amazonaws\.com.*$", c.s3_url))

    def test_paths(self, *args):
        c = Configs()
        self.assertEqual(c.source_dir, "tests/source")
        self.assertEqual(c.restore_dir, "tests/restore")
        self.assertEqual(c.exclude_dirs, ["tests/source/melville"])

    def test_weeks_until_refresh(self, *args):
        c = Configs()
        self.assertEqual(c.weeks_until_refresh, 4)

    @configs
    def test_decorator(self, *args, **kwargs):
        for key in self.keys_expected:
            self.assertTrue(isinstance(os.environ.get(key), str))

        configs = kwargs["configs"]
        configs.tear_down()

        for key in self.keys_expected:
            self.assertEqual(os.environ.get(key, "gone"), "gone")
