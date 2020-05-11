"""
BCE configuration for deployment
"""

import logging

from baidubce.auth.bce_credentials import BceCredentials

from bsamcli.lib.samlib.user_exceptions import DeployContextException
from bsamcli.yamlhelper import yaml_parse
from bsamcli.lib.samlib.cfc_credential_helper import get_credentials, get_region

LOG = logging.getLogger(__name__)

SUPPORTED_REGION = ["bj", "su", "gz"]
endpointMap = {
    "bj": "http://cfc.bj.baidubce.com",
    "gz": "http://cfc.gz.baidubce.com",
    "su": "http://cfc.su.baidubce.com",
}

def get_region_endpoint(region):
    region = region or get_region()
    if region is None:
        LOG.info("using default region: bj")
        region = "bj"
    elif region not in SUPPORTED_REGION:
        raise DeployContextException("Region is not supported: {}".format(region))

    return endpointMap.get(region)
