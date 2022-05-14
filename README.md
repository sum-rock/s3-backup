# S3-Backup

Simplify your S3 Backups!

This is yet another lite layer on top of duplicity sets some reasonable defaults and
lets you store your configurations in yaml files. No more complicated bash called from
crontab! Why choose this one particular duplicity abstraction? Glad you asked, there
are Yaml configs and GPG encryption backup by default. Is this unique? Not particularly.

## Dependencies

1. duplicity
2. GPG

## Installing Duplicity on CentOS/Alma/Rocky

This is tested on RockyLinux 8.5

### EPEL Repositories

Extra Packages for Enterprise Linux

```bash
dnf upgrade --refresh -y
dnf install epel-release
```

### System dependencies

```bash
dnf -y install \
    git wget gcc rsync librsync-devel \
    python3 python3-devel python3-pip python3-lockfile python3-paramiko python3-boto3
```

### Python dependencies

Install these as root. Ignore the pip complaints.

```bash
pip3 install \ 
    PyDrive \
    python-swiftclient \
    python-keystoneclient \
    fasteners \
    future \
    wheel
```

### Build duplicity from source

Because you're a boss (still as root).

```bash
cd ~
git clone https://gitlab.com/duplicity/duplicity.git
cd duplicity
python3 setup.py install
```
