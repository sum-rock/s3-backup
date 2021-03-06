import os
from functools import cached_property
from typing import List, Type

import yaml

from .installation import Installation


class Profile:
    s3_url: str = ""
    restore_dir: str = ""
    sources_dir: str = ""
    include_dirs: List[str] = []
    exclude_dirs: List[str] = []
    weeks_until_log_purge: int = 0
    weeks_until_full_backup: int = 0
    log_dir: str = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"{key} is not a specified property on Profile")


class ContextManager:
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    passphrase: str = ""

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


class SettingsConstructor(Installation):
    """Constructs a context manager and profile from a given profile name."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name

    def verify_profile(self):
        return super().verify_profile(name=self.profile_name)

    @cached_property
    def yaml_data(self):
        with open(f"{self.install_path}/profiles/{self.profile_name}.yaml") as file:
            yaml_data = yaml.load(file, Loader=yaml.Loader)
        return yaml_data

    @property
    def _s3_url(self) -> str:
        amazon = self.yaml_data.get("amazon", {})
        return (
            "s3://s3."
            f"{amazon['hosted_region']}.amazonaws.com/"
            f"{amazon['bucket_name']}"
            f"{amazon['folder_path']}"
        )

    @property
    def _log_dir(self) -> str:
        return f"{self.install_path}/logs/{self.profile_name}"

    def get_profile(self) -> Profile:
        """Construct a Profile object from the given profile name."""
        backups = self.yaml_data.get("backups", {})
        options = self.yaml_data.get("options", {})
        return Profile(
            s3_url=self._s3_url,
            restore_dir=backups.get("restore_dir"),
            sources_dir=backups.get("sources_dir"),
            include_dirs=backups.get("include_dirs"),
            exclude_dirs=backups.get("exclude_dirs"),
            weeks_until_log_purge=options.get("weeks_until_log_purge"),
            weeks_until_full_backup=options.get("weeks_until_full_backup"),
            log_dir=self._log_dir,
        )

    def get_context_klass(self) -> Type[ContextManager]:
        """Construct a ContextManager object from the given profile name."""
        amazon = self.yaml_data.get("amazon", {})
        options = self.yaml_data.get("options", {})

        class ProfileContext(ContextManager):
            aws_access_key_id = amazon.get("aws_access_key_id")
            aws_secret_access_key = amazon.get("aws_secret_access_key")
            passphrase = options.get("passphrase")

        return ProfileContext
