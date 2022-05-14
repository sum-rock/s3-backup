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
