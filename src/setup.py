from setuptools import setup

setup(
    name="s3-backup",
    version="0.1.0",
    author="sum-rock",
    packages=["s3_backup", "s3_backup.tests"],
    scripts=["scripts/s3-backup"],
    description="Simplify your S3 backups!",
    install_requires=["pytest", "pyyaml", "duplicity", "boto"],
)
