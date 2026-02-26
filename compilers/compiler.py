#!/usr/bin/env python3
import os
import sys
import subprocess

# Add parent directory to path so we can import cmakegen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cmakegen.flag_parser import parse_args
from cmakegen.invocation_log import log_invocation, DEFAULT_LOG_PATH

arguments = sys.argv[1:]

# Parse and log the invocation
invocation = parse_args(arguments)
log_path = os.environ.get("CMAKEGEN_LOG", DEFAULT_LOG_PATH)
log_invocation(log_path, invocation)

# Forward to real compiler
subprocess.run(["cc"] + arguments)
