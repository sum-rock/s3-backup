import pathlib

from dotenv import dotenv_values

THIS_DIR = pathlib.Path(__file__).parent.resolve()
INSTALL_PATH = f"{THIS_DIR}/home/.s3-backup"
ENV_VALUES = dotenv_values(".env")
YAML_DATA = {
    "amazon": {
        "aws_access_key_id": ENV_VALUES.get("aws_access_key_id"),
        "aws_secret_access_key": ENV_VALUES.get("aws_secret_access_key"),
        "bucket_name": ENV_VALUES.get("bucket_name"),
        "hosted_region": ENV_VALUES.get("hosted_region"),
        "folder_path": "/test",
    },
    "backups": {
        "restore_dir": f"{THIS_DIR}/home/restore",
        "sources_dir": f"{THIS_DIR}/home/source",
        "include_dirs": [None],
        "exclude_dirs": [f"{THIS_DIR}/home/source/melville"],
    },
    "options": {
        "weeks_until_log_purge": 5,
        "weeks_until_full_backup": 4,
        "passphrase": "cyGficReKVrd.R4drrqvb*-Y",
    },
}
