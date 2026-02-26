"""Parse compiler/linker flags into structured data."""

import os
import re

SOURCE_EXTENSIONS = {'.c', '.cpp', '.cc', '.cxx', '.C'}
OBJECT_EXTENSION = '.o'


def parse_args(argv: list[str]) -> dict:
    """Parse compiler command-line arguments into a structured dict.

    Args:
        argv: List of compiler arguments (excluding the compiler binary itself).

    Returns:
        Dict with parsed flag categories.
    """
    result = {
        "source_files": [],
        "object_files": [],
        "output": None,
        "std": None,
        "include_dirs": [],
        "defines": [],
        "lib_dirs": [],
        "libraries": [],
        "optimization": None,
        "warnings": [],
        "debug": False,
        "pic": False,
        "pthread": False,
        "compile_only": False,
        "linker_flags": [],
        "other_flags": [],
    }

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "-c":
            result["compile_only"] = True

        elif arg == "-o":
            i += 1
            if i < len(argv):
                result["output"] = argv[i]

        elif arg.startswith("-std="):
            result["std"] = arg[5:]

        # -I with space or joined
        elif arg == "-I":
            i += 1
            if i < len(argv):
                result["include_dirs"].append(argv[i])
        elif arg.startswith("-I"):
            result["include_dirs"].append(arg[2:])

        # -D with space or joined
        elif arg == "-D":
            i += 1
            if i < len(argv):
                result["defines"].append(argv[i])
        elif arg.startswith("-D"):
            result["defines"].append(arg[2:])

        # -L with space or joined
        elif arg == "-L":
            i += 1
            if i < len(argv):
                result["lib_dirs"].append(argv[i])
        elif arg.startswith("-L"):
            result["lib_dirs"].append(arg[2:])

        # -l with space or joined
        elif arg == "-l":
            i += 1
            if i < len(argv):
                result["libraries"].append(argv[i])
        elif arg.startswith("-l"):
            result["libraries"].append(arg[2:])

        # Optimization
        elif re.match(r'^-O[0-3sg]$', arg):
            result["optimization"] = arg[2:]

        # Linker flags
        elif arg.startswith("-Wl,"):
            result["linker_flags"].append(arg)

        # Warning flags
        elif arg.startswith("-W"):
            result["warnings"].append(arg[2:])

        elif arg == "-g":
            result["debug"] = True

        elif arg in ("-fPIC", "-fpic"):
            result["pic"] = True

        elif arg == "-pthread":
            result["pthread"] = True

        # Source or object files (positional args)
        elif not arg.startswith("-"):
            ext = os.path.splitext(arg)[1]
            if ext in SOURCE_EXTENSIONS:
                result["source_files"].append(arg)
            elif ext == OBJECT_EXTENSION:
                result["object_files"].append(arg)
            # Ignore other positional args

        else:
            result["other_flags"].append(arg)

        i += 1

    return result
