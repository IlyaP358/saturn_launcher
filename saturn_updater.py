#!/usr/bin/env python3
"""
Saturn Launcher Updater
"""

import sys
import os
import time
import shutil
import subprocess
import platform


def wait_for_process_exit(exe_path, max_wait=10):
    """Wait for the old process to exit by checking if file is accessible"""
    print(f"Waiting for old process to exit...")
    for i in range(max_wait):
        try:
            # Try to open file in exclusive mode
            with open(exe_path, 'rb') as f:
                pass
            # If we can open it, process has exited
            print(f"Old process exited successfully")
            return True
        except (IOError, PermissionError):
            # File is still locked, wait
            time.sleep(1)
            print(f"Waiting... ({i+1}/{max_wait})")
    
    print("Warning: Timeout waiting for old process to exit")
    return False


def update_executable(old_exe, new_exe):
    """Replace old executable with new one"""
    try:
        # Create backup
        backup_path = old_exe + ".old"
        print(f"Creating backup: {backup_path}")
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        shutil.copy2(old_exe, backup_path)
        
        # Replace old with new
        print(f"Replacing executable...")
        os.remove(old_exe)
        shutil.move(new_exe, old_exe)
        
        # Set executable permissions on Linux/Mac
        if platform.system() != "Windows":
            os.chmod(old_exe, 0o755)
            print(f"Set executable permissions")
        
        print(f"✓ Update successful!")
        
        # Clean up backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"Cleaned up backup")
        
        return True
        
    except Exception as e:
        print(f"✗ Update failed: {e}")
        
        # Try to rollback
        if os.path.exists(backup_path) and not os.path.exists(old_exe):
            print(f"Rolling back...")
            shutil.move(backup_path, old_exe)
            print(f"Rollback successful")
        
        return False


def launch_new_version(exe_path):
    """Launch the new version of the executable"""
    try:
        print(f"Launching new version...")
        
        if platform.system() == "Windows":
            # Windows: use subprocess.Popen with DETACHED_PROCESS
            subprocess.Popen([exe_path], 
                           creationflags=subprocess.DETACHED_PROCESS,
                           close_fds=True)
        else:
            # Linux/Mac: use nohup
            subprocess.Popen(['nohup', exe_path],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           close_fds=True)
        
        print(f"✓ New version launched!")
        return True
        
    except Exception as e:
        print(f"✗ Failed to launch new version: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: saturn_updater.py <old_exe_path> <new_exe_path>")
        sys.exit(1)
    
    old_exe = sys.argv[1]
    new_exe = sys.argv[2]
    
    print("=" * 50)
    print("Saturn Launcher Updater")
    print("=" * 50)
    print(f"Old executable: {old_exe}")
    print(f"New executable: {new_exe}")
    print(f"Platform: {platform.system()}")
    print("=" * 50)
    
    # Wait for old process to exit
    if not wait_for_process_exit(old_exe):
        print("Proceeding anyway...")
    
    # Small delay to ensure file is released
    time.sleep(1)
    
    # Update executable
    if update_executable(old_exe, new_exe):
        # Launch new version
        launch_new_version(old_exe)
        
        # Self-destruct (delete this updater script)
        try:
            time.sleep(2)  # Give new process time to start
            updater_path = os.path.abspath(__file__)
            if os.path.exists(updater_path):
                os.remove(updater_path)
                print(f"Updater cleaned up")
        except:
            pass  # Ignore errors during cleanup
        
        print("\n✓ Update complete!")
        sys.exit(0)
    else:
        print("\n✗ Update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
