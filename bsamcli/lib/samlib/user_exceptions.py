"""
Class containing error conditions that are exposed to the user.
"""

from bsamcli.commands.exceptions import UserException


class DeployContextException(UserException):
    """
    Something went wrong when deploying the function
    """
    pass


class InvalidSamTemplateException(UserException):
    """
    The template provided was invalid
    """
    pass


class SamTemplateNotFoundException(UserException):
    """
    The SAM Template provided could not be found
    """
    pass

