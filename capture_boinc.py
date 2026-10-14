import os
import subprocess

BOINC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boinc")
BOINCCMD_EXE = os.path.join(BOINC_DIR, "bin", "boinccmd.exe")
AUTH_CFG = os.path.join(BOINC_DIR, "data", "gui_rpc_auth.cfg")

def main():
    if not os.path.exists(BOINCCMD_EXE):
        print(f"boinccmd.exe не найден по пути: {BOINCCMD_EXE}")
        return

    passwd = ""
    if os.path.exists(AUTH_CFG):
        with open(AUTH_CFG, "r", encoding="utf-8") as f:
            passwd = f.read().strip()

    cmd = [BOINCCMD_EXE]
    if passwd:
        cmd.extend(["--passwd", passwd])
    cmd.append("--get_host_info")

    print(f"Запрос телеметрии через {BOINCCMD_EXE}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(res.stdout)
    except Exception as e:
        print(f"Ошибка вызова boinccmd: {e}")

if __name__ == "__main__":
    main()
