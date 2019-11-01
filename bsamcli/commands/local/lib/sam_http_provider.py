# 一个function下可以有多个HTTP event，分别去创建

"""Class that resolve HTTP event from a SAM Template"""

import logging
from collections import namedtuple

from six import string_types

from bsamcli.commands.local.lib.swagger.parser import SwaggerParser
from bsamcli.commands.local.lib.provider import EventSourceProvider, HttpEvent
from bsamcli.commands.local.lib.sam_base_provider import SamBaseProvider
from bsamcli.commands.local.lib.swagger.reader import SamSwaggerReader
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)


class SamHttpProvider(EventSourceProvider):

    _SERVERLESS_FUNCTION = "BCE::Serverless::Function"
    _TYPE = "Type"

    _FUNCTION_EVENT_TYPE_HTTP = "HTTP"
    _FUNCTION_EVENT = "Events"

    _RESOURCE_PATH = "ResourcePath"
    _METHOD = "Method"
    _AUTH_THPE = "AuthType"

    _ANY_AUTH_TYPE = ["iam", "anonymous"]
    _ANY_METHOD_TYPE = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]

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

        self.http_events = self._extract_http(self.resources)

        LOG.debug("%d HTTP events found in the template", len(self.http_events))

    # def get_all(self):
    #     """
    #     Yields all the Http events in the SAM Template.

    #     :yields Http : namedtuple containing the Api information
    #     """

    #     for event in self.http_events:
    #         yield event

    def get(self, logical_id):
        return self.http_events.get(logical_id)

    def _extract_http(self, resources):
        """
        Extract all Implicit Apis (Apis defined through Serverless Function with an Api Event

        :param dict resources: Dictionary of SAM/CloudFormation resources
        :return: Dict. key: logical_id, value: list of http events
        """

        # Some properties like BinaryMediaTypes, Cors are set once on the resource but need to be applied to each API.
        # For Implicit APIs, which are defined on the Function resource, these properties
        # are defined on a AWS::Serverless::Api resource with logical ID "ServerlessRestApi". Therefore, no matter
        # if it is an implicit API or an explicit API, there is a corresponding resource of type AWS::Serverless::Api
        # that contains these additional configurations.
        #
        # We use this assumption in the following loop to collect information from resources of type
        # AWS::Serverless::Api. We also extract API from Serverless::Function resource and add them to the
        # corresponding Serverless::Api resource. This is all done using the ``collector``.

        result = {}

        for logical_id, resource in resources.items():
            resource_type = resource.get(SamHttpProvider._TYPE)

            if resource_type == SamHttpProvider._SERVERLESS_FUNCTION:
                result[logical_id] = self._extract_http_from_function(logical_id, resource)

        return result

    @staticmethod
    def _extract_http_from_function(logical_id, function_resource):
        """
        Fetches a list of APIs configured for this SAM Function resource.

        Parameters
        ----------
        logical_id : str
            Logical ID of the resource

        function_resource : dict
            Contents of the function resource including its properties
        """

        http_events = []
        count = 0

        resource_properties = function_resource.get("Properties", {})
        serverless_function_events = resource_properties.get(SamHttpProvider._FUNCTION_EVENT, {})

        for _, event in serverless_function_events.items():
            if SamHttpProvider._FUNCTION_EVENT_TYPE_HTTP == event.get(SamHttpProvider._TYPE):
                http_events.append(SamHttpProvider._convert_event_http(logical_id, event.get("Properties")))
                count += 1

        LOG.debug("Found '%d' Http Events in Serverless function with name '%s'", count, logical_id)
        return http_events

    @staticmethod
    def _convert_event_http(logical_id, event_properties):
        """
        Converts a BCE::Serverless::Function's Event Property to an Api configuration usable by the provider.

        :param str logical_id: Logical Id of the AWS::Serverless::Function
        :param dict event_properties: Dictionary of the Event's Property
        :return tuple: tuple of API resource name and Api namedTuple
        """
        methods = event_properties.get(SamHttpProvider._METHOD)
        resource_path = event_properties.get(SamHttpProvider._RESOURCE_PATH)
        auth_type = event_properties.get(SamHttpProvider._AUTH_THPE)

        if isinstance(methods, str):
            methods = [methods]

        if methods is None or resource_path is None:
            raise InvalidSamDocumentException("Method or ResourePath of HTTP Event is empty")

        methods = [m.upper() for m in methods]
        for m in methods:
            if m not in SamHttpProvider._ANY_METHOD_TYPE:
                raise InvalidSamDocumentException("Invalid Http Method: {}".format(methods))
        methods = ",".join(methods)

        if auth_type not in SamHttpProvider._ANY_AUTH_TYPE:
            raise InvalidSamDocumentException("Invalid Http AuthType: {}".format(auth_type))

        return HttpEvent(resource_path=resource_path, method=methods,
            auth_type=auth_type, function_name=logical_id)

    def deploy(self, cfc_client, func_config):
        http_events = self.get(func_config.FunctionName)

        for event in http_events:
            data = {
                "ResourcePath": event.resource_path,
                "Method": event.method,
                "AuthType": event.auth_type
            }

            try:
                event_info = "<ResourcePath: %s, Method: %s, AuthType: %s>" % (data["ResourcePath"], data["Method"], data["AuthType"])

                cfc_client.create_trigger(func_config.FunctionBrn, "cfc-http-trigger/v1/CFCAPI", data)
                LOG.info("HTTP event source %s deploy succ!", event_info)

            except BaseException as e:
                LOG.info("HTTP event source %s deploy failed!", event_info)
                LOG.info("Error msg: %s", str(e))
