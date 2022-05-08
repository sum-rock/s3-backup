import json
import os
import pathlib

import click

from .installation import Installation

THIS_DIR = str(pathlib.Path(__file__).parent.resolve())
INSTALL_JSON = f"{THIS_DIR}/data/install.json"


class Initialize(Installation):
    """Initializes the program by creating a directory for profiles."""

    def do_initialize(self, new_install_path: str):
        """Command entry point.

        This method validates the path and handels the creation of the
        installation file and the directory structure for the install location.
        """
        # Raise error if not given a directory path
        if not os.path.isdir(new_install_path):
            raise click.BadArgumentUsage(
                "This path is not a directory. Please choose a valid path."
            )
        # Raise error new install path is the same as the old install path
        if self.is_installed and self.install_path == new_install_path:
            raise click.BadArgumentUsage(
                "This is already the installation path. No action required."
            )
        # If this is already installed, then set the current path into the old
        # path list
        elif self.is_installed:
            self._set_current_path_to_old_paths()

        # Set the new path to into the installation file
        self._set_new_install_path(new_install_path)
        install_path = self.install_path
        assert install_path == new_install_path

        # Create the folder structure
        os.makedirs(f"{install_path}/.s3-backup/logs")
        os.makedirs(f"{install_path}/.s3-backup/profiles")

    def _write_to_path_file(self, data: dict):
        """Write the given data to the installation file."""
        with open(self._install_json_path, "w") as file:
            json.dump(data, file, indent=2)

    def _set_current_path_to_old_paths(self):
        """Adds the current path to the list of old paths.

        Writes a new installation file.
        """
        install_path = self.install_path
        old_paths = list(set([*self.old_install_paths, install_path]))
        old_paths.sort()
        self._write_to_path_file({"path": install_path, "old_paths": old_paths})

    def _set_new_install_path(self, new_install_path: str):
        """Writes the new path to the installation file.

        The list of old paths is preserved.
        """
        data = {
            "path": new_install_path,
            "old_paths": [] if not self.is_installed else self.old_install_paths,
        }
        self._write_to_path_file(data)
