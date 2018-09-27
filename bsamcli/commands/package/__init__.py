"""
CLI command for "package" command
"""

import click

from bsamcli.cli.main import pass_context, common_options
from bsamcli.lib.samlib.cfc_command import execute_pkg_command


SHORT_HELP = "Package an CFC application."


@click.command("package", short_help=SHORT_HELP, context_settings={"ignore_unknown_options": True})#http://click.pocoo.org/5/api/#click.Context.ignore_unknown_options
# @click.argument("args", nargs=-1, type=click.UNPROCESSED)
@common_options
@pass_context
def cli(ctx):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli()  # pragma: no cover


def do_cli():
    # execute_command("package", args)
    execute_pkg_command("package")
