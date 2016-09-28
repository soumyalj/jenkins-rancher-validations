#!/usr/bin/env python3
# coding: us-ascii
# mode: python

import sys, logging, os, colorama
from invoke import run, Failure
from colorama import Fore
from pprint import pprint as pp

colorama.init()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s'))
log.addHandler(stream)

DOCKER_MACHINE = "docker-machine --storage-path /workdir/.docker/machine "


#
def log_err(msg):
     log.error(Fore.RED + str(msg) + Fore.RESET)


#
def err_and_exit(msg, code=-1):
     log_err(msg)
     sys.exit(-1)


#
def missing_envvars(envvars=['AWS_PREFIX']):
     missing = []
     for envvar in envvars:
          if envvar not in os.environ:
               missing.append(envvar)
     log.debug("Missing envvars: {}".format(missing))
     return missing


#
def deprovision_rancher_server():

     machine_name = "{}-ubuntu-1604-validation-tests-server0".format(os.environ.get('AWS_PREFIX'))

     try:
          cmd = DOCKER_MACHINE + "rm -f {}".format(machine_name)
          run(cmd, echo=True)

     except Failure as e:
          log.error("Failed while deprovisioning rancher/server!: {} :: {}".format(e.result.return_code, e.result.stderr))
          return False

     return True


#
def main():
     if 'DEBUG' in os.environ:
          log.setLevel(logging.DEBUG)
          log.debug("Environment:")
          log.debug(pp(os.environ.copy(), indent=2, width=1))

     # validate our envvars are in place
     missing = missing_envvars()
     if [] != missing:
          err_and_exit("Unable to find required environment variables! : {}".format(', '.join(missing)))

     if not deprovision_rancher_server():
          err_and_exit("Failed while deprovisioning rancher/server!")


if '__main__' == __name__:
    main()
