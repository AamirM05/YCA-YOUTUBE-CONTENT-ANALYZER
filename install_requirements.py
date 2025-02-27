import subprocess
import sys
import pkg_resources

def get_installed_packages():
    """Get a dictionary of installed packages and their versions"""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def install_package(package):
    """Install a package if it's not already installed"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")

def main():
    # Read requirements.txt
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    # Get currently installed packages
    installed_packages = get_installed_packages()
    
    # Install missing packages
    for req in requirements:
        if not req or req.startswith('#'):
            continue
            
        # Split package name and version
        if '==' in req:
            package_name, version = req.split('==')
        else:
            package_name = req
            version = None
        
        package_name = package_name.lower()
        
        if package_name in installed_packages:
            if version and installed_packages[package_name] != version:
                print(f"Updating {package_name} to version {version}")
                install_package(req)
            else:
                print(f"Package {package_name} is already installed")
        else:
            print(f"Installing {req}")
            install_package(req)

if __name__ == "__main__":
    main()
