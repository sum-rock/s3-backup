import json
import os
import pathlib
import shutil
from unittest import TestCase

import click

from s3_backup.context import Initialize

TEST_DIR = str(pathlib.Path(__file__).parent.resolve())
TEST_S3_BACKUP = f"{TEST_DIR}/.s3-backup"
TEST_INSTALL_JSON = f"{TEST_DIR}/../data/install.json"
SECOND_TEST_S3_BACKUP = f"{TEST_DIR}/home/restore/.s3-backup"


class TestInitialization(TestCase):
    @staticmethod
    def clear_if_installed():
        if os.path.isdir(TEST_S3_BACKUP):
            shutil.rmtree(TEST_S3_BACKUP)
        if os.path.isdir(SECOND_TEST_S3_BACKUP):
            shutil.rmtree(SECOND_TEST_S3_BACKUP)
        if os.path.isfile(TEST_INSTALL_JSON):
            os.remove(TEST_INSTALL_JSON)

    def tearDown(self):
        self.clear_if_installed()

    def test_initialization_path(self):
        self.clear_if_installed()

        Initialize().do_initialize(TEST_DIR)
        self.assertTrue(os.path.isfile(TEST_INSTALL_JSON))

        with open(TEST_INSTALL_JSON, "r") as file:
            data = json.load(file)

        self.assertEqual(data["path"], TEST_S3_BACKUP)
        self.assertTrue(os.path.isdir(f"{TEST_S3_BACKUP}/logs"))
        self.assertTrue(os.path.isdir(f"{TEST_S3_BACKUP}/profiles"))

        self.clear_if_installed()

    def test_update_old_paths_when_installed_twice(self):
        self.clear_if_installed()

        i = Initialize()
        i.do_initialize(TEST_DIR)
        self.assertTrue(os.path.isfile(TEST_INSTALL_JSON))

        with open(TEST_INSTALL_JSON, "r") as file:
            data = json.load(file)

        self.assertEqual(data["path"], TEST_S3_BACKUP)
        i.do_initialize(f"{TEST_DIR}/home/restore")

        with open(TEST_INSTALL_JSON, "r") as file:
            new_data = json.load(file)

        self.assertEqual(new_data["path"], f"{TEST_DIR}/home/restore/.s3-backup")
        self.assertEqual(new_data["old_paths"], [TEST_S3_BACKUP])

        self.clear_if_installed()

    def test_error_when_install_path_does_not_exist(self):
        with self.assertRaises(click.BadArgumentUsage):
            Initialize().do_initialize("this/does/not/exist")

    def test_error_when_install_path_is_already_the_path_installed(self):
        self.clear_if_installed()
        i = Initialize()
        i.do_initialize(TEST_DIR)
        self.assertTrue(os.path.isdir(TEST_S3_BACKUP))

        with self.assertRaises(click.BadArgumentUsage):
            i.do_initialize(TEST_DIR)
