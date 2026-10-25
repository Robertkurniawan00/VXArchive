"""
Unit tests for VXArchive Dark Glass Edition, including 10 Pro Features:
1. DoD 5220.22-M Secure Multi-Pass Shredder
2. Archive Format Transcoder / Converter
3. Steganographic Secret Vault (Hide/Extract Archive in Images)
4. Smart Archive Diff & Folder Synchronizer
5. Multi-Volume Splitter & Joiner
6. Suspicious Threat & Zip-Bomb Heuristic Scanner
7. Corrupted Archive Integrity Salvager / Repair Engine
8. Bookmarks & Project Pinboard Hub
9. Virtual ISO / VHD Drive Mounter
10. Deep File Metadata & EXIF Inspector
"""
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from vxarchive.core.archive_engine import ArchiveEngine, ArchiveItem
from vxarchive.core.license_manager import LicenseManager
from vxarchive.core.benchmark import VXArchiveBenchmark
from vxarchive.core.hasher import HashEngine
from vxarchive.core.dedup_analyzer import DuplicateAnalyzer
from vxarchive.core.batch_processor import BatchProcessor
from vxarchive.core.password_vault import PasswordVault
from vxarchive.core.shell_integration import ShellIntegration

# 10 New Pro Engines
from vxarchive.core.shredder import SecureShredder
from vxarchive.core.transcoder import ArchiveTranscoder
from vxarchive.core.steganography import ArchiveSteganography
from vxarchive.core.diff_sync import ArchiveDiffSync
from vxarchive.core.splitter import VolumeSplitter, MultiVolumeDetector
from vxarchive.core.threat_scanner import ThreatScanner
from vxarchive.core.archive_repair import ArchiveRepairEngine
from vxarchive.core.bookmarks import BookmarkManager
from vxarchive.core.iso_mounter import IsoMounter
from vxarchive.core.metadata_inspector import MetadataInspector

# 3 New Suggestions: Grep, SFX, LAN Share
from vxarchive.core.archive_grep import ArchiveGrepEngine
from vxarchive.core.sfx_builder import SFXBuilder
from vxarchive.core.lan_share import LANShareServer
from vxarchive.core.sanitizer import ArchiveSanitizer


