"""CLI entry point: python -m cmakegen generate"""

import argparse
import sys

from cmakegen.invocation_log import read_invocations, clear_log, DEFAULT_LOG_PATH
from cmakegen.cmake_generator import generate_cmake


def main():
    parser = argparse.ArgumentParser(prog="cmakegen", description="Generate CMakeLists.txt from intercepted build commands")
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate", help="Generate CMakeLists.txt from the invocation log")
    gen_parser.add_argument("--log", default=DEFAULT_LOG_PATH, help="Path to the invocation log file")
    gen_parser.add_argument("--output", "-o", help="Write output to file instead of stdout")

    clear_parser = subparsers.add_parser("clear", help="Clear the invocation log")
    clear_parser.add_argument("--log", default=DEFAULT_LOG_PATH, help="Path to the invocation log file")

    args = parser.parse_args()

    if args.command == "generate":
        invocations = read_invocations(args.log)
        if not invocations:
            print("No invocations found in log. Run a build with the proxy compilers first.", file=sys.stderr)
            sys.exit(1)
        cmake_content = generate_cmake(invocations)
        if args.output:
            with open(args.output, "w") as f:
                f.write(cmake_content)
            print(f"CMakeLists.txt written to {args.output}")
        else:
            print(cmake_content)

    elif args.command == "clear":
        clear_log(args.log)
        print("Log cleared.")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
