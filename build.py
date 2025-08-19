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
        "--hidden-import", "google.genai",
        "--hidden-import", "PyQt5",
        "--hidden-import", "psutil",
        "plugin.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("OK Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR Failed to build executable: {e}")
        return False

def create_plugin_package():
    """Create the final minimal plugin package"""
    print("\nCreating minimal plugin package...")
    
    # Create dist directory if not exists
    dist_dir = Path("dist/aria")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Essential files to copy
    files_to_copy = [
        ("manifest.json", "manifest.json"),
    ]
    
    # Copy files
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dist_dir / dst)
            print(f"OK Copied {src}")
        else:
            print(f"ERROR: {src} not found!")
            return None
    
    # Copy essential directories
    dirs_to_copy = ["sprites"]
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, dist_dir / dir_name, dirs_exist_ok=True)
            print(f"OK Copied {dir_name} directory")
        else:
            print(f"WARNING: {dir_name} directory not found")
    
    # Copy executable - CRITICAL FILE
    exe_path = Path("dist/aria_companion.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "aria_companion.exe")
        print("OK Copied executable")
    else:
        print("ERROR: aria_companion.exe not found!")
        return None
        
    # Create API key example
    gemini_key_example = dist_dir / "gemini.key.example"
    with open(gemini_key_example, 'w') as f:
        f.write("YOUR_GEMINI_API_KEY_HERE")
    print("OK Created gemini.key.example")
    
    # Create final zip with aria folder structure
    zip_name = "aria_avatar_companion_v1.0.0.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                # Create archive path: aria/filename
                rel_path = file_path.relative_to(dist_dir)
                arcname = Path("aria") / rel_path
                zipf.write(file_path, arcname)
    
    print(f"\nOK Plugin package created: {zip_name}")
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
    
    # Build executable (always build for deploy)
    build_exe = True
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