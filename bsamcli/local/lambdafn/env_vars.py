"""
Supplies the environment variables necessary to set up Local CFC runtime
"""

import uuid
import sys

class EnvironmentVariables(object):
    """
    Use this class to get the environment variables necessary to run the CFC function. It returns the BCE specific
    variables (credentials, regions, etc) along with any environment variables configured on the function.

    Customers define the name of the environment variables along with default values, if any, when creating the
    function. In order to test the function with different scenarios, customers can override values for some of the
    variables. This class supports three mechanisms of providing values to environment variables.
    If a variable is given a value through all the three mechanisms, then the value from higher priority will be used:

    Priority (Highest to Lowest):
        - Override Values - User specified these
        - Shell Environment Values - Came from the shell environment
        - Default Values - Hard coded values

    If a variable does *not* get a value from either of the above mechanisms, it is given a value of "" (empty string).
    If the value of a variable is an intrinsic function dict/list, then it is given a value of "" (empty string).

    If real bce Credentials were supplied, this class will expose them through appropriate environment variables.
    If not, this class will provide the following placeholder values to bce Credentials:
        region = "bj"
        key = "defaultkey"
        secret = "defaultsecret"
    """

    _BLANK_VALUE = ""
    _DEFAULT_BCE_CREDS = {
        "region": "bj",
        "key": "defaultkey",
        "secret": "defaultsecret"
    }

    def __init__(self,
                 function_memory=None,
                 function_timeout=None,
                 function_handler=None,
                 variables=None,
                 shell_env_values=None,
                 override_values=None,
                 bce_creds=None):
        """
        Initializes this class. It takes in two sets of properties:
            a) (Required) Function information
            b) (Optional) Environment variable configured on the function

        :param integer function_memory: Memory size of the function in megabytes
        :param integer function_timeout: Function's timeout in seconds
        :param string function_handler: Handler of the function
        :param dict variables: Optional. Dict whose key is the environment variable names and value is the default
            values for the variable.
        :param dict shell_env_values: Optional. Dict containing values for the variables grabbed from the shell's
            environment.
        :param dict override_values: Optional. Dict containing values for the variables that will override the values
            from ``default_values`` and ``shell_env_values``.
        :param dict bce_creds: Optional. Dictionary containing bce credentials passed to the CFC runtime through
            environment variables. It should contain "key", "secret", "region" and optional "sessiontoken" keys
        """

        self._function = {
            "memory": function_memory,
            "timeout": function_timeout,
            "handler": function_handler
        }

        self.variables = variables or {}
        self.shell_env_values = shell_env_values or {}
        self.override_values = override_values or {}
        self.bce_creds = bce_creds or {}

    def resolve(self):
        """
        Resolves the values from different sources and returns a dict of environment variables to use when running
        the function locally.

        :return dict: Dict where key is the variable name and value is the value of the variable. Both key and values
            are strings
        """

        # BCE_* variables must always be passed to the function, but user has the choice to override them
        result = self._get_bce_variables()

        # Default value for the variable gets lowest priority
        for name, value in self.variables.items():

            # Shell environment values, second priority
            if name in self.shell_env_values:
                value = self.shell_env_values[name]

            # Overridden values, highest priority
            if name in self.override_values:
                value = self.override_values[name]

            # Any value must be a string when passed to CFC runtime.
            # Runtime expects a Map<String, String> for environment variables
            result[name] = self._stringify_value(value)

        return result

    def add_cfc_event_body(self, value):
        """
        Adds the value of BCE_CFC_EVENT_BODY environment variable.
        """
        self.variables["BCE_EVENT_BODY"] = value

    def add_install_flag(self):
        self.variables["IS_INSTALLING"] = "True"

    @property
    def timeout(self):
        return self._function["timeout"]

    @timeout.setter
    def timeout(self, value):
        self._function["timeout"] = value

    @property
    def memory(self):
        return self._function["memory"]

    @memory.setter
    def memory(self, value):
        self._function["memory"] = value

    @property
    def handler(self):
        return self._function["handler"]

    @handler.setter
    def handler(self, value):
        self._function["handler"] = value

    def _get_bce_variables(self):
        """
        Returns the BCE specific environment variables that should be available in the CFC runtime.
        They are prefixed it "BCE_*".

        :return dict: Name and value of BCE environment variable
        """

        result = {
            # Variable that says this function is running in Local CFC
            "BCE_SAM_LOCAL": "true",

            # BCE Credentials - Use the input credentials or use the defaults

            "BCE_ACCESS_KEY_ID": self.bce_creds.get("key", self._DEFAULT_BCE_CREDS["key"]),

            "BCE_ACCESS_KEY_SECRET": self.bce_creds.get("secret", self._DEFAULT_BCE_CREDS["secret"]),

            "_HANDLER": self.handler,
            "_TIMEOUT": self.timeout,
            "_REQUEST_ID": str(uuid.uuid1())

            # Additional variables we don't fill in
            # "BCE_ACCOUNT_ID="
            # "BCE_CFC_FUNCTION_NAME=",
            # "BCE_CFC_FUNCTION_VERSION=",
        }

        # Session Token should be added **only** if the input creds have a token and the value is not empty.
        if self.bce_creds.get("token"):
            result["BCE_SESSION_TOKEN"] = self.bce_creds.get("token")

        return result

    def _stringify_value(self, value):
        """
        This method stringifies values of environment variables. If the value of the method is a list or dictionary,
        then this method will replace it with empty string. Values of environment variables in CFC must be a string.
        List or dictionary usually means they are intrinsic functions which have not been resolved.

        :param value: Value to stringify
        :return string: Stringified value
        """

        # List/dict/None values are replaced with a blank
        if isinstance(value, (dict, list, tuple)) or value is None:
            result = self._BLANK_VALUE

        # str(True) will output "True". To maintain backwards compatibility we need to output "true" or "false"
        elif value is True:
            result = "true"
        elif value is False:
            result = "false"

        # value is a scalar type like int, str which can be stringified
        # do not stringify unicode in Py2, Py3 str supports unicode
        elif sys.version_info.major > 2:
            result = str(value)
        elif not isinstance(value, unicode):  # noqa: F821 pylint: disable=undefined-variable
            result = str(value)
        else:
            result = value

        return result
