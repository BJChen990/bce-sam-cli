"""
CLI command for "package" command
"""

import click

from bsamcli.cli.main import pass_context, common_options
from bsamcli.lib.samlib.cfc_command import execute_pkg_command


SHORT_HELP = "Package an CFC application."


# http://click.pocoo.org/5/api/#click.Context.ignore_unknown_options
@click.command("package", short_help=SHORT_HELP, context_settings={"ignore_unknown_options": True})
@click.option('--with-src', is_flag=True, default=False, help="Whether to package source code when runtime is Java8")
@common_options
@pass_context
def cli(ctx, with_src):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(with_src)  # pragma: no cover


def do_cli(with_src):
    # execute_command("package", args)
    execute_pkg_command("package", with_src)