class TestVXArchiveProSuite(unittest.TestCase):
    def setUp(self):
        self.engine = ArchiveEngine()
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.test_dir.name

        # Create dummy test files
        self.file1 = os.path.join(self.base_dir, "test1.txt")
        with open(self.file1, "w", encoding="utf-8") as f:
            f.write("VXArchive test sample document 1\n" * 50)

        # Duplicate of file 1
        self.file1_dup = os.path.join(self.base_dir, "test1_copy.txt")
        with open(self.file1_dup, "w", encoding="utf-8") as f:
            f.write("VXArchive test sample document 1\n" * 50)

        self.sub_dir = os.path.join(self.base_dir, "subfolder")
        os.makedirs(self.sub_dir, exist_ok=True)
        self.file2 = os.path.join(self.sub_dir, "test2.txt")
        with open(self.file2, "w", encoding="utf-8") as f:
            f.write("VXArchive nested file 2\n" * 100)

        # Junk file
        self.junk_file = os.path.join(self.base_dir, "Thumbs.db")
        with open(self.junk_file, "wb") as f:
            f.write(b"\x00" * 1024)

    def tearDown(self):
        self.test_dir.cleanup()

    # --- Core & Diagnostics ---

    def test_hasher_engine(self):
        hashes = HashEngine.calculate_hashes(self.file1)
        self.assertIn("CRC32", hashes)
        self.assertIn("MD5", hashes)
        self.assertIn("SHA-1", hashes)
        self.assertIn("SHA-256", hashes)
        self.assertIn("SHA-512", hashes)

        res_match = HashEngine.compare_hash(hashes["SHA-256"], hashes)
        self.assertTrue(res_match["matched"])
        self.assertEqual(res_match["detected_algo"], "SHA-256")

        res_mismatch = HashEngine.compare_hash("E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855", hashes)
        self.assertFalse(res_mismatch["matched"])

    def test_dedup_analyzer(self):
        items = [
            ArchiveItem(path="a.txt", name="a.txt", is_dir=False, size=500, packed_size=200, mtime="", crc="12345678", attributes="...A"),
            ArchiveItem(path="b.txt", name="b.txt", is_dir=False, size=500, packed_size=200, mtime="", crc="12345678", attributes="...A"),
            ArchiveItem(path="c.txt", name="c.txt", is_dir=False, size=1000, packed_size=400, mtime="", crc="87654321", attributes="...A"),
            ArchiveItem(path="Thumbs.db", name="Thumbs.db", is_dir=False, size=1024, packed_size=100, mtime="", crc="AABBCCDD", attributes="...A")
        ]
        res = DuplicateAnalyzer.analyze_archive_items(items)
        self.assertEqual(res["duplicate_groups_count"], 1)
        self.assertEqual(res["total_duplicate_files"], 1)
        self.assertEqual(res["total_wasted_bytes"], 500)
        self.assertEqual(res["junk_count"], 1)

    def test_batch_processor(self):
        proc = BatchProcessor(self.engine)
        out_dir = os.path.join(self.base_dir, "batch_out")
        comp_res = proc.batch_compress_separate(
            source_paths=[self.file1, self.file2],
            output_dir=out_dir,
            archive_format="zip"
        )
        self.assertEqual(len(comp_res), 2)
        self.assertTrue(all(r["success"] for r in comp_res))

        archives = [r["archive"] for r in comp_res]
        for a in archives:
            self.assertTrue(os.path.isfile(a))

        extract_dir = os.path.join(self.base_dir, "batch_extracted")
        ext_res = proc.batch_extract(
            archive_paths=archives,
            base_dest_dir=extract_dir,
            extract_to_subfolders=True
        )
        self.assertEqual(len(ext_res), 2)
        self.assertTrue(all(r["success"] for r in ext_res))

    def test_password_vault(self):
        vault = PasswordVault.get_instance()
        vault.add_password("TestKey", "SuperSecret123!")
        items = vault.get_all()
        found = next((item for item in items if item["label"] == "TestKey"), None)
        self.assertIsNotNone(found)
        self.assertEqual(found["password"], "SuperSecret123!")
        vault.remove_password("TestKey")
        items_after = vault.get_all()
        self.assertIsNone(next((item for item in items_after if item["label"] == "TestKey"), None))

    def test_shell_integration_reg_gen(self):
        reg_file = os.path.join(self.base_dir, "test_vxarchive.reg")
        ShellIntegration.generate_reg_file(reg_file)
        self.assertTrue(os.path.isfile(reg_file))
        with open(reg_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Windows Registry Editor Version 5.00", content)
        self.assertIn("VXArchive.DarkGlass.Archive", content)
        self.assertIn("Extract here", content)
        self.assertIn("Extract to subfolder", content)
        self.assertIn("Add to archive with VXArchive...", content)

    def test_shell_integration_lifecycle_and_status(self):
        # Test status inspect
        status = ShellIntegration.get_status()
        self.assertIn("is_registered", status)
        self.assertIn("cascaded", status)
        self.assertIn("associated_extensions", status)
        self.assertIn("is_admin", status)

        # Test registration with cascaded = True
        ok, msg = ShellIntegration.register_associations(extensions=[".zip", ".rar", ".7z"], config={"cascaded": True})
        self.assertTrue(ok)
        self.assertIn("Cascaded Submenu", msg)

        status_cascaded = ShellIntegration.get_status()
        self.assertTrue(status_cascaded["is_registered"])
        self.assertTrue(status_cascaded["cascaded"])
        self.assertIn(".zip", status_cascaded["associated_extensions"])
        self.assertIn(".rar", status_cascaded["associated_extensions"])

        # Test registration with cascaded = False (Flat context menu)
        ok_flat, msg_flat = ShellIntegration.register_associations(extensions=[".zip"], config={"cascaded": False})
        self.assertTrue(ok_flat)
        self.assertIn("Flat Context Menu", msg_flat)

        # Test unregistration
        ok_unreg, msg_unreg = ShellIntegration.unregister_associations()
        self.assertTrue(ok_unreg)

        # Re-register default for clean state
        ShellIntegration.register_associations(config={"cascaded": True})

    def test_shell_integration_shortcuts(self):
        desktop_dirs = ShellIntegration.get_desktop_paths()
        self.assertTrue(len(desktop_dirs) > 0)
        start_dirs = ShellIntegration.get_start_menu_paths()
        self.assertTrue(len(start_dirs) > 0)

        ok, msg = ShellIntegration.create_shortcuts(desktop=True, start_menu=True)
        self.assertTrue(ok, msg)
        self.assertIn("shortcut(s)", msg)

        # Check that shortcut exists in at least one desktop and start menu
        has_desk = any(os.path.isfile(os.path.join(d, "VXArchive.lnk")) for d in desktop_dirs)
        self.assertTrue(has_desk)
        has_start = any(os.path.isfile(os.path.join(s, "VXArchive.lnk")) for s in start_dirs)
        self.assertTrue(has_start)

    def test_cli_quick_compress_and_extract(self):
        from vxarchive.main import handle_quick_compress, handle_extract
        sample_file = os.path.join(self.base_dir, "cli_sample.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("Quick compress CLI test payload for VXArchive shell integration")

        # Quick compress to zip (-az)
        ret_zip = handle_quick_compress(sample_file, format_ext="zip")
        self.assertEqual(ret_zip, 0)
        expected_zip = os.path.join(self.base_dir, "cli_sample.zip")
        self.assertTrue(os.path.isfile(expected_zip))

        # Quick compress to 7z (-a7)
        ret_7z = handle_quick_compress(sample_file, format_ext="7z")
        self.assertEqual(ret_7z, 0)
        expected_7z = os.path.join(self.base_dir, "cli_sample.7z")
        self.assertTrue(os.path.isfile(expected_7z))

        # Extract into subfolder (-xd)
        ret_ext = handle_extract(expected_zip, into_subfolder=True)
        self.assertEqual(ret_ext, 0)
        extracted_file = os.path.join(self.base_dir, "cli_sample", "cli_sample.txt")
        self.assertTrue(os.path.isfile(extracted_file))
        with open(extracted_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Quick compress CLI test payload for VXArchive shell integration")

    def test_benchmark_engine(self):
        bench = VXArchiveBenchmark(multithreading=False, update_interval=0.05)
        bench.start()
        import time
        for _ in range(20):
            if bench.total_bytes > 0:
                break
            time.sleep(0.1)
        bench.stop()
        self.assertTrue(bench.total_bytes > 0)
        self.assertEqual(bench.errors, 0)

    def test_license_manager(self):
        mgr = LicenseManager.get_instance()
        reg_ok = mgr.register("VXArchive Enterprise", "KEY-12345")
        self.assertTrue(reg_ok)
        self.assertTrue(mgr.is_registered)

    # --- 10 NEW PRO SUITE ENGINES ---

    def test_feature_1_shredder(self):
        dummy_secret = os.path.join(self.base_dir, "classified.txt")
        with open(dummy_secret, "w") as f:
            f.write("CONFIDENTIAL TOP SECRET " * 50)
        self.assertTrue(os.path.exists(dummy_secret))

        ok = SecureShredder.shred_file(dummy_secret, passes=3)
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(dummy_secret))

    def test_feature_2_transcoder(self):
        # Create a source ZIP
        src_zip = os.path.join(self.base_dir, "source.zip")
        with zipfile.ZipFile(src_zip, "w") as zf:
            zf.write(self.file1, arcname="test1.txt")

        dest_tar = os.path.join(self.base_dir, "transcoded.tar")
        transcoder = ArchiveTranscoder(self.engine)
        ok, msg = transcoder.convert(src_zip, target_format="tar", output_path=dest_tar)
        self.assertTrue(ok, msg)
        self.assertTrue(os.path.isfile(dest_tar))

    def test_feature_3_steganography(self):
        # Create a carrier image (minimal PNG)
        png_path = os.path.join(self.base_dir, "carrier.png")
        # 1x1 transparent PNG bytes
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        with open(png_path, "wb") as f:
            f.write(png_data)

        # Create secret archive
        sec_zip = os.path.join(self.base_dir, "secret.zip")
        with zipfile.ZipFile(sec_zip, "w") as zf:
            zf.writestr("secret.txt", "TOP SECRET PAYLOAD")

        out_stego = os.path.join(self.base_dir, "stego_output.png")
        ok, msg = ArchiveSteganography.hide_archive_in_image(png_path, sec_zip, out_stego)
        self.assertTrue(ok, msg)
        self.assertTrue(os.path.isfile(out_stego))

        # Test detection & extraction
        has_hid, arc_type, offset = ArchiveSteganography.detect_hidden_archive(out_stego)
        self.assertTrue(has_hid)
        self.assertEqual(arc_type, "ZIP")
        self.assertTrue(offset > 0)

        extracted_zip = os.path.join(self.base_dir, "recovered_secret.zip")
        ex_ok, ex_msg = ArchiveSteganography.extract_hidden_archive(out_stego, extracted_zip)
        self.assertTrue(ex_ok, ex_msg)
        self.assertTrue(os.path.isfile(extracted_zip))

    def test_feature_4_diff_sync(self):
        # Create an archive with test1.txt
        arc_path = os.path.join(self.base_dir, "diff_arc.zip")
        with zipfile.ZipFile(arc_path, "w") as zf:
            zf.write(self.file1, arcname="test1.txt")

        # In folder, we have test1.txt (identical) and test1_copy.txt (new in folder)
        diff = ArchiveDiffSync(self.engine)
        results = diff.compare(arc_path, self.base_dir)
        self.assertTrue(len(results) > 0)
        statuses = {item.rel_path: item.status for item in results}
        self.assertIn("test1.txt", statuses)
        self.assertEqual(statuses["test1.txt"], "IDENTICAL")

        # Test real synchronization
        sync_ok = diff.sync_to_archive(arc_path, self.base_dir, results)
        self.assertTrue(sync_ok)
        with zipfile.ZipFile(arc_path, "r") as zf:
            names = zf.namelist()
            self.assertIn("test1.txt", names)
            self.assertIn("test1_copy.txt", names)

    def test_real_archive_operations(self):
        # 1. Test real archive deletion
        del_zip = os.path.join(self.base_dir, "test_del.zip")
        with zipfile.ZipFile(del_zip, "w") as zf:
            zf.write(self.file1, arcname="keep_me.txt")
            zf.write(self.file2, arcname="delete_me.txt")

        ok_del, msg_del = self.engine.delete_items_from_archive(del_zip, ["delete_me.txt"])
        self.assertTrue(ok_del, msg_del)
        with zipfile.ZipFile(del_zip, "r") as zf:
            names = zf.namelist()
            self.assertIn("keep_me.txt", names)
            self.assertNotIn("delete_me.txt", names)

        # 2. Test real archive comment
        ok_comm, msg_comm = self.engine.set_comment(del_zip, "Verified Real Archive Comment")
        self.assertTrue(ok_comm, msg_comm)
        read_comm = self.engine.get_comment(del_zip)
        self.assertEqual(read_comm, "Verified Real Archive Comment")

        # 3. Test real cryptographic recovery record
        ok_rec, msg_rec, rec_path = self.engine.create_recovery_record(del_zip, redundancy_percent=5)
        self.assertTrue(ok_rec, msg_rec)
        self.assertTrue(os.path.isfile(rec_path))
        import json
        with open(rec_path, "r", encoding="utf-8") as f:
            rec_data = json.load(f)
        self.assertIn("parity_sha256", rec_data)
        self.assertTrue(rec_data["slice_count"] > 0)

    def test_feature_5_splitter(self):
        # Create a 200KB file
        large_file = os.path.join(self.base_dir, "large.bin")
        payload = b"VXArchiveSplitterBlock1234567890" * 6000  # ~192 KB
        with open(large_file, "wb") as f:
            f.write(payload)

        # Split into 50KB chunks
        out_split_dir = os.path.join(self.base_dir, "parts")
        parts = VolumeSplitter.split_file(large_file, chunk_size_bytes=50 * 1024, output_dir=out_split_dir)
        self.assertTrue(len(parts) >= 3)
        for p in parts:
            self.assertTrue(os.path.isfile(p))

        # Join parts back
        rejoined = os.path.join(self.base_dir, "rejoined.bin")
        ok, msg = VolumeSplitter.join_volumes(parts[0], output_file=rejoined)
        self.assertTrue(ok, msg)
        self.assertEqual(os.path.getsize(rejoined), len(payload))

    def test_multi_volume_detector_and_missing_locator(self):
        mv_dir = os.path.join(self.base_dir, "mv_test")
        os.makedirs(mv_dir, exist_ok=True)

        # Create simulated multi-volume RAR: part1, part2, part4 (part3 missing)
        p1 = os.path.join(mv_dir, "game.part1.rar")
        p2 = os.path.join(mv_dir, "game.part2.rar")
        p4 = os.path.join(mv_dir, "game.part4.rar")
        for p in [p1, p2, p4]:
            with open(p, "wb") as f:
                f.write(b"VOL_CHUNK_DATA" * 50)

        # 1. Detection
        self.assertTrue(MultiVolumeDetector.is_multi_volume_file(p1))
        self.assertTrue(MultiVolumeDetector.is_multi_volume_file("backup.7z.001"))

        # 2. Sequence inspection
        vset = MultiVolumeDetector.inspect_volume_set(p1)
        self.assertIsNotNone(vset)
        self.assertEqual(vset.total_parts, 4)
        self.assertFalse(vset.is_complete)
        self.assertEqual(len(vset.missing_parts), 1)
        self.assertEqual(vset.missing_parts[0].expected_name, "game.part3.rar")

        # 3. Relocate missing part from an external location
        external_dir = os.path.join(self.base_dir, "external_downloads")
        os.makedirs(external_dir, exist_ok=True)
        missing_source = os.path.join(external_dir, "downloaded_game_p3.rar")
        with open(missing_source, "wb") as f:
            f.write(b"VOL_CHUNK_DATA" * 50)

        ok_reloc, dest_p = MultiVolumeDetector.relocate_part(
            missing_part=vset.missing_parts[0],
            chosen_source_path=missing_source,
            target_folder=mv_dir,
            method="copy"
        )
        self.assertTrue(ok_reloc)
        self.assertTrue(os.path.isfile(dest_p))
        self.assertEqual(os.path.basename(dest_p), "game.part3.rar")

        # 4. Re-inspect: now sequence should be 100% complete
        vset_after = MultiVolumeDetector.inspect_volume_set(p1)
        self.assertTrue(vset_after.is_complete)
        self.assertEqual(len(vset_after.missing_parts), 0)

    def test_feature_6_threat_scanner(self):
        # Test suspicious double extension
        deceptive_item = ArchiveItem(
            path="salary_invoice.pdf.exe", name="salary_invoice.pdf.exe",
            is_dir=False, size=1000, packed_size=100, mtime="", crc="", attributes=""
        )
        safe_item = ArchiveItem(
            path="readme.txt", name="readme.txt",
            is_dir=False, size=500, packed_size=200, mtime="", crc="", attributes=""
        )

        rep = ThreatScanner.scan_archive_items([deceptive_item, safe_item])
        self.assertEqual(rep.risk_level, "CRITICAL")
        self.assertTrue(len(rep.threats) >= 1)
        threat_types = [t["type"] for t in rep.threats]
        self.assertIn("Deceptive Double Extension", threat_types)

    def test_feature_7_repair(self):
        # Corrupt an archive header
        corrupt_zip = os.path.join(self.base_dir, "corrupt.zip")
        with open(corrupt_zip, "wb") as f:
            f.write(b"DAMAGED_DATA_HEADER" * 100)

        out_salvage = os.path.join(self.base_dir, "repaired.zip")
        repair_engine = ArchiveRepairEngine(self.engine)
        ok, msg, recovered = repair_engine.repair_archive(corrupt_zip, out_salvage)
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(msg, str)
        self.assertIsInstance(recovered, list)

    def test_feature_8_bookmarks(self):
        mgr = BookmarkManager.get_instance()
        initial_len = len(mgr.bookmarks)
        mgr.add_bookmark("Main Workspace Test", self.base_dir, tag="Projects", is_archive=False)
        self.assertEqual(len(mgr.bookmarks), initial_len + 1)
        last_b = mgr.bookmarks[-1]
        self.assertEqual(last_b["name"], "Main Workspace Test")
        self.assertEqual(last_b["tag"], "Projects")

        mgr.remove_bookmark(len(mgr.bookmarks) - 1)
        self.assertEqual(len(mgr.bookmarks), initial_len)

    def test_feature_9_iso_mounter(self):
        # Test nonexistent image fails cleanly with descriptive message
        ok, msg = IsoMounter.mount_image("C:\\invalid_fake_image.iso")
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())

        ok_dis, msg_dis = IsoMounter.dismount_image("C:\\invalid_fake_image.iso")
        self.assertFalse(ok_dis)
        self.assertIn("not found", msg_dis.lower())

    def test_feature_10_metadata_inspector(self):
        # Test text file inspection
        data = b"Line 1: Hello World\nLine 2: VXArchive Pro Edition\nLine 3: Clean minimal design\n"
        meta = MetadataInspector.inspect("notes.txt", data)
        self.assertEqual(meta["Category"], "Text / Source Code")
        self.assertEqual(meta["Total Lines"], "3")
        self.assertIn("bytes", meta["File Size"])

    def test_feature_11_deep_grep(self):
        grep_zip = os.path.join(self.base_dir, "grep_test.zip")
        with zipfile.ZipFile(grep_zip, "w") as zf:
            zf.writestr("app/config.py", "DEBUG = True\nAPI_KEY = 'VX_TOP_SECRET_999'\nPORT = 8080\n")
            zf.writestr("readme.txt", "VXArchive Documentation\nVersion 2.0\n")

        engine = ArchiveGrepEngine()
        matches = engine.search(grep_zip, query="VX_TOP_SECRET_999", is_regex=False)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].file_path, "app/config.py")
        self.assertEqual(matches[0].line_number, 2)
        self.assertIn("VX_TOP_SECRET_999", matches[0].line_content)

    def test_feature_12_sfx_builder(self):
        sfx_out = os.path.join(self.base_dir, "standalone_app.exe")
        builder = SFXBuilder()
        ok, msg = builder.build_sfx(
            sources=self.file1,
            output_exe_path=sfx_out,
            title="VXArchive Self-Extracting Test",
            extract_path="%%TEMP%%",
            silent=True
        )
        self.assertTrue(ok, msg)
        self.assertTrue(os.path.isfile(sfx_out))
        # SFX module is ~215KB + payload
        self.assertTrue(os.path.getsize(sfx_out) > 200 * 1024)

    def test_feature_13_lan_share(self):
        import urllib.request
        server = LANShareServer(self.file1)
        ok, url = server.start()
        self.assertTrue(ok, url)
        self.assertTrue(server.is_running)

        # Download from micro-server
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read()
            with open(self.file1, "rb") as f:
                expected = f.read()
            self.assertEqual(content, expected)

        server.stop()
        self.assertFalse(server.is_running)

    def test_archive_health_checker(self):
        from vxarchive.core.health_checker import ArchiveHealthChecker
        checker = ArchiveHealthChecker()

        # 1. Healthy archive
        healthy_zip = os.path.join(self.base_dir, "health_healthy.zip")
        with zipfile.ZipFile(healthy_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("clean1.txt", "Healthy file 1 contents")
            zf.writestr("clean2.txt", "Healthy file 2 contents")

        rep = checker.check_health(healthy_zip)
        self.assertTrue(rep.is_healthy)
        self.assertEqual(rep.health_percentage, 100.0)
        self.assertEqual(rep.corrupted_count, 0)
        self.assertEqual(len(rep.file_records), 2)
        self.assertEqual(rep.file_records[0].status, "OK")

        # 2. Corrupt archive
        corrupt_zip = os.path.join(self.base_dir, "health_corrupt.zip")
        with open(healthy_zip, "rb") as f:
            data = bytearray(f.read())
        pos = data.find(b"clean1.txt") + 20
        data[pos] ^= 0xFF
        with open(corrupt_zip, "wb") as f:
            f.write(data)

        rep_bad = checker.check_health(corrupt_zip)
        self.assertFalse(rep_bad.is_healthy)
        self.assertTrue(rep_bad.corrupted_count > 0)
        self.assertTrue(rep_bad.health_percentage < 100.0)

    def test_archive_sanitizer_engine(self):
        sanitizer = ArchiveSanitizer()

        # 1. Build a mock messy/bloated archive
        dirty_zip = os.path.join(self.base_dir, "messy_source.zip")
        with zipfile.ZipFile(dirty_zip, "w") as zf:
            # Ghost & junk files
            zf.writestr("__MACOSX/._invoice.pdf", b"MAC_RESOURCE_FORK" * 10)
            zf.writestr(".DS_Store", b"MAC_DESKTOP_DB" * 20)
            zf.writestr("Thumbs.db", b"THUMBS_CACHE" * 30)
            zf.writestr("desktop.ini", b"[.ShellClassInfo]\nIconResource=...")
            zf.writestr("project/__pycache__/app.cpython-312.pyc", b"BYTECODE" * 50)
            zf.writestr(".vscode/settings.json", b'{"editor.tabSize": 4}')
            zf.writestr("temp_output.tmp", b"TEMP_BUFFER" * 40)
            # Duplicate files
            dup_content = b"IDENTICAL_PAYLOAD_DATA_1234567890" * 50
            zf.writestr("docs/manual.pdf", dup_content)
            zf.writestr("backup/manual_copy.pdf", dup_content)
            # Real clean content
            zf.writestr("src/main.py", b"print('Hello VXArchive')\n")
            zf.writestr("README.md", b"# VXArchive Clean Project\n")

        # 2. Analyze the archive
        report = sanitizer.analyze(dirty_zip)
        self.assertTrue(report.total_junk_count >= 7)
        self.assertTrue(report.waste_bytes > 0)
        self.assertTrue(report.waste_percentage > 0)

        # Check category categorizations
        categories = {j.category for j in report.junk_items}
        self.assertIn("OS Ghost Files", categories)
        self.assertIn("Development Caches", categories)
        self.assertIn("IDE & Editor Clutter", categories)
        self.assertIn("Temporary & Backup Files", categories)
        self.assertIn("Duplicate Payloads", categories)

        # 3. Create Sanitized Archive
        clean_zip = os.path.join(self.base_dir, "sanitized_clean.zip")
        junk_paths = [j.path for j in report.junk_items]
        ok, msg, created = sanitizer.create_sanitized_archive(
            dirty_zip, clean_zip, remove_paths=junk_paths
        )
        self.assertTrue(ok, msg)
        self.assertTrue(os.path.isfile(clean_zip))

        # Verify inside clean_zip: only real clean files remain
        with zipfile.ZipFile(clean_zip, "r") as zf_clean:
            cleaned_names = zf_clean.namelist()
            for ghost in ["__MACOSX/._invoice.pdf", ".DS_Store", "Thumbs.db", "desktop.ini", "project/__pycache__/app.cpython-312.pyc", "temp_output.tmp"]:
                self.assertNotIn(ghost, cleaned_names)
            # Real files remain intact
            self.assertIn("src/main.py", cleaned_names)
            self.assertIn("README.md", cleaned_names)

        # 4. Smart Extract
        extract_target = os.path.join(self.base_dir, "smart_extracted")
        ok_ext, out_dir, pruned_count = sanitizer.smart_extract(
            dirty_zip, target_dir=extract_target, strip_junk=True
        )
        self.assertTrue(ok_ext)
        self.assertTrue(os.path.isdir(out_dir))
        self.assertTrue(pruned_count >= 6)
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "src", "main.py")))
        self.assertFalse(os.path.exists(os.path.join(out_dir, ".DS_Store")))

    def test_security_zip_slip_and_utils(self):
        from vxarchive.core.utils import is_safe_path, format_size, get_app_data_dir

        self.assertEqual(format_size(500), "500 B")
        self.assertIn("KB", format_size(2048))
        self.assertIn("MB", format_size(5 * 1024 * 1024))
        self.assertIn("GB", format_size(3 * 1024 * 1024 * 1024))

        data_dir = get_app_data_dir()
        self.assertTrue(data_dir.exists())

        base = os.path.abspath(self.base_dir)
        self.assertTrue(is_safe_path(base, "folder/file.txt"))
        self.assertTrue(is_safe_path(base, "file.txt"))
        self.assertFalse(is_safe_path(base, "../evil.exe"))
        self.assertFalse(is_safe_path(base, "../../Windows/System32/evil.dll"))
        self.assertFalse(is_safe_path(base, "..\\..\\evil.bat"))

    def test_archive_password_memory_and_pattern_matching(self):
        from vxarchive.core.password_memory import ArchivePasswordMemory

        mem = ArchivePasswordMemory()
        # Clean state for isolated test
        mem.exact_files.clear()
        mem.patterns.clear()

        # 1. Pattern extraction
        p1 = mem.extract_pattern_candidates("[kuyhaa.me]galaxy.rar")
        self.assertIn("[kuyhaa.me]*", p1)

        p2 = mem.extract_pattern_candidates("(gigapurbalingga)windows.zip")
        self.assertIn("(gigapurbalingga)*", p2)

        p3 = mem.extract_pattern_candidates("kuyhaa.me_autocad.rar")
        self.assertIn("kuyhaa.me*", p3)

        p4 = mem.extract_pattern_candidates("biggame.part1.rar")
        self.assertIn("biggame.part*.rar", p4)

        # 2. Pattern matching
        self.assertTrue(mem.match_pattern("[kuyhaa.me]*", "[kuyhaa.me]galaxy.rar"))
        self.assertTrue(mem.match_pattern("[kuyhaa.me]*", "[kuyhaa.me] milyway.rar"))
        self.assertTrue(mem.match_pattern("[kuyhaa.me]*", "D:\\Downloads\\[kuyhaa.me] other.rar"))
        self.assertFalse(mem.match_pattern("[kuyhaa.me]*", "different_file.rar"))

        # 3. Remember and Retrieve for exact file and pattern
        mem.remember_password(
            file_path="D:\\Downloads\\[kuyhaa.me]galaxy.rar",
            password="kuyhaa_pass_2026",
            remember_file=True,
            pattern="[kuyhaa.me]*"
        )

        # Lookup for second file: [kuyhaa.me] milyway.rar
        candidates = mem.get_candidates_for_file("C:\\Users\\User\\Downloads\\[kuyhaa.me] milyway.rar")
        self.assertTrue(len(candidates) >= 1)
        self.assertEqual(candidates[0][0], "kuyhaa_pass_2026")
        self.assertIn("[kuyhaa.me]*", candidates[0][1])

        # 4. Engine password verification and auto-unlock
        test_enc_zip = os.path.join(self.base_dir, "enc_test.zip")
        self.engine.create_archive(
            output_archive=test_enc_zip,
            files_to_add=[self.file1],
            archive_format="zip",
            password="test_secure_pwd"
        )
        self.assertTrue(os.path.isfile(test_enc_zip))

        # Check engine verify_password
        self.assertTrue(self.engine.verify_password(test_enc_zip, "test_secure_pwd"))
        self.assertFalse(self.engine.verify_password(test_enc_zip, "wrong_password_999"))

        # Remember for this test zip
        mem.remember_password(test_enc_zip, "test_secure_pwd", remember_file=True)
        found = self.engine.find_working_password(test_enc_zip)
        self.assertIsNotNone(found)
        self.assertEqual(found[0], "test_secure_pwd")

if __name__ == "__main__":
    unittest.main()

