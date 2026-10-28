"""
GUI smoke tests for VXArchive replica including all enhanced features:
- Multi-Tab archive browsing
- QuickLook Spacebar preview
- Donut storage chart
- Password Vault
- Shell integration & 7-Zip replacement
- All classic VXArchive dialogs
"""
import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from vxarchive.gui.main_window import VXArchiveMainWindow
from vxarchive.gui.dialog_add import ArchiveNameAndParametersDialog
from vxarchive.gui.dialog_extract import ExtractionPathAndOptionsDialog
from vxarchive.gui.dialog_view import InternalViewerDialog
from vxarchive.gui.dialog_info import ArchiveInfoDialog
from vxarchive.gui.dialog_benchmark import BenchmarkDialog
from vxarchive.gui.dialog_about import AboutVXArchiveDialog
from vxarchive.gui.dialog_eval import EvaluationDialog
from vxarchive.gui.dialog_find import FindFilesDialog
from vxarchive.gui.dialog_wizard import WizardDialog
from vxarchive.gui.dialog_password import PasswordDialog
from vxarchive.gui.dialog_progress import VXArchiveProgressDialog
from vxarchive.gui.dialog_hash import HashInspectorDialog
from vxarchive.gui.dialog_duplicates import DuplicateAnalyzerDialog
from vxarchive.gui.dialog_batch import BatchManagerDialog
from vxarchive.gui.dialog_quicklook import QuickLookDialog
from vxarchive.gui.dialog_chart import StorageChartDialog
from vxarchive.gui.dialog_vault import PasswordVaultDialog, PasswordEntryDialog
from vxarchive.gui.dialog_integration import SystemIntegrationDialog

# 10 Pro Dialogs
from vxarchive.gui.dialog_shredder import ShredderDialog
from vxarchive.gui.dialog_transcoder import TranscoderDialog
from vxarchive.gui.dialog_steganography import SteganographyDialog
from vxarchive.gui.dialog_diff_sync import DiffSyncDialog
from vxarchive.gui.dialog_splitter import VolumeSplitterDialog
from vxarchive.gui.dialog_threat_scanner import ThreatScannerDialog
from vxarchive.gui.dialog_repair import ArchiveRepairDialog
from vxarchive.gui.dialog_bookmarks import BookmarkHubDialog
from vxarchive.gui.dialog_iso import IsoMounterDialog
from vxarchive.gui.dialog_metadata import MetadataInspectorDialog

# 3 New Dialogs
from vxarchive.gui.dialog_grep import DeepGrepDialog
from vxarchive.gui.dialog_sfx import SFXStudioDialog
from vxarchive.gui.dialog_lan_share import LANShareDialog
from vxarchive.gui.dialog_missing_volume import MissingVolumeDialog
from vxarchive.gui.dialog_sanitizer import ArchiveSanitizerDialog
from vxarchive.gui.mica_effect import apply_windows_11_mica

