# -*- coding: utf-8 -*-
"""
Init command to scaffold a project app from a template
"""
import logging
import click

from bsamcli.cli.main import pass_context, common_options
from bsamcli.commands.exceptions import UserException
from bsamcli.lib.samlib import cfc_credential_helper

LOG = logging.getLogger(__name__)
SHORT_HELP = "Config the AK/SK and region for CFC"

@click.command("config", short_help=SHORT_HELP, context_settings=dict(help_option_names=[u'-h', u'--help']))
@click.option('-l', '--location', help="Configfile location, ~/.bce as default")
@click.option('--ak', prompt='BCE Access Key ID', help='Known as AK')
@click.option('--sk', prompt='BCE Secret Access Key', help='Known as SK')
@click.option('--region', prompt='BCE region', help='Known as REGION')
@common_options
@pass_context
def cli(ctx, location, ak, sk, region):
    # All logic must be implemented in the `do_cli` method. This helps ease unit tests
    do_cli(ctx, location, ak, sk, region)  # pragma: no cover


def do_cli(ctx, location, ak, sk, region):
    """
    Implementation of the ``cli`` method, just separated out for unit testing purposes
    """
    LOG.debug("Config command")
    click.secho("Configuring project's configs completed...", fg="green")
    cfc_credential_helper.config_interactive(location, ak, sk, region)

