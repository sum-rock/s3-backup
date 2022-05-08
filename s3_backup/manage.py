import click

from .installation import Installation


class ProcessError(Exception):
    pass


class MangageProfiles(Installation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_installed:
            raise ProcessError(
                "You must initialize the s3-backup program before managing profiles."
            )

    def do_add(self, profile_name: str):
        if profile_name in self.installed_profiles:
            raise click.BadArgumentUsage(
                "A profile with this name has already been created. Please choose a "
                "different name."
            )

        new_profile_path = f"{self.install_path}/profiles/{profile_name}.yaml"
        with open(self._template_path, "r") as t, open(new_profile_path, "w") as n:
            n.write(t.read())
