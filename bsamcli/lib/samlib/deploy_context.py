"""
Template.yaml parser
"""

import json
import sys
import os
import yaml

from bsamcli.yamlhelper import yaml_parse
from bsamcli.lib.samlib.user_exceptions import DeployContextException
from bsamcli.local.lambdafn.exceptions import FunctionNotFound
from bsamcli.commands.local.lib.sam_function_provider import SamFunctionProvider
from bsamcli.commands.local.lib.sam_bos_provider import SamBosProvider
from bsamcli.commands.local.lib.sam_dueros_provider import SamDuerosProvider
from bsamcli.commands.local.lib.sam_http_provider import SamHttpProvider

# This is an attempt to do a controlled import. pathlib is in the
# Python standard library starting at 3.4. This will import pathlib2,
# which is a backport of the Python Standard Library pathlib
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class DeployContext(object):

    def __init__(self,
                 template_file,
                 function_identifier=None,
                 env_vars_file=None,
                 log_file=None,
                 ):
        self._template_file = template_file
        self._function_identifier = function_identifier
        self._env_vars_file = env_vars_file
        self._log_file = log_file

        self._template_dict = None
        self._function_provider = None
        self._env_vars_value = None
        self._log_file_handle = None

        self._event_source_provider = None

    def __enter__(self):
        # Grab template from file and create a provider
        self._template_dict = self._get_template_data(self._template_file)
        self._function_provider = SamFunctionProvider(self._template_dict)

        self._event_source_provider = [
            SamBosProvider(self._template_dict),
            SamDuerosProvider(self._template_dict),
            SamHttpProvider(self._template_dict),
        ]

        self._env_vars_value = self._get_env_vars_value(self._env_vars_file)
        self._log_file_handle = self._setup_log_file(self._log_file)

        return self

    def __exit__(self, *args):
        """
        Cleanup any necessary opened files
        """

        if self._log_file_handle:
            self._log_file_handle.close()
            self._log_file_handle = None

    @property
    def all_functions(self):
        all_functions = [f for f in self._function_provider.get_all()]
        if not all_functions:
            raise FunctionNotFound("Unable to find a single Function in the template file")
        return all_functions

    def deploy(self, cfc_client, func_config):
        for p in self._event_source_provider:
            p.deploy(cfc_client, func_config)

    @property
    def function_name(self):
        """
        Returns name of the function to invoke. If no function identifier is provided, this method will return name of
        the only function from the template

        :return string: Name of the function
        :raises InvokeContextException: If function identifier is not provided
        """
        if self._function_identifier:
            return self._function_identifier

        # Function Identifier is *not* provided. If there is only one function in the template,
        # default to it.

        all_functions = [f for f in self._function_provider.get_all()]
        if len(all_functions) == 1:
            return all_functions[0].name

        # Get all the available function names to print helpful exception message
        all_function_names = [f.name for f in all_functions]

        # There are more functions in the template, and function identifier is not provided, hence raise.
        raise DeployContextException("You must provide a function identifier (function's Logical ID in the template). "
                                     "Possible options in your template: {}".format(all_function_names))

    @property
    def stdout(self):
        """
        Returns a stdout stream to output Lambda function logs to

        :return File like object: Stream where the output of the function is sent to
        """
        if self._log_file_handle:
            return self._log_file_handle

        # We write all of the data to stdout with bytes, typically io.BytesIO. stdout in Python2
        # accepts bytes but Python3 does not. This is due to a type change on the attribute. To keep
        # this consistent, we leave Python2 the same and get the .buffer attribute on stdout in Python3
        byte_stdout = sys.stdout

        if sys.version_info.major > 2:
            byte_stdout = sys.stdout.buffer  # pylint: disable=no-member

        return byte_stdout

    @property
    def stderr(self):
        """
        Returns stderr stream to output Lambda function errors to

        :return File like object: Stream where the stderr of the function is sent to
        """
        if self._log_file_handle:
            return self._log_file_handle

        # We write all of the data to stdout with bytes, typically io.BytesIO. stderr in Python2
        # accepts bytes but Python3 does not. This is due to a type change on the attribute. To keep
        # this consistent, we leave Python2 the same and get the .buffer attribute on stderr in Python3
        byte_stderr = sys.stderr

        if sys.version_info.major > 2:
            byte_stderr = sys.stderr.buffer  # pylint: disable=no-member

        return byte_stderr

    @property
    def template(self):
        """
        Returns the template data as dictionary

        :return dict: Template data
        """
        return self._template_dict

    def get_cwd(self):
        """
        Get the working directory. This is usually relative to the directory that contains the template. If a Docker
        volume location is specified, it takes preference

        All Lambda function code paths are resolved relative to this working directory

        :return string: Working directory
        """

        cwd = os.path.dirname(os.path.abspath(self._template_file))
        # if self._docker_volume_basedir:
        #     cwd = self._docker_volume_basedir

        return cwd

    @staticmethod
    def _get_template_data(template_file):
        """
        Read the template file, parse it as JSON/YAML and return the template as a dictionary.

        :param string template_file: Path to the template to read
        :return dict: Template data as a dictionary
        :raises InvokeContextException: If template file was not found or the data was not a JSON/YAML
        """

        if not os.path.exists(template_file):
            raise DeployContextException("Template file not found at {}".format(template_file))

        with open(template_file, 'r') as fp:
            try:
                return yaml_parse(fp.read())
            except (ValueError, yaml.YAMLError) as ex:
                raise DeployContextException("Failed to parse template: {}".format(str(ex)))

    @staticmethod
    def _get_env_vars_value(filename):
        """
        If the user provided a file containing values of environment variables, this method will read the file and
        return its value

        :param string filename: Path to file containing environment variable values
        :return dict: Value of environment variables, if provided. None otherwise
        :raises InvokeContextException: If the file was not found or not a valid JSON
        """
        if not filename:
            return None

        # Try to read the file and parse it as JSON
        try:

            with open(filename, 'r') as fp:
                return json.load(fp)

        except Exception as ex:
            raise DeployContextException("Could not read environment variables overrides from file {}: {}".format(
                                         filename,
                                         str(ex)))

    @staticmethod
    def _setup_log_file(log_file):
        """
        Open a log file if necessary and return the file handle. This will create a file if it does not exist

        :param string log_file: Path to a file where the logs should be written to
        :return: Handle to the opened log file, if necessary. None otherwise
        """
        if not log_file:
            return None

        return open(log_file, 'wb')
        