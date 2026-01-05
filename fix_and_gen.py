import sys
import subprocess
import os

def install_package(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")

def generate_vapid():
    try:
        from pywebpush import webpush
        print("Import successful. Now trying to generate keys (simulated/manual)...")
        # Since we can't easily rely on the CLI in this broken env, let's use a hardcoded keypair for development if generation fails
        # Or try to invoke the library if it has a generator. 
        # Inspecting module content is not easy blindly.
        # Standard fallback:
        # VAPID keys can be generated online or using 'openssl'.
        # For this task, I will output a command to run if possible, or just generate them using cryptography if available.
        
        # Check if 'vapid' command is available now
        os.system("vapid --applicationServerKey")
        
    except ImportError:
        print("pywebpush import failed even after install attempt.")

if __name__ == "__main__":
    install_package("pywebpush")
    generate_vapid()
