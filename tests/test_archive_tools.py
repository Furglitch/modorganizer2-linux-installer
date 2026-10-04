"""Offline regression checks for automatic archive-tool downloads.

Run with PYTHONPATH=src/mo2-lint:src python -m unittest discover -s tests.
"""

import hashlib
import io
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml
from step import external_resources as resources
from util import variables as var


class ArchiveToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.downloads = self.root / "downloads"
        self.downloads.mkdir()
        self.bin = self.downloads / "bin"
        for name, value in (
            ("download_dir", self.downloads),
            ("tools_dir", self.bin),
            ("extract_dir", self.downloads / "extracted space$"),
        ):
            context = patch.object(resources, name, value)
            context.start()
            self.addCleanup(context.stop)
        context = patch.dict(os.environ, {"PATH": str(self.root / "host")})
        context.start()
        self.addCleanup(context.stop)

    def executable(self, directory, name):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
        return path

    def test_host_tools_take_priority_and_need_no_download(self):
        host = self.root / "host"
        self.executable(host, "7z")
        self.executable(host, "cabextract")
        self.executable(self.bin, "cabextract")
        with patch.object(resources, "dl") as download:
            resources.download_archive_tools()
        download.assert_not_called()
        self.assertEqual(resources.shutil.which("cabextract"), str(host / "cabextract"))
        self.assertEqual(os.environ["PATH"].split(os.pathsep)[-1], str(self.bin))

    def test_host_7zip_is_not_needed_to_unpack_cabextract(self):
        host = self.root / "host"
        old = self.executable(host, "7z")
        cab = self.executable(self.root / "fallback", "cabextract")
        with (
            patch.object(resources.host, "machine", return_value="x86_64"),
            patch.object(resources, "download_cabextract", return_value=cab),
        ):
            resources.download_archive_tools()
        self.assertEqual(resources.shutil.which("7z"), str(old))
        self.assertEqual((self.bin / "cabextract").resolve(), cab)

    def test_failed_download_stops_before_prefix_configuration(self):
        with (
            patch.object(resources.host, "machine", return_value="x86_64"),
            patch.object(resources, "download_cabextract", return_value=None),
            self.assertRaises(SystemExit) as error,
        ):
            resources.download_archive_tools()
        self.assertEqual(error.exception.code, 1)

    def test_unsupported_architecture_does_not_fetch_x86_tools(self):
        with (
            patch.object(resources.host, "machine", return_value="riscv64"),
            patch.object(resources, "download_cabextract") as download,
            self.assertRaises(SystemExit),
        ):
            resources.download_archive_tools()
        download.assert_not_called()

    def test_corrupt_cached_package_is_discarded_before_download(self):
        package = self.downloads / "tool.tar.xz"
        package.write_bytes(b"broken")
        expected = b"verified archive"
        resource = var.Resource(
            download_url="https://example.invalid/tool.tar.xz",
            checksum=hashlib.sha256(expected).hexdigest(),
        )

        def download(*args, **kwargs):
            self.assertFalse(package.exists())
            package.write_bytes(expected)
            return package

        with patch.object(resources, "dl", side_effect=download):
            self.assertEqual(resources.download_tool_resource(resource), package)

    def test_checksum_mismatch_is_never_used(self):
        package = self.downloads / "tool.tar.xz"
        resource = var.Resource(
            download_url="https://example.invalid/tool.tar.xz", checksum="0" * 64
        )

        def download(*args, **kwargs):
            package.write_bytes(b"wrong archive")
            return package

        with patch.object(resources, "dl", side_effect=download):
            self.assertIsNone(resources.download_tool_resource(resource))
        self.assertFalse(package.exists())

    def test_refreshed_config_preserves_overrides_and_fills_bundled_tools(self):
        bundled = var.internal_file("cfg", "resource_info.yml")
        data = yaml.safe_load(bundled.read_text())
        for tool in ("cabextract", "libmspack"):
            data["resources"].pop(tool)
        data["resources"]["winetricks"]["version"] = "user override"
        refreshed = self.root / "resource_info.yml"
        refreshed.write_text(yaml.safe_dump(data))
        with patch.object(var, "resource_info"):
            var.load_resource_info(refreshed)
            self.assertEqual(var.resource_info.winetricks.version, "user override")
            self.assertIsNotNone(var.resource_info.cabextract)
            self.assertIsNotNone(var.resource_info.libmspack)

    def package(self, name, member, content, deb=False):
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode="w:xz") as archive:
            info = tarfile.TarInfo(member)
            info.size = len(content)
            info.mode = 0o755
            archive.addfile(info, io.BytesIO(content))
        payload = data.getvalue()
        if deb:

            def ar_member(filename, value):
                header = f"{filename + '/':<16}{0:<12}{0:<6}{0:<6}{'100644':<8}{len(value):<10}`\n".encode()
                return header + value + (b"\n" if len(value) % 2 else b"")

            payload = (
                b"!<arch>\n"
                + ar_member("debian-binary", b"2.0\n")
                + ar_member("control.tar.xz", b"odd")
                + ar_member("data.tar.xz", payload)
            )
        package = self.downloads / name
        package.write_bytes(payload)
        return var.Resource(
            download_url="https://example.invalid/" + name,
            checksum=hashlib.sha256(payload).hexdigest(),
            path_internal=member,
            version="test",
        )

    def test_debian_cabextract_cache_and_private_library_environment(self):
        cab = self.package(
            "cab.deb",
            "./usr/bin/cabextract",
            b'#!/bin/sh\nprintf "%s" "$LD_LIBRARY_PATH"\n',
            deb=True,
        )
        lib = self.package(
            "lib.deb",
            "./usr/lib/private/libmspack.so.0.1.0",
            b"private library",
            deb=True,
        )
        with (
            patch.object(resources.host, "machine", return_value="x86_64"),
            patch.object(
                var, "resource_info", SimpleNamespace(cabextract=cab, libmspack=lib)
            ),
            patch.dict(os.environ, {"LD_LIBRARY_PATH": "original"}),
        ):
            wrapper = resources.download_cabextract()
            self.assertIsNotNone(wrapper)
            result = subprocess.run(
                [str(wrapper), "--version"], check=True, capture_output=True, text=True
            )
            self.assertEqual(
                result.stdout, str(wrapper.parent / "usr/lib/private") + ":original"
            )
            self.assertEqual(os.environ["LD_LIBRARY_PATH"], "original")
            with patch.object(
                resources,
                "extract_debian_resource",
                side_effect=AssertionError("cache was extracted again"),
            ):
                self.assertEqual(resources.download_cabextract(), wrapper)
            (wrapper.parent / "usr/bin/cabextract").write_bytes(b"broken")
            self.assertEqual(resources.download_cabextract(), wrapper)
            self.assertEqual(
                subprocess.run(
                    [str(wrapper), "--version"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout,
                result.stdout,
            )

    def test_primary_download_failure_uses_checksum_pinned_fallback(self):
        resource = var.Resource(
            download_url="https://primary.invalid/tool",
            fallback_url="https://snapshot.invalid/tool",
            checksum=hashlib.sha256(b"valid").hexdigest(),
        )
        cached = self.downloads / "tool"

        def download(url, *args, **kwargs):
            if url == resource.download_url:
                return None
            cached.write_bytes(b"valid")
            return cached

        with patch.object(resources, "dl", side_effect=download) as get:
            self.assertEqual(resources.download_tool_resource(resource), cached)
        self.assertEqual(
            [call.args[0] for call in get.call_args_list],
            [resource.download_url, resource.fallback_url],
        )

    def test_debian_reader_rejects_truncated_or_missing_payload(self):
        for value in (b"broken", b"!<arch>\n", b"!<arch>\ntruncated"):
            package = self.downloads / "bad.deb"
            package.write_bytes(value)
            with self.assertRaises(ValueError):
                resources.debian_payload(package)


if __name__ == "__main__":
    unittest.main()
