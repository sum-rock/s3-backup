import datetime as dt
import os

from .settings import Profile


class Backup:
    def __init__(self, profile: Profile):
        self.profile = profile
        self._purge_logs()

    def _purge_logs(self):
        """Prune the log files that are dated prior to the cuttoff defined in yaml."""
        cuttoff_date = (
            dt.datetime.now() - dt.timedelta(weeks=self.profile.weeks_until_log_purge)
        ).date()

        existing_logs = [
            x for x in os.listdir(self.profile.log_dir) if x.endswith(".log")
        ]
        for existing_log in existing_logs:
            no_extension = existing_log.replace(".log", "")
            try:
                log_date = dt.datetime.strptime(no_extension, "%Y-%m-%d").date()
            except ValueError:
                continue

            if log_date < cuttoff_date:
                os.remove(f"{self.profile.log_dir}/{existing_log}")

    @property
    def _new_log_path(self):
        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        if today in os.listdir(self.profile.log_dir):
            os.remove(f"{self.profile.log_dir}/{today}")
        return f"{self.profile.log_dir}/{today}"

    def get_command(self) -> str:
        cmd = "duplicity "
        cmd += f"--full-if-older-than {self.profile.weeks_until_full_backup}W "
        cmd += f"--log-file {self._new_log_path} "

        for include_path in self.profile.include_dirs:
            if isinstance(include_path, str):
                cmd += f"--include {include_path} "

        for exclude_path in self.profile.exclude_dirs:
            if isinstance(exclude_path, str):
                cmd += f"--exclude {exclude_path} "

        cmd += f"{self.profile.sources_dir} "
        cmd += f"{self.profile.s3_url}"
        return cmd

    def do_backup(self):
        os.system(self.get_command())
