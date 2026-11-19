#!/usr/bin/env python3
"""Compare recoverable AirLift type metadata with an older Swift source tree.

This tool only reads a decompiler archive; it does not access any iOS device,
write to an application container, or reconstruct machine-code bodies.
"""
import argparse
import re
from pathlib import Path
from zipfile import ZipFile


def inventory(archive: Path, source_root: Path):
    with ZipFile(archive) as zf:
        swift = zf.read("swift/3105.swift").decode("utf-8", errors="replace")
    names = set(re.findall(r"^(?:class|struct|enum|protocol) _105\.(AirLift[A-Za-z0-9_]+)", swift, flags=re.M))
    old = "\n".join(path.read_text(errors="replace") for path in source_root.rglob("*.swift"))
    old_names = set(re.findall(r"\b(?:class|struct|enum|protocol)\s+(AirLift[A-Za-z0-9_]+)\b", old))
    print("AirLift types in newer compiled metadata:", len(names))
    print("AirLift types declared in old Swift sources:", len(old_names))
    print("Known newer types missing from old Swift sources:")
    for name in sorted(names - old_names):
        print(" -", name)
    print("\nNote: names and field declarations are not function implementations.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("decompiler_zip", type=Path)
    parser.add_argument("swift_source_directory", type=Path)
    args = parser.parse_args()
    inventory(args.decompiler_zip, args.swift_source_directory)
