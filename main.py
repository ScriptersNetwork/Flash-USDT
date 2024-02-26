import subprocess

# The path to the Flash.exe file
flash_exe_path = 'Flash.exe'

# Run Flash.exe
try:
    subprocess.run(flash_exe_path, check=True)
    print("Flash.exe ran successfully.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred while trying to run Flash.exe: {e}")
