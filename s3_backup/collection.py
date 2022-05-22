import os

from .settings import Profile


class Collection:
    def __init__(self, profile: Profile):
        self.profile = profile

    def get_collection_status(self):
        cmd = f"duplicity collection-status {self.profile.s3_url}"
        os.system(cmd)

    def get_file_list(self):
        cmd = f"duplicity list-current-files {self.profile.s3_url}"
        os.system(cmd)

    def do_cleanup(self):
        cmd = "duplicity cleanup --force"
        cmd += self.profile.s3_url
        os.system(cmd)

    def do_prune(self, count: int):
        cmd = "duplicity remove-all-but-n-full "
        cmd += f"{count} "
        cmd += "--force "
        cmd += self.profile.s3_url
        os.system(cmd)
