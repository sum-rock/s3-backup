import json
import os
import pathlib
from functools import cached_property
from typing import List

import click

THIS_DIR = str(pathlib.Path(__file__).parent.resolve())


class Installation:
    """General Information about the installation"""

    @cached_property
    def _install_json_path(self):
        return f"{THIS_DIR}/data/install.json"

    @property
    def is_installed(self):
        return os.path.isfile(self._install_json_path)

    @property
    def _install_data(self) -> dict:
        if not self.is_installed:
            raise click.BadOptionUsage(
                "--profile",
                "Cannot retrieve installation data because s3-backup is not initialized",
            )

        with open(self._install_json_path, "r") as file:
            data = json.load(file)
        return data

    @property
    def install_path(self) -> str:
        """The path where s3-backup has installed the profile directories."""
        return self._install_data.get("path")

    @property
    def old_install_paths(self) -> List[list]:
        return self._install_data.get("old_paths", [])

    @property
    def installed_profiles(self) -> List[str]:
        """A list of profiles that have been installed."""
        return [
            x.replace(".yaml", "") for x in os.listdir(f"{self.install_path}/profiles")
        ]
