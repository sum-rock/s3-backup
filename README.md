# S3-Backup

Simplify your S3 Backups!

This light layer on top of duplicity sets some reasonable defaults and lets you store
your configurations in yaml files. No more complicated bash called from crontab!

## Building the RPM

Start by building the python package from the `src` directory.

```unix
(.venv)$ python setup.py sdist
```
