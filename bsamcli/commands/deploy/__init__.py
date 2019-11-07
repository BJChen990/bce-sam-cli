"""
CLI command for "deploy" command
"""

import click

from bsamcli.cli.main import pass_context, common_options
from bsamcli.lib.samlib.cfc_command import execute_deploy_command
from bsamcli.lib.samlib.cfc_deploy_conf import SUPPORTED_REGION


SHORT_HELP = "Deploy an CFC application"

@click.command("deploy", short_help=SHORT_HELP, context_settings={"ignore_unknown_options": True})
@click.option("--region", type=click.Choice(SUPPORTED_REGION), help="Specify the region you want to deploy")
@common_options
@pass_context
def cli(ctx, region):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(region)  # pragma: no cover


def do_cli(region):
    # execute_command("deploy", args)
    execute_deploy_command("deploy", region=region)
