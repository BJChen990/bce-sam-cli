# coding=utf-8

import logging

from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

from bsamcli.yamlhelper import yaml_parse
from bsamcli.lib.samlib.cfc_credential_helper import get_credentials, get_region


LOG = logging.getLogger(__name__)

SUPPORTED_REGION = ["bj", "su", "gz"]
endpointMap = {
    "bj": "http://cfc.bj.baidubce.com",
    "gz": "http://cfc.gz.baidubce.com",
    "su": "http://cfc.su.baidubce.com",
}

def get_config(region):
    region = region or get_region()
    if region is None:
        LOG.info("using default region: bj")
        region = "bj"
    elif region not in SUPPORTED_REGION:
        LOG.info("unsupported region: %s", region)
     
    return BceClientConfiguration(credentials=get_credentials(), endpoint=endpointMap.get(region))
