import os

import click

from .installation import Installation


class ProcessError(Exception):
    pass


class ManageProfiles(Installation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_installed:
            raise ProcessError(
                "You must initialize the s3-backup program before managing profiles."
            )

    def do_add(self, name: str):
        if name in self.installed_profiles:
            raise click.BadArgumentUsage(
                "A profile with this name has already been created. Please choose a "
                "different name."
            )

        path = self.get_profile_path(name)
        with open(self._template_path, "r") as t, open(path, "w") as n:
            n.write(t.read())

    def do_edit(self, name: str):
        if name not in self.installed_profiles:
            raise click.BadArgumentUsage("A profile with this name does not exist.")
        os.system(f"vim {self.get_profile_path(name)}")

    def do_remove(self, name: str):
        if name not in self.installed_profiles:
            raise click.BadArgumentUsage("A profile with this name does not exist.")
        os.system(f"rm {self.get_profile_path(name)}")
