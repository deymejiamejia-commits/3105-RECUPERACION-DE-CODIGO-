#!/usr/bin/env python3
"""Recover the available Swift AirLift symbol names from a 3105 IPA.

This is read-only analysis of the compiled binary. It does not reconstruct
function bodies, perform pairing, or grant access to iOS app containers.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile


SWIFT_SYMBOL = re.compile(rb"_\$s4_105[A-Za-z0-9_$]{10,800}")
MACH_O_MAGICS = {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"}


def extract_symbols(ipa: Path) -> list[str]:
    symbols: set[str] = set()
    with ZipFile(ipa) as archive:
        binaries = [
            item for item in archive.infolist()
            if item.filename.startswith("Payload/")
            and ".app/" in item.filename
            and not item.is_dir()
            and item.file_size < 150_000_000
        ]
        for entry in binaries:
            with archive.open(entry) as source:
                magic = source.read(4)
                if magic not in MACH_O_MAGICS:
                    continue
                binary = magic + source.read()
            for matched in SWIFT_SYMBOL.finditer(binary):
                name = matched.group().decode("ascii")
                if "AirLift" in name:
                    symbols.add(name)
    return sorted(symbols)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipa", type=Path, help="IPA to inspect (read-only)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--contains", default="", help="optional symbol-name filter")
    parser.add_argument("--compare", type=Path, help="compare symbols with another IPA")
    args = parser.parse_args()

    matches = [name for name in extract_symbols(args.ipa) if args.contains in name]
    if args.compare is not None:
        other = [name for name in extract_symbols(args.compare) if args.contains in name]
        only_first = sorted(set(matches) - set(other))
        only_second = sorted(set(other) - set(matches))
        report = {
            "first_ipa": args.ipa.name,
            "first_count": len(matches),
            "second_ipa": args.compare.name,
            "second_count": len(other),
            "shared": len(set(matches) & set(other)),
            "first_only": only_first,
            "second_only": only_second,
        }
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{args.ipa.name}: {len(matches)} matching Swift symbol names")
            print(f"{args.compare.name}: {len(other)} matching Swift symbol names")
            print(f"Shared: {report['shared']}")
            print(f"Only in first: {len(only_first)}; only in second: {len(only_second)}")
        return

    if args.json:
        print(json.dumps({"ipa": args.ipa.name, "count": len(matches),
                          "symbols": matches}, indent=2))
    else:
        print(f"Recovered {len(matches)} AirLift Swift symbol names")
        for name in matches:
            print(name)


if __name__ == "__main__":
    main()
