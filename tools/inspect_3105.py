#!/usr/bin/env python3
"""Read-only inspection of unprotected 3105PATCH v1/v2/v3 package metadata.

Requires: pip install cryptography
Does not apply patches or write to application containers.
"""
import argparse
import hashlib
import json
import plistlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def inspect(path: Path) -> dict:
    raw = path.read_bytes()
    if not raw.startswith(b"3105PATCH\0"):
        raise ValueError("Missing 3105PATCH header")
    header = plistlib.loads(raw[len(b"3105PATCH\0"):])
    version = header["schemaVersion"]
    package_id = header["packageID"]
    key = header.get("publicContentKey")
    if header.get("isPasswordProtected") or key is None:
        raise ValueError("Password-protected package: cannot inspect without its password")
    if hashlib.sha256(key).digest() != header["keyFingerprint"]:
        raise ValueError("Content key fingerprint mismatch")
    payload = header["encryptedPayload"]
    aad = f"3105PATCH/v{version}/payload/{package_id}".encode()
    decoded = AESGCM(key).decrypt(payload[:12], payload[12:], aad)
    project = plistlib.loads(decoded)["project"]
    if str(project["id"]).upper() != package_id.upper():
        raise ValueError("Package identity mismatch")
    rules = project.get("rules", [])
    return {
        "name": project["name"],
        "schema_version": version,
        "package_id": package_id,
        "target_bundles": project.get("bundleIdentifiers", []),
        "rules": [
            {
                "bundle_id": r.get("bundleID"),
                "relative_path": r.get("relativePath"),
                "replacement_filename": r.get("replacementFilename"),
                "replacement_size_bytes": len(r.get("replacementData", b"")),
            }
            for r in rules
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect .3105 metadata without modifying files")
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.package), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
