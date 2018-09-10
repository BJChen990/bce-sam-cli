import logging
import yaml
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

from samcli.yamlhelper import yaml_parse
from samcli.lib.samlib.cfc_credential_helper import get_credentials
from user_exceptions import DeployContextException

# HOST = 'http://cfc.bj.baidubce.com'
config_file = "deploy_config.yaml"

logger = logging.getLogger('baidubce.services.cfc.bosclient')
fh = logging.FileHandler('sample.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)


# def _get_creditial():
#     with open(config_file, 'r') as fp:
#         try:
#             return yaml_parse(fp.read())
#         except (ValueError, yaml.YAMLError) as ex:
#             raise DeployContextException("Failed to parse yml: {}".format(str(ex)))


def get_config():
    HOST = 'http://cfc.bj.baidubce.com'  
    return BceClientConfiguration(credentials=get_credentials(), endpoint=HOST)
