from typing import TYPE_CHECKING
import datetime as dt
import os
from typing import Optional

if TYPE_CHECKING:
    from s3_backup.context import Profile


class Restore:
    def __init__(self, profile: "Profile"):
        self.profile = profile

    def get_restore_path(self):
        if os.path.isdir(self.profile.restore_dir) and (
            self.profile.restore_dir != self.profile.sources_dir
        ):
            today = dt.datetime.now().strftime("%Y-%m-%d")
            return f"{self.profile.restore_dir}/{today}"
        return self.profile.restore_dir

    def get_command(self, opts: Optional[dict] = None):
        cmd = "duplicity restore "

        if isinstance(opts, dict):
            for key, value in opts.items():
                cmd += f"{key} {value} "

        cmd += f"{self.profile.s3_url} "
        cmd += f"{self.get_restore_path()}"
        return cmd

    def do_restore(self, opts: Optional[dict] = None):
        os.system(self.get_command(opts=opts))
