"""
Interaction of credential input
"""

import os
import configparser
import logging

from baidubce.auth.bce_credentials import BceCredentials
from bsamcli.commands.exceptions import UserException

default_config_location = os.path.expanduser('~') + os.sep + ".bce"
default_config_file = default_config_location + os.sep + "config"
default_credential_file = default_config_location + os.sep + "credentials"

DEFAULT_REGION = "bj"

CREDENTIAL_SECTION_NAME = "defaults"
CONFIG_SECTION_NAME = "defaults"
ACCESS_KEY_OPTION_NAME = "bce_access_key_id"
SECRET_KEY_OPTION_NAME = "bce_secret_access_key"
BCE_SESSION_TOKEN = "bce_session_token"

LOG = logging.getLogger(__name__)

def get_credentials():
    """
    get credential from default location
    """
    if not os.path.exists(default_credential_file):
        LOG.debug("credential file not found: %s does not exist, try execute 'sam config' later" % format(default_credential_file))
        return BceCredentials('test-ak', 'test-sk')
    #生成config对象
    safe_config_json = {ACCESS_KEY_OPTION_NAME: "", SECRET_KEY_OPTION_NAME: "", BCE_SESSION_TOKEN: ""}
    conf = configparser.SafeConfigParser(safe_config_json)
    #用config对象读取配置文件
    conf.read(default_credential_file)
    #指定section，option读取值
    ak = conf.get(CREDENTIAL_SECTION_NAME, ACCESS_KEY_OPTION_NAME)
    sk = conf.get(CREDENTIAL_SECTION_NAME, SECRET_KEY_OPTION_NAME)
    return BceCredentials(ak, sk)


def get_region():
    """
    get region from default configfile
    """
    if not os.path.exists(default_credential_file):
        LOG.debug("config file not found : {} does not exist, try 'sam config' later".format(default_config_file))
        return DEFAULT_REGION
    #生成config对象
    conf = configparser.SafeConfigParser({"region": DEFAULT_REGION})
    #用config对象读取配置文件
    conf.read(default_config_file)
    #指定section，option读取值
    return conf.get(CONFIG_SECTION_NAME, "region")

def init_conf_folder(config_folder):
    """
    Init conf folder and files
    """
    credential_path = config_folder + os.sep + 'credentials'
    config_path = config_folder + os.sep + 'config'
    if os.path.exists(config_folder):
        if os.path.isdir(config_folder):
            if not os.path.exists(credential_path):
                __init_credential_config(credential_path)
            if not os.path.exists(config_path):
                __init_cfc_config(config_path)
        else:
            raise Exception("Cannot create directory '%s': File exists. please check..."
                            % config_folder)
    else:
        os.mkdir(config_folder)
        __init_credential_config(credential_path)
        __init_cfc_config(config_path)

def config_interactive(config_folder, ak="", sk="", region=""):
    if not config_folder:
        config_folder = default_config_location

    credential_path = config_folder + os.sep + 'credentials'
    config_path = config_folder + os.sep + 'config'

    if os.path.exists(credential_path):
        __set_credential_config(credential_path, ak, sk)

    if os.path.exists(config_path):
        __set_cfc_config(config_path, region)

    init_conf_folder(config_folder)
    __set_credential_config(credential_path, ak, sk)
    __set_cfc_config(config_path, region)


def __init_credential_config(credential_path):
    conf = configparser.SafeConfigParser()
    conf.read(open(credential_path, "w+"))
    conf.add_section(CREDENTIAL_SECTION_NAME)
    conf.set(CREDENTIAL_SECTION_NAME, ACCESS_KEY_OPTION_NAME, "")
    conf.set(CREDENTIAL_SECTION_NAME, SECRET_KEY_OPTION_NAME, "")
    conf.write(open(credential_path, "w"))


def __init_cfc_config(config_path):
    conf = configparser.SafeConfigParser()
    conf.read(open(config_path, "w+"))
    conf.add_section(CONFIG_SECTION_NAME)
    conf.set(CONFIG_SECTION_NAME, "region", DEFAULT_REGION)
    conf.write(open(config_path, "w"))


def __set_credential_config(credential_path, ak, sk):
    conf = configparser.SafeConfigParser()
    conf.read(credential_path)
    if CREDENTIAL_SECTION_NAME not in conf.sections():
        conf.add_section(CREDENTIAL_SECTION_NAME)
    conf.set(CREDENTIAL_SECTION_NAME, ACCESS_KEY_OPTION_NAME, ak)
    conf.set(CREDENTIAL_SECTION_NAME, SECRET_KEY_OPTION_NAME, sk)
    conf.write(open(credential_path, "w"))


def __set_cfc_config(config_path, region):
    conf = configparser.SafeConfigParser()
    conf.read(config_path)
    if CONFIG_SECTION_NAME not in conf.sections():
        conf.add_section(CONFIG_SECTION_NAME)
    conf.set(CONFIG_SECTION_NAME, "region", region)
    conf.write(open(config_path, "w"))
