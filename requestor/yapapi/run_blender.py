import os
import subprocess
import time
import json
import shutil
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run_command(command, working_dir=None):
    logger.info(f"Running command: {command}")
    command_array = command.split(" ")
    logger.info(f"Command array: {command_array}")
    p = subprocess.Popen(command_array, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    rc = p.returncode
    logger.info(f"Command output: {out}")
    logger.info(f"Command err-output: {err}")
    logger.info(f"Command return code: {rc}")
    return out, err, rc


def run_command_output_log(command, working_dir=None):
    logger.info(f"Running command: {command}")
    command_array = command.split(" ")
    logger.info(f"Command array: {command_array}")
    subprocess.run(command_array, cwd=working_dir)

