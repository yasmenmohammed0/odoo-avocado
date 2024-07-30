import subprocess
import sys
import platform
import urllib.request
import os
import shutil

def is_wkhtmltopdf_installed():
    try:
        # Check if wkhtmltopdf is already installed and accessible in PATH
        result = subprocess.run(['wkhtmltopdf', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("wkhtmltopdf is already installed.")
            return True
        else:
            print("wkhtmltopdf is not installed.")
            return False
    except (FileNotFoundError, OSError):
        print("wkhtmltopdf is not installed or not found in PATH.")
        return False

def check_wkhtmltopdf_in_path():
    if platform.system().lower() == 'windows':
        default_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if os.path.exists(default_path):
            print(f"wkhtmltopdf found at {default_path}")
            os.environ['PATH'] += os.pathsep + os.path.dirname(default_path)
            return True
    return False

def install_wkhtmltopdf():
    if check_wkhtmltopdf_in_path() or is_wkhtmltopdf_installed():
        return

    print("Installing wkhtmltopdf...")
    try:
        os_name = platform.system().lower()
        if os_name == 'linux':
            distro = platform.linux_distribution()[0].lower()
            if 'ubuntu' in distro or 'debian' in distro:
                subprocess.check_call(['sudo', 'apt-get', 'update'])
                subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'wkhtmltopdf'])
            elif 'centos' in distro or 'redhat' in distro or 'fedora' in distro:
                subprocess.check_call(['sudo', 'yum', 'install', '-y', 'wkhtmltopdf'])
            else:
                print(f"Unsupported Linux distribution: {distro}")
        elif os_name == 'darwin':
            subprocess.check_call(['/bin/bash', '-c', 'brew install wkhtmltopdf'])
        elif os_name == 'windows':
            # Download and install wkhtmltopdf for Windows
            url = 'https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe'
            installer_path = os.path.join(os.getcwd(), 'wkhtmltox-installer.exe')
            urllib.request.urlretrieve(url, installer_path)
            print(f"Downloaded wkhtmltopdf installer to {installer_path}")

            # Run the installer with proper arguments
            install_command = f'"{installer_path}" /silent /verysilent /norestart'
            subprocess.check_call(install_command, shell=True)
            print("wkhtmltopdf installed successfully.")

            # Clean up the installer
            os.remove(installer_path)

            # Ensure the path to wkhtmltopdf is in the PATH environment variable
            install_path = r'C:\Program Files\wkhtmltopdf\bin'
            if install_path not in os.environ['PATH']:
                os.environ['PATH'] += os.pathsep + install_path
                print(f"Added {install_path} to PATH")
        else:
            print(f"Unsupported operating system: {os_name}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_wkhtmltopdf()
