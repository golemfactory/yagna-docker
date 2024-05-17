import os
import asyncio
import json
import subprocess
import threading
import logging

logger = logging.getLogger(__name__)


def read_stream_stdout(stream, context):
    context["stdout"] = b""
    while True:
        chunk = stream.read(2000)
        if not chunk:
            break
        context["stdout"] += chunk


def read_stream_stderr(stream, context):
    context["stderr"] = b""
    while True:
        chunk = stream.read(2000)
        if not chunk:
            break
        context["stderr"] += chunk


def run_process_start(args):
    context = {}
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    context["process"] = process

    # Create threads to read stdout and stderr concurrently
    stdout_thread = threading.Thread(
        target=read_stream_stdout, args=(process.stdout, context)
    )
    stderr_thread = threading.Thread(
        target=read_stream_stderr, args=(process.stderr, context)
    )

    # Start the threads
    stdout_thread.start()
    stderr_thread.start()

    context["stdout_thread"] = stdout_thread
    context["stderr_thread"] = stderr_thread

    return context


def run_process_blocking(args):
    context = run_process_start(args)

    # Wait for the process to finish
    context["process"].wait()

    # Wait for threads to complete
    context["stdout_thread"].join()
    context["stderr_thread"].join()


async def run_process_async_text(command):
    command.split(" ")
    return await run_process_async(command)


async def run_process_async(args):
    context = run_process_start(args)

    while context["process"].poll() is None:
        await asyncio.sleep(1)

    # Wait for threads to complete
    context["stdout_thread"].join()
    context["stderr_thread"].join()

    logger.info(
        "GFTP process finished with return code: {}".format(
            context["process"].returncode
        )
    )
    if "error" in context:
        raise Exception(context["error"])

    return context["stdout"]


def run_simple(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output
    stdout, stderr = process.communicate()

    return stdout
