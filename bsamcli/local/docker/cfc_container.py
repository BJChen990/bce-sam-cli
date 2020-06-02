"""
Represents Cfc runtime containers.
"""

import logging
from enum import Enum
from .container import Container

LOG = logging.getLogger(__name__)


class Runtime(Enum):
    nodejs10 = "nodejs10"
    nodejs12 = "nodejs12"
    python27 = "python2"
    python36 = "python3"
    php72 = "php7"
    lua53 = "lua5.3"
    java8 = "java8"
    golang = "golang"
    dotnetcore22 = "dotnetcore2.2"
    powershell62 = "powershell6.2"

    @classmethod
    def has_value(cls, value):
        """
        Checks if the enum has this value

        :param string value: Value to check
        :return bool: True, if enum has the value
        """
        return any(value == item.value for item in cls)


class CfcContainer(Container):
    """
    Represents a Cfc runtime container. This class knows how to setup entry points, environment variables,
    exposed ports etc specific to Cfc runtime container. The container management functionality (create/start/stop)
    is provided by the base class
    """

    _IMAGE_REPO_NAME = "registry.baidubce.com/cfc-public/runtime"

    _WORKING_DIR = "/var/task"

    # The Volume Mount path for debug files in docker
    _DEBUGGER_VOLUME_MOUNT_PATH = "/tmp/lambdaci_debug_files"
    _DEFAULT_CONTAINER_DBG_GO_PATH = _DEBUGGER_VOLUME_MOUNT_PATH + "/dlv"

    # This is the dictionary that represents where the debugger_path arg is mounted in docker to as readonly.
    _DEBUGGER_VOLUME_MOUNT = {"bind": _DEBUGGER_VOLUME_MOUNT_PATH, "mode": "ro"}

    def __init__(self,
                 runtime,
                 handler,
                 code_dir,
                 memory_mb=128,
                 env_vars=None,
                 debug_options=None):
        """
        Initializes the class

        :param string runtime: Name of the CFC runtime
        :param string handler: Handler of the function to run
        :param string code_dir: Directory where the CFC function code is present. This directory will be mounted
            to the container to execute
        :param int memory_mb: Optional. Max limit of memory in MegaBytes this CFC function can use.
        :param dict env_vars: Optional. Dictionary containing environment variables passed to container
        :param DebugContext debug_options: Optional. Contains container debugging info (port, debugger path)
        """

        if not Runtime.has_value(runtime):
            raise ValueError("Unsupported CFC runtime {}".format(runtime))

        image = CfcContainer._get_image(runtime)
        ports = CfcContainer._get_exposed_ports(debug_options)
        entry = CfcContainer._get_entry_point(runtime, debug_options)
        additional_options = CfcContainer._get_additional_options(runtime, debug_options)
        additional_volumes = CfcContainer._get_additional_volumes(debug_options)

        super(CfcContainer, self).__init__(image,
                                           None,
                                           self._WORKING_DIR,
                                           code_dir,
                                           memory_limit_mb=memory_mb,
                                           exposed_ports=ports,
                                           entrypoint=entry,
                                           env_vars=env_vars,
                                           container_opts=additional_options,
                                           additional_volumes=additional_volumes)

    @staticmethod
    def _get_exposed_ports(debug_options):
        """
        Return Docker container port binding information. If a debug port is given, then we will ask Docker to
        bind to same port both inside and outside the container ie. Runtime process is started in debug mode with
        at given port inside the container and exposed to the host machine at the same port

        :param int debug_port: Optional, integer value of debug port
        :return dict: Dictionary containing port binding information. None, if debug_port was not given
        """
        if not debug_options:
            return None

        return {
            # container port : host port
            debug_options.debug_port: debug_options.debug_port
        }

    @staticmethod
    def _get_additional_options(runtime, debug_options):
        """
        Return additional Docker container options. Used by container debug mode to enable certain container
        security options.
        :param DebugContext debug_options: DebugContext for the runtime of the container.
        :return dict: Dictionary containing additional arguments to be passed to container creation.
        """
        if not debug_options:
            return None

        opts = {}

        # if runtime == Runtime.go1x.value:
        #     # These options are required for delve to function properly inside a docker container on docker < 1.12
        #     # See https://github.com/moby/moby/issues/21051
        #     opts["security_opt"] = ["seccomp:unconfined"]
        #     opts["cap_add"] = ["SYS_PTRACE"]

        return opts

    @staticmethod
    def _get_additional_volumes(debug_options):
        """
        Return additional volumes to be mounted in the Docker container. Used by container debug for mapping
        debugger executable into the container.
        :param DebugContext debug_options: DebugContext for the runtime of the container.
        :return dict: Dictionary containing volume map passed to container creation.
        """
        if not debug_options or not debug_options.debugger_path:
            return None

        return {
            debug_options.debugger_path: CfcContainer._DEBUGGER_VOLUME_MOUNT
        }

    @staticmethod
    def _get_image(runtime):
        """
        Returns the name of Docker Image for the given runtime

        :param string runtime: Name of the runtime
        :return: Name of Docker Image for the given runtime
        """
        return "{}:{}".format(CfcContainer._IMAGE_REPO_NAME, runtime)

    @staticmethod
    def _get_entry_point(runtime, debug_options=None):
        """
        Returns the entry point for the container. The default value for the entry point is already configured in the
        Dockerfile. We override this default specifically when enabling debugging. The overridden entry point includes
        a few extra flags to start the runtime in debug mode.

        :param string runtime: CFC function runtime name
        :param int debug_port: Optional, port for debugger
        :param string debug_args: Optional additional arguments passed to the entry point.
        :return list: List containing the new entry points. Each element in the list is one portion of the command.
            ie. if command is ``node index.js arg1 arg2``, then this list will be ["node", "index.js", "arg1", "arg2"]
        """

        if not debug_options:
            return None

        debug_port = debug_options.debug_port
        debug_args_list = []
        if debug_options.debug_args:
            debug_args_list = debug_options.debug_args.split(" ")

        # configs from: https://github.com/lambci/docker-lambda
        # to which we add the extra debug mode options
        entrypoint = None
        if runtime in [Runtime.nodejs10.value, Runtime.nodejs12.value, Runtime.python27.value, Runtime.python36.value, Runtime.java8.value]:
            entrypoint = ["/bin/bash", "/var/runtime/bin/entry.sh"] + [str(debug_port)] + debug_args_list

        # elif runtime == Runtime.go1x.value:
        #     entrypoint = ["/var/runtime/aws-lambda-go"] \
        #         + debug_args_list \
        #         + [
        #             "-debug=true",
        #             "-delvePort=" + str(debug_port),
        #             "-delvePath=" + CfcContainer._DEFAULT_CONTAINER_DBG_GO_PATH,
        #           ]

        return entrypoint
