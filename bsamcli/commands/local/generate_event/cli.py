"""
Sets up the cli for generate-event
"""

import click

from bsamcli.cli.main import pass_context
from bsamcli.commands.local.generate_event.event_generation import GenerateEventCommand

HELP_TEXT = """
You can use this command to generate sample payloads from different event sources
such as BOS, DuerOS, and HTTP trigger. These payloads contain the information that the
event sources send to your CFC functions.\n
\b
Generate the event that BOS sends to your CFC function when a new object is uploaded
$ bsam local generate-event bos put\n
\b
You can even customize the event by adding parameter flags. To find which flags apply to your command,
run:\n
$ bsam local generate-event bos put --help\n
Then you can add in those flags that you wish to customize using\n
$ bsam local generate-event bos put --bucket <bucket> --object <object>\n
\b
After you generate a sample event, you can use it to test your CFC function locally
$ bsam local generate-event bos put --bucket <bucket> --object <object> | bsam local invoke <function logical id>
"""


@click.command(name="generate-event", cls=GenerateEventCommand, help=HELP_TEXT)
@pass_context
def cli(self):
    """
    Generate an event for one of the services listed below:
    """
    pass  # pragma: no cover
