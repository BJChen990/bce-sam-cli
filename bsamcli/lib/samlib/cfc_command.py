"""
Execution of package and deploy command
"""

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
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.exception import BceServerError
from baidubce.exception import BceHttpClientError

from bsamcli.commands.exceptions import UserException
from bsamcli.local.lambdafn.exceptions import FunctionNotFound
from bsamcli.commands.validate.lib.exceptions import InvalidSamDocumentException
from bsamcli.lib.samlib.cfc_credential_helper import get_credentials, get_region
from bsamcli.lib.samlib.cfc_deploy_conf import get_region_endpoint

from bsamcli.lib.samlib.deploy_context import DeployContext
from bsamcli.lib.samlib.user_exceptions import DeployContextException
from bsamcli.local.docker.cfc_container import Runtime

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
                codeuri = warp_codeuri(f)
                zip_up(codeuri, f.name)
    except FunctionNotFound:
        raise UserException("Function not found in template")
    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))


def execute_deploy_command(command, region=None, endpoint=None):
    LOG.debug("%s command is called", command)
    try:
        with DeployContext(template_file=_TEMPLATE_OPTION_DEFAULT_VALUE,
                           function_identifier=None,
                           env_vars_file=None,
                           log_file=None,
                           ) as context:
            for f in context.all_functions:
                do_deploy(context, f, region, endpoint)

    except FunctionNotFound:
        raise UserException("Function not found in template")
    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))

def do_deploy(context, function, region, endpoint_input):
    # create a cfc client

    client_endpoint = None
    if endpoint_input is not None:
        client_endpoint = endpoint_input
    else:
        client_endpoint = get_region_endpoint(region)    

    cfc_client = CfcClient(BceClientConfiguration(credentials=get_credentials(), endpoint=client_endpoint))
    existed = check_if_exist(cfc_client, function.name)
    if existed:
        update_function(cfc_client, function)
    else:
        create_function(cfc_client, function)
        create_triggers(cfc_client, function, context)

    LOG.info("Funtion %s deploy done." % function.name)


def check_if_exist(cfc_client, function_name):
    try:
        get_function_response = cfc_client.get_function(function_name)
        LOG.debug("[Sample CFC] get_function response:%s", get_function_response)
    except (BceServerError, BceHttpClientError): # TODO 区分一下具体的异常，因为可能是响应超时,input out put 一致
        return False

    return True


def create_function(cfc_client, function):
    # create a cfc function
    function_name = function.name
    base64_file = get_function_base64_file(function_name)
    user_memorysize = function.memory or 128
    user_timeout = function.timeout or 3
    user_runtime = deal_with_func_runtime(function.runtime)
    user_region = get_region()

    env = function.environment
    if env is not None:
        env = env.get("Variables", None)

    try:
        create_response = cfc_client.create_function(function_name,
                                                 description=function.description or "function created by bsam cli",
                                                 handler=function.handler,
                                                 memory_size=user_memorysize,
                                                 environment=env,
                                                 region=user_region,
                                                 zip_file=base64_file,
                                                 publish=False,
                                                 run_time=user_runtime,
                                                 timeout=user_timeout,
                                                 dry_run=False)
        LOG.debug("[Sample CFC] create_response:%s", create_response)
        LOG.info("Function Create Response: %s", str(create_response))

    except(BceServerError, BceHttpClientError) as e:
        if e.last_error.status_code == 403:
            LOG.info("Probably invalid AK/SK , check out ~/.bce/credential to find out...")
        else:
            raise UserException(str(e))


def update_function(cfc_client, function):
    # update function code and configuration
    function_name = function.name
    base64_file = get_function_base64_file(function_name)
    try:
        cfc_client.update_function_code(function.name, zip_file=base64_file)

        LOG.info("Function %s code updated." % function.name)

        env = function.environment
        if env is not None:
            env = env.get("Variables", None)

        cfc_client.update_function_configuration(function.name,
                                            environment=env,
                                            handler=function.handler,
                                            run_time=deal_with_func_runtime(function.runtime),
                                            timeout=function.timeout,
                                            description=function.description)

        LOG.info("Function %s configuration updated." % function.name)


    except(BceServerError, BceHttpClientError) as e:
        if e.last_error.status_code == 403:
            LOG.info("Probably invalid AK/SK , check out ~/.bce/credential to find out...")
        else:
            raise UserException(str(e))


def get_function_base64_file(function_name):
    zipfile_name = function_name + '.zip'
    if not os.path.exists(zipfile_name):
        raise DeployContextException("Zip file not found : {}".format(zipfile_name))

    with open(zipfile_name, 'rb') as fp:
        try:
            return base64.b64encode(fp.read()).decode("utf-8")
        except ValueError as ex:
            raise DeployContextException("Failed to convert zipfile to base64: {}".format(str(ex)))


def zip_up(code_uri, zipfile_name):
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

def deal_with_func_runtime(func_runtime):
    if not Runtime.has_value(func_runtime):
        raise ValueError("Unsupported CFC runtime {}".format(func_runtime))
    return func_runtime

def create_triggers(cfc_client, function, context):
    func_config = cfc_client.get_function_configuration(function.name)
    LOG.debug("get function ret is: %s", func_config)

    try:
        context.deploy(cfc_client, func_config)
    except(BceServerError, BceHttpClientError) as e:
        raise UserException(str(e))

def warp_codeuri(f):
    LOG.debug("f.runtime is: %s", f.runtime)
    if f.runtime == "dotnetcore2.2":
        new_uri = os.path.join(f.codeuri, "bin", "Release", "netcoreapp2.2", "publish/")
        return new_uri
    return f.codeuri
