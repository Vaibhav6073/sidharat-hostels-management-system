import os
import zipfile
import shutil

def create_installer_package():
    """Create a downloadable installer package"""
    
    # Files to include in the package
    files_to_include = [
        'app.py',
        'requirements.txt',
        'README.md',
        'INSTALL.md',
        'INSTALL.bat',
        'START.bat',
        'mobile_run.bat',
        'templates/',
    ]
    
    # Create package directory
    package_dir = 'sidharat-hostels-installer'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy files to package directory
    for item in files_to_include:
        if os.path.isfile(item):
            shutil.copy2(item, package_dir)
        elif os.path.isdir(item):
            shutil.copytree(item, os.path.join(package_dir, item))
    
    # Create uploads directory
    os.makedirs(os.path.join(package_dir, 'uploads'), exist_ok=True)
    
    # Create ZIP file
    zip_filename = 'sidharat-hostels-installer.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    print(f"Package created: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    print("\nPackage Contents:")
    print("- Complete hostel management system")
    print("- One-click installer (INSTALL.bat)")
    print("- Easy start script (START.bat)")
    print("- Mobile access helper (mobile_run.bat)")
    print("- All templates and static files")
    print("- Documentation and setup guide")
    
    return zip_filename

if __name__ == "__main__":
    create_installer_package()