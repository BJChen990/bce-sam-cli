# 一个function下可以有多个bos event，分别去创建

"""Class that resolve DuerOS event from a SAM Template"""

import logging
from collections import namedtuple

from six import string_types

from bsamcli.commands.local.lib.swagger.parser import SwaggerParser
from bsamcli.commands.local.lib.provider import EventSourceProvider, DuerosEvent
from bsamcli.commands.local.lib.sam_base_provider import SamBaseProvider
from bsamcli.commands.local.lib.swagger.reader import SamSwaggerReader
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)


class SamDuerosProvider(EventSourceProvider):

    _SERVERLESS_FUNCTION = "BCE::Serverless::Function"
    _TYPE = "Type"

    _FUNCTION_EVENT_TYPE_DUEROS = "DuerOS"
    _FUNCTION_EVENT = "Events"

    def __init__(self, template_dict, cwd=None):
        """
        Initialize the class with SAM template data. The template_dict (SAM Templated) is assumed
        to be valid, normalized and a dictionary. template_dict should be normalized by running any and all
        pre-processing before passing to this class.
        This class does not perform any syntactic validation of the template.

        After the class is initialized, changes to ``template_dict`` will not be reflected in here.
        You will need to explicitly update the class with new template, if necessary.

        Parameters
        ----------
        template_dict : dict
            SAM Template as a dictionary
        cwd : str
            Optional working directory with respect to which we will resolve relative path to Swagger file
        """

        self.template_dict = SamBaseProvider.get_template(template_dict)
        self.resources = self.template_dict.get("Resources", {})

        LOG.debug("%d resources found in the template", len(self.resources))

        self.cwd = cwd

        self.dueros_events = self._extract_dueros(self.resources)

    # def get_all(self):
    #     """
    #     Yields all the Bos events in the SAM Template.

    #     :yields Bos : namedtuple containing the Api information
    #     """

    #     for event in self.bos_events:
    #         yield event

    def get(self, logical_id):
        return self.dueros_events.get(logical_id)

    def _extract_dueros(self, resources):
        """
        Extract all Implicit Apis (Apis defined through Serverless Function with an Api Event

        :param dict resources: Dictionary of SAM/CloudFormation resources
        :return: Dict. key: logical_id, value: list of bos events
        """

        result = {}

        for logical_id, resource in resources.items():
            resource_type = resource.get(SamDuerosProvider._TYPE)

            if resource_type == SamDuerosProvider._SERVERLESS_FUNCTION:
                if self._extract_dueros_from_function(logical_id, resource) is True:
                    result[logical_id] = DuerosEvent(function_name=logical_id)

        return result

    @staticmethod
    def _extract_dueros_from_function(logical_id, function_resource):
        """
        Fetches a list of APIs configured for this SAM Function resource.

        Parameters
        ----------
        logical_id : str
            Logical ID of the resource

        function_resource : dict
            Contents of the function resource including its properties
        """
        count = 0

        resource_properties = function_resource.get("Properties", {})
        serverless_function_events = resource_properties.get(SamDuerosProvider._FUNCTION_EVENT, {})

        for _, event in serverless_function_events.items():
            if SamDuerosProvider._FUNCTION_EVENT_TYPE_DUEROS == event.get(SamDuerosProvider._TYPE):
                LOG.debug("Found Dueros Events in Serverless function with name '%s'", logical_id)
                count += 1

        if count > 1:
            raise ValueError('A function can only have one DUEROS event source.')

        return count == 1

    def deploy(self, cfc_client, func_config):
        dueros_events = self.get(func_config.FunctionName)
        if dueros_events is not None:
            try:
                cfc_client.create_trigger(func_config.FunctionBrn, "dueros")
                LOG.info("Dueros event source deploy succ!")
            except BaseException as e:
                LOG.info("Dueros event source deploy failed!")
                LOG.info("Error msg: %s", str(e))
