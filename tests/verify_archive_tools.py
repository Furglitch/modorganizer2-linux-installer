"""Integration check using real pinned downloads in an isolated temporary cache."""

import os
import struct
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from step import external_resources as resources
from util import variables as var


def verify():
    with tempfile.TemporaryDirectory(prefix="mo2-lint-tools-") as temporary:
        root = Path(temporary)
        resources.download_dir = root / "downloads"
        resources.extract_dir = resources.download_dir / "extracted"
        resources.tools_dir = resources.download_dir / "bin"
        var.load_resource_info(var.internal_file("cfg", "resource_info.yml"))
        os.environ["PATH"] = str(root / "empty-host")
        resources.download_archive_tools()
        with patch.object(
            resources, "dl", side_effect=AssertionError("unexpected download")
        ):
            resources.download_archive_tools()

        # A single uncompressed CAB member exercises actual cabextract execution.
        payload = b"MO2-LINT archive-tools integration check\n"
        name = b"sample.txt\0"
        data_offset = 36 + 8 + 16 + len(name)
        size = data_offset + 8 + len(payload)
        cab = root / "sample.cab"
        cab.write_bytes(
            struct.pack(
                "<4sIIIIIBBHHHHH", b"MSCF", 0, size, 0, 44, 0, 3, 1, 1, 1, 0, 0, 0
            )
            + struct.pack("<IHH", data_offset, 1, 0)
            + struct.pack("<IIHHHH", len(payload), 0, 0, 0, 0, 32)
            + name
            + struct.pack("<IHH", 0, len(payload), len(payload))
            + payload
        )
        cab_out = root / "cab-out"
        cab_out.mkdir()
        subprocess.run(["cabextract", "-q", "-d", str(cab_out), str(cab)], check=True)
        assert (cab_out / "sample.txt").read_bytes() == payload

        archive = root / "sample.7z"
        subprocess.run(
            ["7z", "a", str(archive), str(cab_out / "sample.txt")],
            check=True,
            capture_output=True,
        )
        extracted = root / "7z-out"
        resources.unzip(str(archive), outdir=str(extracted), verbosity=-1)
        assert (extracted / "sample.txt").read_bytes() == payload
        print(
            "Pinned downloads, cache reuse, CAB extraction and patool .7z extraction passed."
        )


if __name__ == "__main__":
    verify()
