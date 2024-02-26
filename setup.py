# setup.py
import subprocess
import sys

def install_packages():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All required packages have been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install required packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_packages()
    # Now run your main application script
    subprocess.check_call([sys.executable, "main.py"])
