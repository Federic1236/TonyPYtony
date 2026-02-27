import os
import sys
import winreg
import json

def setup_all():
    # 1. Get absolute paths
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    icon_path = os.path.join(base_path, "resources", "tony.ico")
    python_exe = sys.executable
    run_cmd = f'"{python_exe}" -m tonypytony.interpreter "%1"'

    try:
        # 2. Registry Magic
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".ptny") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "TonyPytonyFile")
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "TonyPytonyFile\\DefaultIcon") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, icon_path)
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "TonyPytonyFile\\shell\\open\\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, run_cmd)

        # 3. VS Code Settings "Injection"
        vscode_settings_path = os.path.expandvars(r"%APPDATA%\Code\User\settings.json")
        if os.path.exists(vscode_settings_path):
            with open(vscode_settings_path, "r+") as f:
                data = json.load(f)
                # Add the association and silence Pylance
                data.setdefault("files.associations", {})["*.ptny"] = "python"
                data.setdefault("python.analysis.diagnosticSeverityOverrides", {})["reportUndefinedVariable"] = "none"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        print("Successfully installed TonyPytony environment!")
    except Exception as e:
        print(f"Failed to set system settings: {e}")

if __name__ == "__main__":
    setup_all()
