import os
import shutil

from s3_backup.context import Installation


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
        path = self.get_profile_path(name)
        with open(self._template_path, "r") as t, open(path, "w") as n:
            n.write(t.read())

        if not os.path.isdir(self.get_log_path(name)):
            os.makedirs(self.get_log_path(name))

    def do_edit(self, name: str):
        os.system(f"vim {self.get_profile_path(name)}")

    def do_remove(self, name: str):
        os.system(f"rm {self.get_profile_path(name)}")
        if os.path.isdir(self.get_log_path(name)):
            shutil.rmtree(self.get_log_path(name))
