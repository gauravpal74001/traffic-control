#!/usr/bin/env python3
"""
Script to add best_ps3.pt model file to weights directory.
This script can:
1. Create a copy of best.pt as best_ps3.pt (if they're the same model)
2. Create a symbolic link (if on Unix systems)
3. Provide instructions for adding your own model file
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    weights_dir = project_root / "weights"
    best_pt = weights_dir / "best.pt"
    best_ps3_pt = weights_dir / "best_ps3.pt"
    
    print("=" * 60)
    print("Adding best_ps3.pt Model File")
    print("=" * 60)
    print()
    
    # Check if best_ps3.pt already exists
    if best_ps3_pt.exists():
        print(f"✅ {best_ps3_pt} already exists!")
        print(f"   Size: {best_ps3_pt.stat().st_size / (1024*1024):.2f} MB")
        return 0
    
    # Check if best.pt exists
    if not best_pt.exists():
        print(f"❌ {best_pt} not found!")
        print()
        print("💡 Options to add best_ps3.pt:")
        print("   1. Place your trained model file at: weights/best_ps3.pt")
        print("   2. Download the model from your training repository")
        print("   3. Copy from another location")
        return 1
    
    print(f"📁 Found {best_pt}")
    print(f"   Size: {best_pt.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    # Ask user what to do
    print("Options:")
    print("1. Copy best.pt to best_ps3.pt (if they're the same model)")
    print("2. Create symbolic link (Unix/Mac only)")
    print("3. Skip (you'll add the file manually)")
    print()
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        # Copy the file
        try:
            print(f"📋 Copying {best_pt} to {best_ps3_pt}...")
            shutil.copy2(best_pt, best_ps3_pt)
            print(f"✅ Successfully created {best_ps3_pt}!")
            print(f"   Size: {best_ps3_pt.stat().st_size / (1024*1024):.2f} MB")
            return 0
        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return 1
    
    elif choice == "2":
        # Create symbolic link (Unix/Mac)
        if sys.platform == "win32":
            print("❌ Symbolic links on Windows require administrator privileges.")
            print("   Please use option 1 (copy) instead.")
            return 1
        
        try:
            print(f"🔗 Creating symbolic link from {best_pt} to {best_ps3_pt}...")
            if best_ps3_pt.exists():
                best_ps3_pt.unlink()
            best_ps3_pt.symlink_to(best_pt)
            print(f"✅ Successfully created symbolic link!")
            return 0
        except Exception as e:
            print(f"❌ Error creating symbolic link: {e}")
            return 1
    
    elif choice == "3":
        print("⏭️  Skipped. Please add best_ps3.pt manually to the weights/ directory.")
        print()
        print("💡 To add manually:")
        print(f"   1. Place your model file at: {best_ps3_pt}")
        print("   2. Or run this script again and choose option 1 or 2")
        return 0
    
    else:
        print("❌ Invalid choice!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

