"""Read aggregated invocations and produce CMakeLists.txt content."""

import os


def generate_cmake(invocations: list[dict]) -> str:
    """Generate CMakeLists.txt content from a list of parsed invocations.

    Separates compile and link invocations, aggregates flags, and produces
    a complete CMakeLists.txt string.
    """
    compile_invocations = [inv for inv in invocations if inv.get("compile_only")]
    link_invocations = [inv for inv in invocations if not inv.get("compile_only")]

    # Collect data from compile invocations
    source_files = []
    include_dirs = []
    defines = []
    std = None
    warnings = []
    debug = False
    optimization = None
    other_flags = []
    pic = False
    pthread = False

    # Map .o files to source files for linking step resolution
    obj_to_source = {}

    for inv in compile_invocations:
        for src in inv.get("source_files", []):
            basename = os.path.basename(src)
            if basename not in [os.path.basename(s) for s in source_files]:
                source_files.append(src)
            # Map output .o to this source
            out = inv.get("output")
            if out:
                obj_to_source[out] = src

        for d in inv.get("include_dirs", []):
            if d not in include_dirs:
                include_dirs.append(d)

        for d in inv.get("defines", []):
            if d not in defines:
                defines.append(d)

        if inv.get("std") and not std:
            std = inv["std"]

        for w in inv.get("warnings", []):
            if w not in warnings:
                warnings.append(w)

        if inv.get("debug"):
            debug = True

        if inv.get("optimization") and not optimization:
            optimization = inv["optimization"]

        for f in inv.get("other_flags", []):
            if f not in other_flags:
                other_flags.append(f)

        if inv.get("pic"):
            pic = True

        if inv.get("pthread"):
            pthread = True

    # Extract data from link invocations
    target_name = None
    libraries = []
    lib_dirs = []
    linker_flags = []

    for inv in link_invocations:
        if inv.get("output") and not target_name:
            target_name = inv["output"]

        for lib in inv.get("libraries", []):
            if lib not in libraries:
                libraries.append(lib)

        for d in inv.get("lib_dirs", []):
            if d not in lib_dirs:
                lib_dirs.append(d)

        for f in inv.get("linker_flags", []):
            if f not in linker_flags:
                linker_flags.append(f)

        # If no compile invocations, get source files from link step via .o mapping
        if not compile_invocations:
            for src in inv.get("source_files", []):
                basename = os.path.basename(src)
                if basename not in [os.path.basename(s) for s in source_files]:
                    source_files.append(src)

        # Map .o files in link step back to sources from compile steps
        for obj in inv.get("object_files", []):
            if obj in obj_to_source:
                src = obj_to_source[obj]
                basename = os.path.basename(src)
                if basename not in [os.path.basename(s) for s in source_files]:
                    source_files.append(src)

        if inv.get("pthread"):
            pthread = True

    # Default target name
    if not target_name:
        target_name = "project"

    # Determine C vs C++ standard
    std_setting = None
    if std:
        # Extract numeric part from standards like c++11, gnu++14, c11, gnu11
        if "c++" in std or "gnu++" in std:
            std_num = std.replace("gnu++", "").replace("c++", "")
            std_setting = ("CXX", std_num)
        else:
            std_num = std.replace("gnu", "").replace("c", "")
            std_setting = ("C", std_num)

    # Use basenames for source files in CMake output
    source_basenames = [os.path.basename(s) for s in source_files]

    # Build CMakeLists.txt
    lines = []
    lines.append("cmake_minimum_required(VERSION 3.10)")
    lines.append(f"project({target_name})")

    if std_setting:
        lang, num = std_setting
        lines.append(f"set(CMAKE_{lang}_STANDARD {num})")

    lines.append(f"add_executable({target_name} {' '.join(source_basenames)})")

    if include_dirs:
        dirs_str = " ".join(include_dirs)
        lines.append(f"target_include_directories({target_name} PRIVATE {dirs_str})")

    if defines:
        defs_str = " ".join(defines)
        lines.append(f"target_compile_definitions({target_name} PRIVATE {defs_str})")

    if libraries or pthread:
        libs = list(libraries)
        if pthread and "pthread" not in libs:
            libs.append("pthread")
        libs_str = " ".join(libs)
        lines.append(f"target_link_libraries({target_name} PRIVATE {libs_str})")

    if lib_dirs:
        dirs_str = " ".join(lib_dirs)
        lines.append(f"target_link_directories({target_name} PRIVATE {dirs_str})")

    compile_opts = []
    for w in warnings:
        compile_opts.append(f"-W{w}")
    if debug:
        compile_opts.append("-g")
    if optimization:
        compile_opts.append(f"-O{optimization}")
    if pic:
        compile_opts.append("-fPIC")
    compile_opts.extend(other_flags)

    if compile_opts:
        opts_str = " ".join(compile_opts)
        lines.append(f"target_compile_options({target_name} PRIVATE {opts_str})")

    return "\n".join(lines) + "\n"
