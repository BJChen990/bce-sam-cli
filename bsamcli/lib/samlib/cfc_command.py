# coding=utf-8

import logging
import platform
import subprocess
import sys
import time
import base64
import os
import zipfile
import json

from baidubce.services.cfc.cfc_client import CfcClient
from baidubce.services.bos.bos_client import BosClient
from baidubce.exception import BceServerError
from baidubce.exception import BceHttpClientError
import cfc_deploy_conf

from bsamcli.commands.exceptions import UserException
from bsamcli.local.lambdafn.exceptions import FunctionNotFound
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException
from bsamcli.lib.samlib.cfc_credential_helper import get_region

from deploy_context import DeployContext
from user_exceptions import DeployContextException

LOG = logging.getLogger(__name__)
_TEMPLATE_OPTION_DEFAULT_VALUE = "template.yaml"

def execute_pkg_command(command):
    LOG.debug("%s command is called", command)
    try:
        with DeployContext(template_file=_TEMPLATE_OPTION_DEFAULT_VALUE,
                           function_identifier=None,
                           env_vars_file=None,
                           log_file=None,
                           ) as context:
            for f in context.all_functions:                
                _zip_up(f.codeuri, f.name)
    except FunctionNotFound:
        raise UserException("Function not found in template")
    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))


def execute_deploy_command(command, region=None):
    LOG.debug("%s command is called", command)
    try:
        with DeployContext(template_file=_TEMPLATE_OPTION_DEFAULT_VALUE,
                           function_identifier=None,
                           env_vars_file=None,
                           log_file=None,
                           ) as context:
            for f in context.all_functions:                                
                _do_deploy(context, f, region)

    except FunctionNotFound:
        raise UserException("Function not found in template")
    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))

def _do_deploy(context, function, region):
    # create a cfc client
    cfc_client = CfcClient(cfc_deploy_conf.get_config(region))
    existed = _check_if_exist(cfc_client, function.name)
    if existed:
        _update_function(cfc_client, function)
    else:
        _create_function(cfc_client, function)
        _create_event_source(cfc_client, function, context)
    LOG.info("deploy done.")


def _check_if_exist(cfc_client, function_name):
    try:
        get_function_response = cfc_client.get_function(function_name)
        LOG.debug("[Sample CFC] get_function response:%s", get_function_response)
    except (BceServerError,BceHttpClientError) as e: # TODO 区分一下具体的异常，因为可能是响应超时,input out put 一致
        return False
    
    # if (get_function_response.FunctionName == None or get_function_response.FunctionName != function_name):
        # return False

    return True


def _create_function(cfc_client, function):
    # create a cfc function
    function_name = function.name
    base64_file = _get_function_base64_file(function_name)
    user_memorysize = function.memory or 128
    user_timeout = function.timeout or 3
    user_runtime = _deal_with_func_runtime(function.runtime)
    user_region = get_region()
    
    try:
        create_response = cfc_client.create_function(function_name,
                                                 description=function.description or "cfc function from bsam cli",
                                                 handler=function.handler,
                                                 memory_size=user_memorysize,
                                                 environment=function.environment.get("Variables", None),
                                                 region=user_region,
                                                 zip_file=base64_file,
                                                 publish=False,
                                                 run_time=user_runtime,
                                                 timeout=user_timeout,
                                                 dry_run=False)  
        LOG.debug("[Sample CFC] create_response:%s", create_response)
        LOG.info("Function Create Response: %s", str(create_response))

    except(BceServerError,BceHttpClientError) as e:
        if e.last_error.message == "Forbidden":
            LOG.info("Probably invalid AK/SK , check out ~/.bce/credential to find out...")
        else:
            raise UserException(str(e))  


def _update_function(cfc_client, function):
    # update function code and configuration
    function_name = function.name
    base64_file = _get_function_base64_file(function_name)
    try:
        update_function_code_response = cfc_client.update_function_code(function.name,
                                                                    zip_file=base64_file)        
        LOG.info("Function Update Response: %s\n", str(update_function_code_response))

        update_func_config_response = cfc_client.update_function_configuration(function.name,
                                            environment=function.environment.get("Variables", None),
                                            handler=function.handler,
                                            run_time=_deal_with_func_runtime(function.runtime),
                                            timeout=function.timeout,
                                            description=function.description)

        LOG.info("Function Configuration Update Response: %s", str(update_func_config_response))


    except(BceServerError,BceHttpClientError) as e:
        if e.last_error.message == "Forbidden":
            LOG.info("Probably invalid AK/SK , check out ~/.bce/credential to find out...")
        else:
            raise UserException(str(e))


def _get_function_base64_file(function_name):
    zipfile_name = function_name + '.zip'
    if not os.path.exists(zipfile_name):
            raise DeployContextException("Zip file not found : {}".format(zipfile_name))

    with open(zipfile_name, 'r') as fp:
        try:
            return base64.b64encode(fp.read())
        except ValueError as ex:
            raise DeployContextException("Failed to convert zipfile to base64: {}".format(str(ex)))


def _zip_up(code_uri, zipfile_name):
    if code_uri is None:
        raise DeployContextException("Missing the file or the directory to zip up : {} is not valid".format(code_uri))
    
    zipfile_name = zipfile_name + '.zip'
    z = zipfile.ZipFile(zipfile_name, 'w', zipfile.ZIP_DEFLATED)
    
    if os.path.isfile(code_uri):
        z.write(code_uri, os.path.basename(code_uri))
    else:
        for dirpath, dirnames, filenames in os.walk(code_uri):
            fpath = dirpath.replace(code_uri, '') #这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ''
            for filename in filenames:
                z.write(os.path.join(dirpath, filename), fpath+filename)
    
    LOG.info('%s zip suceeded!', zipfile_name)
    z.close()
    
def _deal_with_func_runtime(function_runtime):
    if function_runtime in ('python','python2','python2.7'):
        return 'python2'
    elif function_runtime in ('nodejs8','nodejs8.5'):
        return 'nodejs8.5'
    elif function_runtime in ('java','java8'):
        return 'java8'
    else:
        raise UserException("Function runtime not supported")


def _create_event_source(cfc_client, function, context):    
    func_config = cfc_client.get_function_configuration(function.name)
    LOG.debug("get function ret is: %s", func_config)
    
    try:
        context.deploy(cfc_client, func_config)
    except(BceServerError, BceHttpClientError) as e:
        raise UserException(str(e))
    