import json
import os
from functools import cached_property
from typing import List

import yaml


class ConfigurationError(Exception):
    pass


class ProgrammingError(Exception):
    pass


class Profile:
    s3_url: str
    restore_dir: str
    include_dirs: List[str]
    exclude_dirs: List[str]
    weeks_until_log_purge: int
    weeks_until_full_backup: int

    def __init__(self, **kwargs):
        for key, value in kwargs:
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"{key} is not a specified property on Profile")


class ContextManager:
    aws_access_key_id: str
    aws_secret_access_key: str
    passphrase: str

    def __init__(self, **kwargs):
        for key, value in kwargs:
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"{key} is not a specified property on ContextManager")

    def __enter__(self):
        os.environ.update(
            {
                "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
                "PASSPHRASE": self.passphrase,
            }
        )

    def __exit__(self, *args, **kwargs):
        for variable in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "PASSPHRASE"]:
            if variable in os.environ.keys():
                del os.environ[variable]


class SettingsConstructor:
    """Constructs a context manager and profile from a given profile name."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name

        if self.profile_name not in self.installed_profiles:
            raise ConfigurationError(
                f"{self.profile_name} is not found in the configured profiles."
            )
        with open(f"{self.install_path}/profiles/{self.profile_name}.yaml") as file:
            self.yaml_data = yaml.load(file, Loader=yaml.Loader)

    @cached_property
    def is_installed(self) -> bool:
        """Determine if s3-backup has been installed/setup."""
        return "install.json" in os.listdir("./data")

    @cached_property
    def install_path(self) -> str:
        """The path where s3-backup has installed the profile directories."""
        if not self.is_installed:
            raise ConfigurationError(
                "Cannot retrieve installation path because s3-backup is not initialized"
            )
        with open("./data/install.json", "r") as file:
            data = json.load(file)
            return data["path"]

    @cached_property
    def installed_profiles(self) -> List[str]:
        """A list of profiles that have been installed."""
        return [
            x.replace(".yaml", "") for x in os.listdir(f"{self.install_path}/profiles")
        ]

    def get_profile(self) -> Profile:
        """Construct a Profile object from the given profile name."""
        amazon = self.yaml_data.get("amazon", {})
        backups = self.yaml_data.get("backups", {})
        options = self.yaml_data.get("options", {})
        s3_url = (
            "s3://s3."
            f"{amazon['hosted_region']}.amazonaws.com/"
            f"{amazon['bucket_name']}/"
            f"{amazon['folder_url']}"
        )
        return Profile(
            s3_url=s3_url,
            restore_dir=backups.get("restore_dir"),
            include_dirs=backups.get("include_dirs"),
            exclude_dirs=backups.get("exclude_dirs"),
            weeks_until_log_purge=options.get("weeks_until_log_purge"),
            weeks_until_full_backup=options.get("weeks_until_full_backup"),
        )

    def get_context_manager(self) -> ContextManager:
        """Construct a ContextManager object from the given profile name."""
        amazon = self.yaml_data.get("amazon", {})
        options = self.yaml_data.get("options", {})
        return ContextManager(
            aws_access_key_id=amazon.get("aws_access_key_id"),
            aws_secret_access_key=amazon.get("aws_secret_access_key"),
            passphrase=options.get("passphrase"),
        )
