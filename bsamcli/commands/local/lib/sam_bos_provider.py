# 一个function下可以有多个bos event，分别去创建

"""Class that resolve BOS event from a SAM Template"""

import logging
from collections import namedtuple

from six import string_types

from bsamcli.commands.local.lib.swagger.parser import SwaggerParser
from bsamcli.commands.local.lib.provider import EventSourceProvider, BosEvent
from bsamcli.commands.local.lib.sam_base_provider import SamBaseProvider
from bsamcli.commands.local.lib.swagger.reader import SamSwaggerReader
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)


class SamBosProvider(EventSourceProvider):

    _SERVERLESS_FUNCTION = "BCE::Serverless::Function"
    _TYPE = "Type"

    _FUNCTION_EVENT_TYPE_BOS = "BOS"
    _FUNCTION_EVENT = "Events"

    _BUCKET_NAME = "Bucket"
    _EVENT_TYPES = "EventTypes"
    _PREFIX = "Prefix"
    _SUFFIX = "Suffix"

    _ANY_EVENT_TYPE = ["PutObject",
                         "PostObject",
                         "AppendObject",
                         "CopyObject",
                         "CompleteMultipartUpload"]

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

        self.bos_events = self._extract_bos(self.resources)

        LOG.debug("%d BOS events found in the template", len(self.bos_events))

    # def get_all(self):
    #     """
    #     Yields all the Bos events in the SAM Template.

    #     :yields Bos : namedtuple containing the Api information
    #     """

    #     for event in self.bos_events:
    #         yield event

    def get(self, logical_id):
        return self.bos_events.get(logical_id)

    def _extract_bos(self, resources):
        """
        Extract all Implicit Apis (Apis defined through Serverless Function with an Api Event

        :param dict resources: Dictionary of SAM/CloudFormation resources
        :return: Dict. key: logical_id, value: list of bos events
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
            resource_type = resource.get(SamBosProvider._TYPE)

            if resource_type == SamBosProvider._SERVERLESS_FUNCTION:
                result[logical_id] = self._extract_bos_from_function(logical_id, resource)

        return result

    @staticmethod
    def _extract_bos_from_function(logical_id, function_resource):
        """
        Fetches a list of APIs configured for this SAM Function resource.

        Parameters
        ----------
        logical_id : str
            Logical ID of the resource

        function_resource : dict
            Contents of the function resource including its properties
        """

        bos_events = []
        count = 0

        resource_properties = function_resource.get("Properties", {})
        serverless_function_events = resource_properties.get(SamBosProvider._FUNCTION_EVENT, {})

        for _, event in serverless_function_events.items():
            if SamBosProvider._FUNCTION_EVENT_TYPE_BOS == event.get(SamBosProvider._TYPE):
                bos_events.append(SamBosProvider._convert_event_bos(logical_id, event.get("Properties")))
                count += 1

        LOG.debug("Found '%d' Bos Events in Serverless function with name '%s'", count, logical_id)
        return bos_events

    @staticmethod
    def _convert_event_bos(logical_id, event_properties):
        """
        Converts a BCE::Serverless::Function's Event Property to an Api configuration usable by the provider.

        :param str logical_id: Logical Id of the AWS::Serverless::Function
        :param dict event_properties: Dictionary of the Event's Property
        :return tuple: tuple of API resource name and Api namedTuple
        """
        prefix = event_properties.get(SamBosProvider._PREFIX, "")
        suffix = event_properties.get(SamBosProvider._SUFFIX, "")
        bucket_name = event_properties.get(SamBosProvider._BUCKET_NAME)
        event_types = event_properties.get(SamBosProvider._EVENT_TYPES)

        if isinstance(event_types, str):
            event_types = [event_types]

        if event_types is None or bucket_name is None:
            raise InvalidSamDocumentException("Bucket or Event_types of BOS Event is empty")

        for event_type in event_types:
            if event_type not in SamBosProvider._ANY_EVENT_TYPE:
                raise InvalidSamDocumentException("Invalid event_type: {}".format(event_type))

        return BosEvent(prefix=prefix, suffix=suffix, bucket=bucket_name,
            event_types=event_types, function_name=logical_id)

    def deploy(self, cfc_client, func_config):
        bos_events = self.get(func_config.FunctionName)

        for event in bos_events:
            data = {
                "EventType": event.event_types,
                "Status": "enabled",
                "Prefix": event.prefix,
                "Suffix": event.suffix
            }

            try:
                event_info = "<EventTypes: %s, Prefix: %s, Suffix: %s>" % (', '.join(data["EventType"]), data["Prefix"], data["Suffix"])

                cfc_client.create_trigger(func_config.FunctionBrn, "bos/" + event.bucket, data)
                LOG.info("BOS event source %s deploy succ!", event_info)

            except BaseException as e:
                LOG.info("BOS event source %s deploy failed!", event_info)
                LOG.info("Error msg: %s", str(e))
