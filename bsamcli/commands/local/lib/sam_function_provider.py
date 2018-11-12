"""
Class that provides functions from a given SAM template
"""

import logging
import six

from .provider import FunctionProvider, Function
from .sam_base_provider import SamBaseProvider

LOG = logging.getLogger(__name__)


class SamFunctionProvider(FunctionProvider):
    """
    Fetches and returns CFC Functions from a SAM Template. The SAM template passed to this provider is assumed
    to be valid, normalized and a dictionary.

    It may or may not contain a function.
    """

    _SERVERLESS_FUNCTION = "BCE::Serverless::Function"
    _CFC_FUNCTION = "BCE::CFC::Function"
    _DEFAULT_CODEURI = "."

    def __init__(self, template_dict):
        """
        Initialize the class with SAM template data. The SAM template passed to this provider is assumed
        to be valid, normalized and a dictionary. It should be normalized by running all pre-processing
        before passing to this class. The process of normalization will remove structures like ``Globals``, resolve
        intrinsic functions etc.
        This class does not perform any syntactic validation of the template.

        After the class is initialized, any changes to the ``template_dict`` will not be reflected in here.
        You need to explicitly update the class with new template, if necessary.

        :param dict template_dict: SAM Template as a dictionary
        """

        self.template_dict = SamBaseProvider.get_template(template_dict)
        self.resources = self.template_dict.get("Resources", {})

        LOG.debug("%d resources found in the template", len(self.resources))

        # Store a map of function name to function information for quick reference
        self.functions = self._extract_functions(self.resources)

    def get(self, name):
        """
        Returns the function given name or LogicalId of the function. Every SAM resource has a logicalId, but it may
        also have a function name. This method searches only for LogicalID and returns the function that matches
        it.

        :param string name: Name of the function
        :return Function: namedtuple containing the Function information if function is found.
                          None, if function is not found
        :raises ValueError If name is not given
        """

        if not name:
            raise ValueError("Function name is required")

        return self.functions.get(name)

    def get_all(self):
        """
        Yields all the Lambda functions available in the SAM Template.

        :yields Function: namedtuple containing the function information
        """

        for _, function in self.functions.items():
            yield function

    @staticmethod
    def _extract_functions(resources):
        """
        Extracts and returns function information from the given dictionary of SAM/CloudFormation resources. This
        method supports functions defined with AWS::Serverless::Function and AWS::Lambda::Function

        :param dict resources: Dictionary of SAM/CloudFormation resources
        :return dict(string : samcli.commands.local.lib.provider.Function): Dictionary of function LogicalId to the
            Function configuration object
        """

        result = {}

        for name, resource in resources.items():

            resource_type = resource.get("Type")
            resource_properties = resource.get("Properties", {})

            if resource_type == SamFunctionProvider._SERVERLESS_FUNCTION:
                result[name] = SamFunctionProvider._convert_sam_function_resource(name, resource_properties)

            # We don't care about other resource types. Just ignore them

        return result

    @staticmethod
    def _convert_sam_function_resource(name, resource_properties):
        """
        Converts a BCE::Serverless::Function resource to a Function configuration usable by the provider.

        :param string name: LogicalID of the resource NOTE: This is *not* the function name because not all functions
            declare a name
        :param dict resource_properties: Properties of this resource
        :return samcli.commands.local.lib.provider.Function: Function configuration
        """

        codeuri = resource_properties.get("CodeUri", SamFunctionProvider._DEFAULT_CODEURI)

        # CodeUri can be a dictionary of BOS Bucket/Key or a BOS URI, neither of which are supported
        # TODO 支持将CodeUri改为符合BOS的格式
        if isinstance(codeuri, dict) or \
                (isinstance(codeuri, six.string_types) and codeuri.startswith("bos://")):

            codeuri = SamFunctionProvider._DEFAULT_CODEURI
            LOG.warning("CFC function '%s' has specified BOS location for CodeUri which is unsupported. "
                        "Using default value of '%s' instead", name, codeuri)

        LOG.debug("Found CFC function with name='%s' and CodeUri='%s'", name, codeuri)

        return Function(
            name=name,
            runtime=resource_properties.get("Runtime"),
            memory=resource_properties.get("MemorySize"),
            timeout=resource_properties.get("Timeout"),
            handler=resource_properties.get("Handler"),
            description=resource_properties.get("Description"),
            codeuri=codeuri,
            environment=resource_properties.get("Environment"),
            rolearn=resource_properties.get("Role")
        )
