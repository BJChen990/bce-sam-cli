"""
CLI command for "local install" command
"""

import logging
import click

from bsamcli.cli.main import pass_context, common_options as cli_framework_options
from bsamcli.commands.local.cli_common.options import template_click_option
from bsamcli.commands.exceptions import UserException
from bsamcli.commands.local.cli_common.options import template_common_option as template_option
from bsamcli.commands.local.cli_common.invoke_context import InvokeContext
from bsamcli.local.lambdafn.exceptions import FunctionNotFound
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)


HELP_TEXT = """
You can use this command to install dependency for your nodejs and python function.
In addition, this command will compile and package java function for you, thus avoiding
inconsistencies in the compilation environment.\n
"""

@click.command("install", help=HELP_TEXT, short_help="Install dependency for CFC local function, and package for Java function")
@template_option
@cli_framework_options
@click.argument('function_identifier', required=False)
@pass_context
def cli(ctx, function_identifier, template):

    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(ctx, function_identifier, template)  # pragma: no cover


def do_cli(ctx, function_identifier, template):
    """
    Implementation of the ``cli`` method, just separated out for unit testing purposes
    """

    LOG.debug("local install command is called")

    try:
        with InvokeContext(template_file=template,
                            function_identifier=function_identifier,
                            skip_pull_image=True) as context:
            # reuse invoke to enter the container, but don't actually invoke user function
            context.local_lambda_runner.invoke(context.function_name,
                                               event=None,
                                               is_installing=True,
                                               stdout=context.stdout,
                                               stderr=context.stderr)

    except FunctionNotFound:
        raise UserException("Function {} not found in template".format(function_identifier))
    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))
