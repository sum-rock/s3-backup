# S3-Backup

Simplify your S3 Backups!

This is yet another lite layer on top of duplicity. The project sets some reasonable
defaults and lets you store your configurations in yaml files. No more complicated bash
called from crontab! Why choose this one particular duplicity abstraction? Glad you
asked, there are Yaml configs and GPG encryption backup by default. Is this unique? Not
particularly, but I had fun writing it.

## Dependencies

1. duplicity
2. GPG

## Installing Duplicity on CentOS/Alma/Rocky

This is tested on RockyLinux 8.5

### EPEL Repositories

You'll need Extra Packages for Enterprise Linux for a bunch of different dependencies.

```bash
dnf upgrade --refresh -y
dnf install epel-release
```

### Duplicity

```bash
sudo dnf install python3.9 duplicity
sudo pip3 install boto
```

## Install s3-backup

Still as root

```bash
cd ~
git clone https://github.com/sum-rock/s3-backup.git
cd s3-backup
pip3.9 install .
cd ../
rm -rf s3-backup 
```

## Usage

### Initializing

Before you are able to to do anything you'll need to initialize s3-backup. All commands
need to be run as root.

The path option within the init command specifies where the profile data and logs will
be saved.

```bash
s3-backup init ~
```

### Profiles

Once initialized, profiles can be created, edited and removed through the `profile`
subcommand. The name option within the profile subcommand is used to specify the profile
name.

```bash
s3-backup profile [create, edit, remove] <profile-name>
```

### Execute

Profiles are able to be used to execute backup and restore commands. (These parse to
standard duplicity commands.) The name argument within the profile subcommand is used to
specify the profile to action on.

```bash
s3-backup execute [backup, restore] <profile-name>
```

### Collection

The collection subcommand is used to perform several collection management actions. Again,
the name argument is used to specify the profile of the collection being managed.

```bash
s3-backup collection [status, list-files, clean, prune] <profile-name>
```
