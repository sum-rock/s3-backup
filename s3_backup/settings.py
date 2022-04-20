import os
from dataclasses import dataclass
from typing import List

import yaml


def configs(func):
    def inner(*args, **kwargs):
        c = Configs()
        c.set_up()
        func(*args, configs=c, **kwargs)
        c.tear_down()

    return inner


@dataclass
class SecretConfigKeys:
    env_var_name: str
    yaml_key_name: str


class Configs:
    def __init__(self):
        with open(f"{self.config_dir}/conf.yaml", "r") as file:
            self._config = yaml.load(file, Loader=yaml.Loader)

        with open(f"{self.config_dir}/secrets.yaml", "r") as file:
            self._secrets = yaml.load(file, Loader=yaml.Loader)

        self._secret_key_definitions = [
            SecretConfigKeys(
                env_var_name="AWS_ACCESS_KEY_ID",
                yaml_key_name="aws_access_key_id",
            ),
            SecretConfigKeys(
                env_var_name="PASSPHRASE",
                yaml_key_name="backup_passphrase",
            ),
            SecretConfigKeys(
                env_var_name="AWS_SECRET_ACCESS_KEY",
                yaml_key_name="aws_secret_access_key",
            ),
        ]

    def set_up(self):
        """Sets system environmental variables"""
        os.environ.update(
            {
                d.env_var_name: self._secrets[d.yaml_key_name]
                for d in self._secret_key_definitions
            }
        )

    def tear_down(self):
        """Removes system environmental variables"""
        for d in self._secret_key_definitions:
            if d.env_var_name in os.environ.keys():
                del os.environ[d.env_var_name]

    @classmethod
    @property
    def config_dir(cls) -> str:
        """String path to the config directory.

        This method allows us to mock patch the config directory for tests.
        """
        return "/etc/s3-backup"

    @classmethod
    @property
    def log_dir(cls) -> str:
        """String path to the log directory.

        This method allows us to mock patch the log directory for tests.
        """
        return "/var/log/s3-backup"

    @property
    def s3_url(self) -> str:
        return (
            "s3://s3."
            f"{self._secrets['hosted_region']}.amazonaws.com/"
            f"{self._secrets['bucket_name']}/"
            f"{self._config['backup_folder']}"
        )

    @property
    def source_dir(self) -> str:
        return f"{self._config['source_dir']}"

    @property
    def restore_dir(self) -> str:
        return f"{self._config['restore_dir']}"

    @property
    def exclude_dirs(self) -> List[str]:
        if not self._config["exclude_paths"]:
            return []
        return [f"{self.source_dir}/{x}" for x in self._config["exclude_paths"]]

    @property
    def weeks_until_refresh(self) -> int:
        return int(self._config["weeks_until_refresh"])

    def __enter__(self):
        self.set_up()

    def __exit__(self, *args):
        self.tear_down()
