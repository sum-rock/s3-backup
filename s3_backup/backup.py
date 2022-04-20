import datetime as dt
import os

from .settings import Configs


class Backup:
    def __init__(self, configs: Configs):
        self.configs = configs
        self._create_exclusion_list()
        self._prune_logs()

    def _create_exclusion_list(self):
        """Parse list of excluded files from the yaml config and write to temp file."""
        exclude_file = f"{self.configs.log_dir}/.exclude-files.txt"
        with open(exclude_file, "+w") as file:
            file.writelines(f"{i}\n" for i in self.configs.exclude_dirs)

    def _prune_logs(self):
        """Prune the log files that are dated prior to the cuttoff defined in yaml."""
        cuttoff_date = (
            dt.datetime.now() - dt.timedelta(weeks=self.configs.weeks_until_refresh)
        ).date()

        existing_logs = [
            x for x in os.listdir(self.configs.log_dir) if x.endswith(".log")
        ]
        for existing_log in existing_logs:
            no_extension = existing_log.replace(".log", "")
            try:
                log_date = dt.datetime.strptime(no_extension, "%Y-%m-%d").date()
            except ValueError:
                continue

            if log_date < cuttoff_date:
                os.remove(f"{self.configs.log_dir}/{existing_log}")

    @property
    def _new_log_path(self):
        today = f"{dt.datetime.now().strftime('%Y-%m-%d')}.log"
        if today in os.listdir(self.configs.log_dir):
            os.remove(f"{self.configs.log_dir}/{today}")
        return f"{self.configs.log_dir}/{today}"

    def get_command(self) -> str:
        cmd = "duplicity "
        cmd += f"--full-if-older-than {self.configs.weeks_until_refresh}W "
        cmd += f"--log-file={self._new_log_path} "
        cmd += f"--exclude-filelist={self.configs.log_dir}/.exclude-files.txt "
        cmd += f"{self.configs.source_dir} "
        cmd += f"{self.configs.s3_url}"
        return cmd
