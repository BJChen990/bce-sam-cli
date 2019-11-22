"""
Classes representing a local CFC runtime
"""

import os
import shutil
import tempfile
import signal
import logging
import threading
import json
from contextlib import contextmanager

from bsamcli.local.docker.cfc_container import CfcContainer
from .zip import unzip

LOG = logging.getLogger(__name__)


class CfcRuntime(object):
    """
    This class represents a Local CFC runtime. It can run the CFC function code locally in a Docker container
    and return results. Public methods exposed by this class are similar to the BCE CFC APIs, for convenience only.
    This class is **not** intended to be an local replica of the CFC APIs.
    """

    SUPPORTED_ARCHIVE_EXTENSIONS = (".jar")

    def __init__(self, container_manager):
        """
        Initialize the Local CFC runtime

        :param bsamcli.local.docker.manager.ContainerManager container_manager: Instance of the ContainerManager class
            that can run a local Docker container
        """
        self._container_manager = container_manager

    def invoke(self,
               function_config,
               cwd,
               event,
               debug_context=None,
               is_installing=None,
               stdout=None,
               stderr=None):
        """
        Invoke the given CFC function locally.

        ##### NOTE: THIS IS A LONG BLOCKING CALL #####
        This method will block until either the CFC function completes or timed out, which could be seconds.
        A blocking call will block the thread preventing any other operations from happening. If you are using this
        method in a web-server or in contexts where your application needs to be responsive when function is running,
        take care to invoke the function in a separate thread. Co-Routines or micro-threads might not perform well
        because the underlying implementation essentially blocks on a socket, which is synchronous.

        :param FunctionConfig function_config: Configuration of the function to invoke
        :param event: String input event passed to CFC function
        :param DebugContext debug_context: Debugging context for the function (includes port, args, and path)
        :param io.IOBase stdout: Optional. IO Stream to that receives stdout text from container.
        :param io.IOBase stderr: Optional. IO Stream that receives stderr text from container
        :raises Keyboard
        """
        timer = None

        # Update with event input
        environ = function_config.env_vars
        environ.add_cfc_event_body(event)
        if is_installing:
            environ.add_install_flag()
        # Generate a dictionary of environment variable key:values
        env_vars = environ.resolve()
        with self._get_code_dir(function_config, cwd, is_installing) as code_dir:
            container = CfcContainer(function_config.runtime,
                                        function_config.handler,
                                        code_dir,
                                        memory_mb=function_config.memory,
                                        env_vars=env_vars,
                                        debug_options=debug_context)

            try:

                # Start the container. This call returns immediately after the container starts
                self._container_manager.run(container, is_installing)

                # Setup appropriate interrupt - timeout or Ctrl+C - before function starts executing.
                #
                # Start the timer **after** container starts. Container startup takes several seconds, only after which,
                # our CFC function code will run. Starting the timer is a reasonable approximation that function has
                # started running.
                timer = self._configure_interrupt(function_config.name,
                                                  function_config.timeout,
                                                  container,
                                                  bool(debug_context),
                                                  is_installing)

                # NOTE: BLOCKING METHOD
                # Block the thread waiting to fetch logs from the container. This method will return after container
                # terminates, either successfully or killed by one of the interrupt handlers above.
                container.wait_for_logs(stdout=stdout, stderr=stderr)

            except KeyboardInterrupt:
                # When user presses Ctrl+C, we receive a Keyboard Interrupt. This is especially very common when
                # container is in debugging mode. We have special handling of Ctrl+C. So handle KeyboardInterrupt
                # and swallow the exception. The ``finally`` block will also take care of cleaning it up.
                LOG.debug("Ctrl+C was pressed. Aborting CFC execution")

            finally:
                # We will be done with execution, if either the execution completed or an interrupt was fired
                # Any case, cleanup the timer and container.
                #
                # If we are in debugging mode, timer would not be created. So skip cleanup of the timer
                if timer:
                    timer.cancel()
                self._container_manager.stop(container)

    def _configure_interrupt(self, function_name, timeout, container, is_debugging, is_installing):
        """
        When a CFC function is executing, we setup certain interrupt handlers to stop the execution.
        Usually, we setup a function timeout interrupt to kill the container after timeout expires. If debugging though,
        we don't enforce a timeout. But we setup a SIGINT interrupt to catch Ctrl+C and terminate the container.

        :param string function_name: Name of the function we are running
        :param integer timeout: Timeout in seconds
        :param bsamcli.local.docker.container.Container container: Instance of a container to terminate
        :param bool is_debugging: Are we debugging?
        :return threading.Timer: Timer object, if we setup a timer. None otherwise
        """

        def timer_handler():
            # NOTE: This handler runs in a separate thread. So don't try to mutate any non-thread-safe data structures
            LOG.info("Function '%s' timed out after %d seconds", function_name, timeout)
            self._container_manager.stop(container)

        def signal_handler(sig, frame):
            # NOTE: This handler runs in a separate thread. So don't try to mutate any non-thread-safe data structures
            LOG.info("Execution of function %s was interrupted", function_name)
            self._container_manager.stop(container)

        if is_debugging or is_installing:
            LOG.debug("Setting up SIGTERM interrupt handler")
            signal.signal(signal.SIGTERM, signal_handler)
        else:
            # Start a timer, we'll use this to abort the function if it runs beyond the specified timeout
            LOG.debug("Starting a timer for %s seconds for function '%s'", timeout, function_name)
            timer = threading.Timer(timeout, timer_handler, ())
            timer.start()
            return timer

    @contextmanager
    def _get_code_dir(self, function_config, cwd, is_installing):
        """
        Method to get a path to a directory where the CFC function code is available. This directory will
        be mounted directly inside the Docker container.

        This method handles a few different cases for ``code_path``:
            - ``code_path``is a existent zip/jar file: Unzip in a temp directory and return the temp directory
            - ``code_path`` is a existent directory: Return this immediately
            - ``code_path`` is a file/dir that does not exist: Return it as is. May be this method is not clever to
                detect the existence of the path

        :param string code_path: Path to the code. This could be pointing at a file or folder either on a local
            disk or in some network file system
        :return string: Directory containing CFC function code. It can be mounted directly in container
        """

        code_path = function_config.code_abs_path
        tmp_dir = None

        try:
            if is_installing:
                if function_config.runtime == "java8":
                    yield cwd          # where template.yaml is
                else:
                    yield code_path

            elif os.path.isfile(code_path) and code_path.endswith(self.SUPPORTED_ARCHIVE_EXTENSIONS):
                tmp_dir = _get_tmp_dir(code_path)
                yield tmp_dir

            elif function_config.runtime == "dotnetcore2.2":
                yield os.path.join(code_path, "bin", "Release", "netcoreapp2.2", "publish/")

            else:
                LOG.debug("Code %s is not a jar file", code_path)
                yield code_path
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir)

def _get_tmp_dir(filepath):
    """
    copy .jar to a temporary directory
    """

    tmp_dir = tempfile.mkdtemp()
    if os.name == 'posix':
        os.chmod(tmp_dir, 0o755)

    LOG.info("Copying %s to a temporary directory", filepath)

    shutil.copyfile(filepath, os.path.join(tmp_dir, "tmp.jar"))

    return os.path.realpath(tmp_dir)


def _unzip_file(filepath):
    """
    Helper method to unzip a file to a temporary directory

    :param string filepath: Absolute path to this file
    :return string: Path to the temporary directory where it was unzipped
    """

    temp_dir = tempfile.mkdtemp()

    if os.name == 'posix':
        os.chmod(temp_dir, 0o755)

    LOG.info("Decompressing %s", filepath)

    unzip(filepath, temp_dir)

    # The directory that Python returns might have symlinks. The Docker File sharing settings will not resolve
    # symlinks. Hence get the real path before passing to Docker.
    # Especially useful in Mac OSX which returns /var/folders which is a symlink to /private/var/folders that is a
    # part of Docker's Shared Files directories
    return os.path.realpath(temp_dir)
