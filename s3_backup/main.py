from pathlib import Path

import click

from commands import (
    Backup,
    Collection,
    Initialize,
    ManageProfiles,
    Restore,
)
from context import SettingsConstructor


@click.group()
def cli():
    pass


@cli.command(help="Initialize the CLI, required before executing or managing")
@click.argument("path")
def init(path):
    if not path:
        path = str(Path.home().resolve())

    Initialize().do_initialize(path)
    click.echo("success")


@click.group(help="Execution commands, including backup and restore")
def execute():
    pass


@execute.command(help="Perform backup operation")
@click.option("--allow-source-mismatch", default=False, is_flag=True)
@click.argument("name")
def backup(allow_source_mismatch, name):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        b = Backup(settings.get_profile())

        if allow_source_mismatch:
            b.do_backup(opts={"--allow-source-mismatch": ""})
        else:
            b.do_backup()

    click.echo("success")


@execute.command(help="Perform restore operation")
@click.argument("name")
def restore(name):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        Restore(settings.get_profile()).do_restore()

    click.echo("success")


@click.group(help="Output collection information")
def collection():
    pass


@collection.command(help="Output collection status")
@click.argument("name")
def status(name):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        Collection(settings.get_profile()).get_collection_status()


@collection.command(help="Output a file list of files currently in the backup.")
@click.argument("name")
def list_files(name):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        Collection(settings.get_profile()).get_file_list()


@collection.command(help="Run the duplicity cleanup command for this profile.")
@click.argument("name")
def cleanup(name):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        Collection(settings.get_profile()).do_cleanup()


@collection.command(
    help="Removes all backups older than the count back of full backups."
)
@click.option(
    "--count",
    default=4,
    help="Count of full backups and associated incremental backups to keep.",
)
@click.argument("name")
def prune(name, count):
    settings = SettingsConstructor(profile_name=name)
    settings.verify_profile()

    with settings.get_context_klass()():
        Collection(settings.get_profile()).do_prune(count)


@click.group(help="Profile management commands, including add, remove, and edit")
def profile():
    pass


@profile.command(help="Create a new profile")
@click.argument("name")
def create(name):
    m = ManageProfiles()
    if not name:
        raise click.BadArgumentUsage("Must provide a name for your profile.")
    elif name in m.installed_profiles:
        raise click.BadArgumentUsage(
            "A profile with this name has already been created."
        )
    else:
        m.do_add(name)


@profile.command(help="Edit a profile")
@click.argument("name")
def edit(name):
    m = ManageProfiles()
    m.verify_profile(name)
    m.do_edit(name)


@profile.command(help="Edit a profile")
@click.argument("name")
def remove(name):
    m = ManageProfiles()
    m.verify_profile(name)
    m.do_remove(name)


if __name__ == "__main__":
    cli.add_command(execute)
    cli.add_command(profile)
    cli.add_command(collection)
    cli()