class TestVXArchiveGUI(unittest.TestCase):
    def test_main_window_and_tabs(self):
        win = VXArchiveMainWindow(initial_path=os.getcwd())
        self.assertIsNotNone(win)
        self.assertEqual(win.tabs.count(), 1)
        # Add new tab
        idx = win.add_tab(os.getcwd())
        self.assertEqual(win.tabs.count(), 2)
        # Close tab
        win.close_tab(idx)
        self.assertEqual(win.tabs.count(), 1)
        win.close()

    def test_dialog_quicklook(self):
        dlg = QuickLookDialog(None, title="readme.txt", data=b"Sample QuickLook text content\nLine 2")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_chart(self):
        sample_items = [
            {"name": "file.zip", "size": 102400},
            {"name": "pic.png", "size": 204800},
            {"name": "doc.pdf", "size": 51200},
            {"name": "script.py", "size": 12800},
        ]
        dlg = StorageChartDialog(None, items=sample_items)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_vault(self):
        dlg = PasswordVaultDialog(None, is_select_mode=False)
        self.assertIsNotNone(dlg)
        self.assertTrue(hasattr(dlg, 'btn_add'))
        self.assertTrue(hasattr(dlg, 'btn_edit'))
        self.assertTrue(hasattr(dlg, 'btn_delete'))
        self.assertTrue(hasattr(dlg, 'btn_copy'))
        self.assertEqual(dlg.btn_add.text(), 'Add')
        self.assertEqual(dlg.btn_edit.text(), 'Edit')
        self.assertEqual(dlg.btn_delete.text(), 'Delete')

        entry_dlg = PasswordEntryDialog(None, mode='add', label='TestEntry', password='SecretPassword')
        lbl, pwd = entry_dlg.get_data()
        self.assertEqual(lbl, 'TestEntry')
        self.assertEqual(pwd, 'SecretPassword')
        entry_dlg.close()
        dlg.close()

    def test_dialog_integration(self):
        dlg = SystemIntegrationDialog(None)
        self.assertIsNotNone(dlg)
        self.assertEqual(dlg.tabs.count(), 3)
        self.assertTrue(dlg.chk_cascaded.isChecked())

        # Test preview update with cascaded toggle
        dlg.chk_cascaded.setChecked(False)
        self.assertIn("Flat Context Menu", dlg.lbl_preview_content.text())
        dlg.chk_cascaded.setChecked(True)
        self.assertIn("VXArchive", dlg.lbl_preview_content.text())

        # Test extension selection buttons
        dlg._clear_all_exts()
        self.assertFalse(any(chk.isChecked() for chk in dlg.ext_checkboxes.values()))
        dlg._select_common_exts()
        self.assertTrue(dlg.ext_checkboxes[".zip"].isChecked())
        self.assertTrue(dlg.ext_checkboxes[".7z"].isChecked())
        dlg._select_all_exts()
        self.assertTrue(all(chk.isChecked() for chk in dlg.ext_checkboxes.values()))

        # Test config dictionary extraction
        cfg = dlg._get_current_config()
        self.assertTrue(cfg["cascaded"])
        self.assertEqual(len(cfg["extensions"]), len(dlg.ext_checkboxes))
        self.assertTrue(cfg["enable_open"])
        self.assertTrue(cfg["enable_add_zip"])
        dlg.close()

    def test_dialog_progress(self):
        dlg = VXArchiveProgressDialog(None, title="Testing Progress", operation_type="Extracting")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_hash(self):
        dlg = HashInspectorDialog(None, file_path_or_data=b"Sample content for checksum test", display_name="sample.txt")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_duplicates(self):
        dlg = DuplicateAnalyzerDialog(None, archive_items=[], title="SampleArchive.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_batch(self):
        dlg = BatchManagerDialog(None, initial_archives=[], initial_sources=[])
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_add(self):
        dlg = ArchiveNameAndParametersDialog(None, default_archive_name="test.zip", files_to_add=["file.txt"])
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_extract(self):
        dlg = ExtractionPathAndOptionsDialog(None, default_dest="C:\\Temp", default_archive="test.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_view(self):
        dlg = InternalViewerDialog(None, title="readme.txt", data=b"Hello VXArchive 1:1 replica!")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_info(self):
        info = {
            "filename": "demo.rar",
            "type": "RAR archive",
            "total_files": 12,
            "total_folders": 2,
            "total_size": 102400,
            "total_packed": 45000,
            "ratio": 43.9,
            "is_solid": True,
            "has_comment": False
        }
        dlg = ArchiveInfoDialog(None, info=info)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_benchmark(self):
        dlg = BenchmarkDialog(None)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_about(self):
        dlg = AboutVXArchiveDialog(None)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_eval(self):
        dlg = EvaluationDialog(None)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_find(self):
        dlg = FindFilesDialog(None, items=[])
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_wizard(self):
        dlg = WizardDialog(None)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_password(self):
        dlg = PasswordDialog(None, is_prompt_mode=False)
        self.assertIsNotNone(dlg)
        dlg.close()

        dlg_prompt = PasswordDialog(None, is_prompt_mode=True, archive_name="[kuyhaa.me]galaxy.rar")
        self.assertIsNotNone(dlg_prompt)
        self.assertTrue(hasattr(dlg_prompt, "remember_file_chk"))
        self.assertTrue(hasattr(dlg_prompt, "remember_pattern_chk"))
        self.assertIn("[kuyhaa.me]*", dlg_prompt.remember_pattern_chk.text())
        dlg_prompt.close()

    # 10 New Pro Dialog Tests
    def test_dialog_shredder(self):
        dlg = ShredderDialog(None, initial_files=["test.txt"])
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_transcoder(self):
        dlg = TranscoderDialog(None, initial_archive="test.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_steganography(self):
        dlg = SteganographyDialog(None)
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_diff_sync(self):
        dlg = DiffSyncDialog(None, initial_archive="test.zip", initial_folder="C:\\")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_splitter(self):
        dlg = VolumeSplitterDialog(None, initial_file="test.bin")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_threat_scanner(self):
        dlg = ThreatScannerDialog(None, archive_items=[], archive_name="sample.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_repair(self):
        dlg = ArchiveRepairDialog(None, initial_archive="corrupt.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_bookmarks(self):
        dlg = BookmarkHubDialog(None, current_path="C:\\")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_iso(self):
        dlg = IsoMounterDialog(None, initial_iso="image.iso")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_metadata(self):
        dlg = MetadataInspectorDialog(None, file_name="notes.txt", raw_data=b"Sample notes data")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_grep(self):
        dlg = DeepGrepDialog(None, archive_path="")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_sfx(self):
        dlg = SFXStudioDialog(None, initial_source="sample.zip")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_lan_share(self):
        dlg = LANShareDialog(None, file_path="")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_missing_volume(self):
        dlg = MissingVolumeDialog(None, volume_set=None, initial_file="test.part1.rar")
        self.assertIsNotNone(dlg)
        dlg.close()

    def test_dialog_health(self):
        from vxarchive.gui.dialog_health import ArchiveHealthDialog
        dlg = ArchiveHealthDialog(None, archive_path="")
        self.assertIsNotNone(dlg)
        self.assertIsNotNone(dlg.table)
        self.assertEqual(dlg.table.columnCount(), 6)
        dlg.close()

    def test_dialog_diagnostic(self):
        from vxarchive.gui.dialog_diagnostic import ExtractionDiagnosticDialog
        dlg = ExtractionDiagnosticDialog(
            None,
            archive_path="Bully.7z",
            dest_dir=os.getcwd(),
            error_message="ERROR: Data Error : Bully.iso\nERROR: Data Error : readme.html"
        )
        self.assertIsNotNone(dlg)
        self.assertEqual(len(dlg.error_items), 2)
        self.assertEqual(dlg.error_items[0]["file"], "Bully.iso")
        self.assertEqual(dlg.error_items[0]["type"], "Data Error")
        self.assertEqual(dlg.error_items[1]["file"], "readme.html")
        self.assertEqual(dlg.table.rowCount(), 2)
        dlg.close()

    def test_dialog_sanitizer(self):
        dlg = ArchiveSanitizerDialog(None, archive_path="")
        self.assertIsNotNone(dlg)
        self.assertIsNotNone(dlg.table)
        self.assertEqual(dlg.table.columnCount(), 5)
        self.assertIsNotNone(dlg.btn_purge)
        self.assertIsNotNone(dlg.btn_smart_extract)
        dlg.close()

    def test_navigation_history(self):
        win = VXArchiveMainWindow(initial_path=os.getcwd())
        tab = win.current_tab
        self.assertIsNotNone(tab)
        self.assertFalse(tab.can_go_back())
        self.assertFalse(tab.can_go_forward())

        parent = os.path.dirname(os.getcwd())
        tab.navigate_to_folder(parent)
        self.assertTrue(tab.can_go_back())
        self.assertFalse(tab.can_go_forward())

        win._action_back()
        self.assertEqual(tab.current_folder_path, os.getcwd())
        self.assertTrue(tab.can_go_forward())

        win._action_forward()
        self.assertEqual(tab.current_folder_path, parent)
        win.close()

    def test_windows_11_mica_effect(self):
        from PyQt6.QtWidgets import QWidget
        test_widget = QWidget()
        res = apply_windows_11_mica(test_widget, backdrop_type="mica_alt", dark_mode=True, rounded_corners=True)
        self.assertIsInstance(res, bool)
        test_widget.close()

if __name__ == "__main__":
    unittest.main()
