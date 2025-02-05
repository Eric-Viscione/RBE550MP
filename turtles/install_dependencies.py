import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print(f"Installed {package}")
    
    
    
def main():
    required_packages = ['opencv-python']
    print("Updating Pip")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    print("Pip Sucesfully Updated")
    for package in required_packages: 
        print(f"installing {package}")
        install(package)
        
if __name__ == "__main__":
    main()