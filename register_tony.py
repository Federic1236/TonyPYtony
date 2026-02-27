import os
import sys
import winreg

def install():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(BASE_DIR, "tony.ico")
    python_exe = sys.executable
    run_command = f'"{python_exe}" -m tonypytony.interpreter "%1"'

    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".ptny") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "TonyPytonyFile")
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TonyPytonyFile\DefaultIcon") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, icon_path)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TonyPytonyFile\shell\open\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, run_command)

        print(f"Installation Complete. Path: {BASE_DIR}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    install()