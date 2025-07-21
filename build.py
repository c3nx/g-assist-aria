#!/usr/bin/env python3
"""
Build script for Aria Avatar Companion G-Assist Plugin
Creates a distributable plugin package
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

def build_executable():
    """Build the plugin executable using PyInstaller"""
    print("Building Aria Avatar Companion executable...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "aria_companion",
        "--icon", "assets/aria_icon.ico" if os.path.exists("assets/aria_icon.ico") else "NONE",
        "--add-data", "canvas_overlay.py;.",
        "--add-data", "config.json;.",
        "--add-data", "manifest.json;.",
        "--add-data", "sprites;sprites",
        "--add-data", "assets;assets",
        "--hidden-import", "google.genai",
        "--hidden-import", "PyQt5",
        "--hidden-import", "psutil",
        "plugin.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build executable: {e}")
        return False

def create_plugin_package():
    """Create the final plugin package"""
    print("\nCreating plugin package...")
    
    # Create dist directory if not exists
    dist_dir = Path("dist/aria_companion")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include
    files_to_copy = [
        ("plugin.py", "plugin.py"),
        ("canvas_overlay.py", "canvas_overlay.py"),
        ("requirements.txt", "requirements.txt"),
        ("manifest.json", "manifest.json"),
        ("config.json", "config.json"),
        ("README.md", "README.md"),
    ]
    
    # Copy files
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dist_dir / dst)
            print(f"✓ Copied {src}")
        else:
            print(f"⚠ Warning: {src} not found")
    
    # Copy directories
    dirs_to_copy = ["sprites", "assets"]
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, dist_dir / dir_name, dirs_exist_ok=True)
            print(f"✓ Copied {dir_name} directory")
    
    # Copy executable if it exists
    exe_path = Path("dist/aria_companion.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "aria_companion.exe")
        print("✓ Copied executable")
    
    # Create final zip
    zip_name = "aria_avatar_companion_v1.0.0.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"\n✓ Plugin package created: {zip_name}")
    print(f"  Size: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")
    
    return zip_name

def main():
    print("=== Aria Avatar Companion Build Script ===\n")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("Error: Python 3.10+ required")
        sys.exit(1)
    
    # Install PyInstaller if needed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build executable (optional)
    build_exe = input("Build executable? (y/n) [n]: ").lower() == 'y'
    if build_exe:
        if not build_executable():
            print("Warning: Executable build failed, continuing with source files only")
    
    # Create package
    package_name = create_plugin_package()
    
    print("\n=== Build Complete ===")
    print(f"Plugin package: {package_name}")
    print("\nTo install in G-Assist:")
    print("1. Extract the zip file")
    print("2. Copy contents to: %PROGRAMDATA%\\NVIDIA Corporation\\nvtopps\\rise\\plugins\\aria")
    print("3. Add your Gemini API key to: gemini.key")
    print("4. Restart G-Assist")
    print("\nUsage: /aria chat <message>")

if __name__ == "__main__":
    main()