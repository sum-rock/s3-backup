import json
import os
import pathlib

import click

THIS_DIR = str(pathlib.Path(__file__).parent.resolve())
INSTALL_JSON = f"{THIS_DIR}/data/install.json"


def initialize_to_path(initialization_path: str):

    # Verify that the path is real
    if not os.path.isdir(initialization_path):
        raise click.BadArgumentUsage(
            "This path is not a directory. Please choose a valid path."
        )

    # If we have a record of installation, append last path to old paths.
    if os.path.isfile(INSTALL_JSON):
        with open(INSTALL_JSON, "r") as file:
            data = json.load(file)

        if data.get("path") == initialization_path:
            raise click.BadArgumentUsage(
                "This is already the installation path. No action required."
            )

        old_paths = data.get("old_paths", [])
        old_paths += [data.get("path")]
        data.update(
            {"old_paths": [x for x in old_paths if x], "path": initialization_path}
        )

    # If no installation record, create one
    else:
        data = {"path": initialization_path}

    # Create the directory structure if they don't exist
    os.makedirs(f"{initialization_path}/.s3-backup/logs")
    os.makedirs(f"{initialization_path}/.s3-backup/profiles")

    # Set the installation record.
    with open(INSTALL_JSON, "w") as file:
        json.dump(data, file, indent=4)
