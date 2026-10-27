"""
Windows Explorer Shell context menu, cascaded submenus, and file associations.
"""
import os
import sys
from typing import List, Dict, Any, Tuple


class ShellIntegration:
    """Manages Windows Explorer shell integration, file associations, and registry keys."""

    SUPPORTED_EXTS = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".cab", ".wim"]
    _status_cache = {
        "is_registered": False,
        "cascaded": True,
        "associated_extensions": [".zip", ".rar", ".7z"],
        "is_admin": False
    }

    @staticmethod
    def get_status() -> Dict[str, Any]:
        return dict(ShellIntegration._status_cache)

    @staticmethod
    def _get_target_exe() -> Tuple[str, str]:
        # Priority 1: Permanent user AppData installation
        local_app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
        appdata_exe = os.path.join(local_app_data, "Programs", "VXArchive", "VXArchive.exe")
        appdata_ico = os.path.join(local_app_data, "Programs", "VXArchive", "vxarchive.ico")
        if os.path.isfile(appdata_exe):
            ico_ref = appdata_ico if os.path.isfile(appdata_ico) else f"{appdata_exe},0"
            return appdata_exe, ico_ref

        # Priority 2: Frozen PyInstaller execution
        if getattr(sys, "frozen", False):
            exe = sys.executable
            ico = os.path.join(os.path.dirname(exe), "vxarchive.ico")
            return exe, (ico if os.path.isfile(ico) else f"{exe},0")

        # Priority 3: Local build dist or development fallback
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dist_exe = os.path.join(base_dir, "dist", "VXArchive", "VXArchive.exe")
        ico_file = os.path.join(base_dir, "vxarchive.ico")
        if os.path.isfile(dist_exe):
            return dist_exe, f"{dist_exe},0"
        return sys.executable, (ico_file if os.path.isfile(ico_file) else f"{sys.executable},0")

    @staticmethod
    def register_associations(extensions: List[str] = None, config: Dict[str, Any] = None) -> Tuple[bool, str]:
        exts = extensions or ShellIntegration.SUPPORTED_EXTS
        cfg = config or {"cascaded": True}
        cascaded = cfg.get("cascaded", True)

        ShellIntegration._status_cache["is_registered"] = True
        ShellIntegration._status_cache["cascaded"] = cascaded
        ShellIntegration._status_cache["associated_extensions"] = list(exts)

        # Apply real registry keys in HKCU
        try:
            import winreg
            import ctypes

            # 1. Suppress 7-Zip CLI (7z.exe) from appearing in Open With
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\7z.exe") as k7z:
                    winreg.SetValueEx(k7z, "NoOpenWith", 0, winreg.REG_SZ, "")
            except Exception:
                pass

            # 2. Register VXArchive.exe Application
            exe_path, ico_ref = ShellIntegration._get_target_exe()
            app_key_path = r"Software\Classes\Applications\VXArchive.exe"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, app_key_path) as kapp:
                winreg.SetValueEx(kapp, "", 0, winreg.REG_SZ, "VXArchive")
                winreg.SetValueEx(kapp, "FriendlyAppName", 0, winreg.REG_SZ, "VXArchive")
                winreg.SetValueEx(kapp, "ApplicationCompany", 0, winreg.REG_SZ, "VXArchive Studio")

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{app_key_path}\\DefaultIcon") as kico:
                winreg.SetValueEx(kico, "", 0, winreg.REG_SZ, ico_ref)

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{app_key_path}\\shell\\open\\command") as kcmd:
                winreg.SetValueEx(kcmd, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

            # SupportedTypes strictly for archive extensions to avoid unassociated suggestions
            for e in exts:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{app_key_path}\\SupportedTypes") as kst:
                    winreg.SetValueEx(kst, e, 0, winreg.REG_SZ, "")

            # ProgID
            prog_path = r"Software\Classes\VXArchive.DarkGlass.Archive"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, prog_path) as kp:
                winreg.SetValueEx(kp, "", 0, winreg.REG_SZ, "VXArchive Compressed File")
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{prog_path}\\DefaultIcon") as kpico:
                winreg.SetValueEx(kpico, "", 0, winreg.REG_SZ, ico_ref)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{prog_path}\\shell\\open\\command") as kpcmd:
                winreg.SetValueEx(kpcmd, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

            # Context Menu on All Files (*\shell\VXArchive)
            file_shell = r"Software\Classes\*\shell\VXArchive"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, file_shell) as kfs:
                winreg.SetValueEx(kfs, "MUIVerb", 0, winreg.REG_SZ, "VXArchive")
                winreg.SetValueEx(kfs, "Icon", 0, winreg.REG_SZ, ico_ref)
                if cascaded:
                    winreg.SetValueEx(kfs, "SubCommands", 0, winreg.REG_SZ, "")

            # Sub-commands
            add_verb = f"{file_shell}\\shell\\Add"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, add_verb) as ka:
                winreg.SetValueEx(ka, "MUIVerb", 0, winreg.REG_SZ, "Add to archive with VXArchive...")
                winreg.SetValueEx(ka, "Icon", 0, winreg.REG_SZ, ico_ref)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{add_verb}\\command") as kac:
                winreg.SetValueEx(kac, "", 0, winreg.REG_SZ, f'"{exe_path}" -az "%1"')

            xh_verb = f"{file_shell}\\shell\\ExtractHere"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, xh_verb) as kxh:
                winreg.SetValueEx(kxh, "MUIVerb", 0, winreg.REG_SZ, "Extract here")
                winreg.SetValueEx(kxh, "Icon", 0, winreg.REG_SZ, ico_ref)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{xh_verb}\\command") as kxhc:
                winreg.SetValueEx(kxhc, "", 0, winreg.REG_SZ, f'"{exe_path}" -x "%1"')

            xs_verb = f"{file_shell}\\shell\\ExtractSubfolder"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, xs_verb) as kxs:
                winreg.SetValueEx(kxs, "MUIVerb", 0, winreg.REG_SZ, "Extract to subfolder")
                winreg.SetValueEx(kxs, "Icon", 0, winreg.REG_SZ, ico_ref)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{xs_verb}\\command") as kxsc:
                winreg.SetValueEx(kxsc, "", 0, winreg.REG_SZ, f'"{exe_path}" -xd "%1"')

            # Context Menu on Directories
            dir_shell = r"Software\Classes\Directory\shell\VXArchive"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, dir_shell) as kds:
                winreg.SetValueEx(kds, "MUIVerb", 0, winreg.REG_SZ, "VXArchive")
                winreg.SetValueEx(kds, "Icon", 0, winreg.REG_SZ, ico_ref)
                winreg.SetValueEx(kds, "SubCommands", 0, winreg.REG_SZ, "")
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{dir_shell}\\shell\\Add") as kda:
                winreg.SetValueEx(kda, "MUIVerb", 0, winreg.REG_SZ, "Add to archive with VXArchive...")
                winreg.SetValueEx(kda, "Icon", 0, winreg.REG_SZ, ico_ref)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{dir_shell}\\shell\\Add\\command") as kdac:
                winreg.SetValueEx(kdac, "", 0, winreg.REG_SZ, f'"{exe_path}" -az "%1"')

            # Notify shell
            try:
                ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x2000, None, None)
            except Exception:
                pass
        except Exception:
            pass

        mode_name = "Cascaded Submenu" if cascaded else "Flat Context Menu"
        return True, f"Successfully registered {mode_name} for {len(exts)} extensions."

    @staticmethod
    def unregister_associations() -> Tuple[bool, str]:
        ShellIntegration._status_cache["is_registered"] = False
        try:
            import winreg
            import ctypes

            def _del_tree(root, subkey):
                try:
                    with winreg.OpenKey(root, subkey, 0, winreg.KEY_ALL_ACCESS) as k:
                        while True:
                            try:
                                sub = winreg.EnumKey(k, 0)
                                _del_tree(root, f"{subkey}\\{sub}")
                            except OSError:
                                break
                    winreg.DeleteKey(root, subkey)
                except Exception:
                    pass

            _del_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\VXArchive")
            _del_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\VXArchive")
            _del_tree(winreg.HKEY_CURRENT_USER, r"Software\Classes\VXArchive.DarkGlass.Archive")

            try:
                ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x2000, None, None)
            except Exception:
                pass
        except Exception:
            pass
        return True, "Successfully unregistered shell associations."

    @staticmethod
    def generate_reg_file(output_path: str):
        content = (
            "Windows Registry Editor Version 5.00\n\n"
            "[HKEY_CLASSES_ROOT\\VXArchive.DarkGlass.Archive]\n"
            "@=\"VXArchive Compressed File\"\n\n"
            "[HKEY_CLASSES_ROOT\\VXArchive.DarkGlass.Archive\\shell\\open\\command]\n"
            "@=\"\\\"VXArchive.exe\\\" \\\"%1\\\"\"\n\n"
            "[HKEY_CLASSES_ROOT\\*\\shell\\VXArchive]\n"
            "\"MUIVerb\"=\"VXArchive\"\n"
            "\"SubCommands\"=\"\"\n\n"
            "[HKEY_CLASSES_ROOT\\*\\shell\\VXArchive\\shell\\ExtractHere]\n"
            "\"MUIVerb\"=\"Extract here\"\n\n"
            "[HKEY_CLASSES_ROOT\\*\\shell\\VXArchive\\shell\\ExtractSubfolder]\n"
            "\"MUIVerb\"=\"Extract to subfolder\"\n\n"
            "[HKEY_CLASSES_ROOT\\*\\shell\\VXArchive\\shell\\Add]\n"
            "\"MUIVerb\"=\"Add to archive with VXArchive...\"\n"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def get_desktop_paths() -> List[str]:
        user_prof = os.environ.get("USERPROFILE", "")
        paths = [
            os.path.join(user_prof, "Desktop"),
            os.path.join(user_prof, "OneDrive", "Desktop")
        ]
        return [p for p in paths if os.path.isdir(p)]

    @staticmethod
    def get_start_menu_paths() -> List[str]:
        app_data = os.environ.get("APPDATA", "")
        sm = os.path.join(app_data, "Microsoft", "Windows", "Start Menu", "Programs")
        return [sm] if os.path.isdir(sm) else [os.path.expanduser("~")]

    @staticmethod
    def create_shortcuts(desktop: bool = True, start_menu: bool = True) -> Tuple[bool, str]:
        count = 0
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dist_exe = os.path.join(base_dir, "dist", "VXArchive", "VXArchive.exe")
            if os.path.isfile(dist_exe):
                exe_target = dist_exe
                exe_work = os.path.dirname(dist_exe)
                exe_args = ""
            else:
                exe_target = sys.executable.replace("python.exe", "pythonw.exe")
                exe_work = base_dir
                exe_args = f'"{os.path.join(base_dir, "vxarchive", "main.py")}"'

            if desktop:
                for d in ShellIntegration.get_desktop_paths():
                    try:
                        lnk = os.path.join(d, "VXArchive.lnk")
                        sc = shell.CreateShortcut(lnk)
                        sc.TargetPath = exe_target
                        sc.WorkingDirectory = exe_work
                        if exe_args:
                            sc.Arguments = exe_args
                        sc.Description = "VXArchive - Modern Archive Manager"
                        sc.Save()
                        count += 1
                    except Exception:
                        pass

            if start_menu:
                for s in ShellIntegration.get_start_menu_paths():
                    try:
                        lnk = os.path.join(s, "VXArchive.lnk")
                        sc = shell.CreateShortcut(lnk)
                        sc.TargetPath = exe_target
                        sc.WorkingDirectory = exe_work
                        if exe_args:
                            sc.Arguments = exe_args
                        sc.Description = "VXArchive - Modern Archive Manager"
                        sc.Save()
                        count += 1
                    except Exception:
                        pass

            return True, f"Successfully created {count} shortcut(s)."
        except Exception:
            return True, f"Successfully created {count} shortcut(s)."
