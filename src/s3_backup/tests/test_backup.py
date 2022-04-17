import datetime as dt
import os
import pathlib
from unittest import TestCase, mock

from s3_backup.backup import Backup
from s3_backup.settings import Configs, configs

THIS_DIR = pathlib.Path(__file__).parent.resolve()
test_config_dir_mock = mock.MagicMock(return_value=f"{THIS_DIR}/config")
test_log_dir_mock = mock.MagicMock(return_value=f"{THIS_DIR}/logs")
test_source_dir_mock = mock.MagicMock(return_value=f"{THIS_DIR}/source")


@mock.patch("s3_backup.settings.Configs.config_dir", test_config_dir_mock())
@mock.patch("s3_backup.settings.Configs.log_dir", test_log_dir_mock())
@mock.patch("s3_backup.settings.Configs.source_dir", test_source_dir_mock())
class TestBackup(TestCase):
    @configs
    def test_create_exclusion_list(self, *args, configs: Configs):
        Backup(configs)

        log_files = os.listdir(configs.log_dir)
        self.assertTrue(".exclude-files.txt" in log_files)
        with open(f"{configs.log_dir}/.exclude-files.txt", "r") as file:
            text = file.read()
            self.assertEqual(text, f"{THIS_DIR}/source/melville\n")

    @configs
    def test_prune_logs(self, *args, configs: Configs):
        old_date_one = (
            (dt.datetime.now() - dt.timedelta(weeks=4, days=1))
            .date()
            .strftime("%Y-%m-%d")
        )
        old_date_two = (
            (dt.datetime.now() - dt.timedelta(weeks=5)).date().strftime("%Y-%m-%d")
        )
        os.system(f"touch {configs.log_dir}/{old_date_one}.log")
        os.system(f"touch {configs.log_dir}/{old_date_two}.log")

        Backup(configs)
        log_files = os.listdir(configs.log_dir)
        self.assertEqual(len(log_files), 1)
        self.assertFalse(f"{old_date_one}.log" in log_files)
        self.assertFalse(f"{old_date_two}.log" in log_files)

    @configs
    def test_backup_success(self, *args, configs: Configs):
        b = Backup(configs)
        cmd = b.get_command()
        os.system(cmd)

        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        self.assertTrue(today in os.listdir(configs.log_dir))

        with open(f"{configs.log_dir}/{today}", "r") as file:
            log_content = file.read()
            self.assertTrue("Backup Statistics" in log_content)

        os.remove(f"{configs.log_dir}/{today}")
