
import os
import sys
import requests
import platform
import subprocess
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QMessageBox, QTextEdit)

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def get_current_version():
    """Get current version from version.txt"""
    try:
        version_file = get_resource_path('version.txt')
        with open(version_file, 'r') as f:
            return f.read().strip()
    except:
        return "unknown"

class UpdateCheckThread(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            # Public repository URL
            github_repo = 'IlyaP358/saturn-versions-rep'
            headers = {'Accept': 'application/vnd.github.v3+json'}
            url = f'https://api.github.com/repos/{github_repo}/releases/latest'
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                self.error.emit("No releases found")
                return
            
            response.raise_for_status()
            release_data = response.json()
            
            current_version = get_current_version()
            latest_version = release_data['tag_name'].lstrip('v')
            
            # Simple version comparison
            current_parts = [int(x) for x in current_version.split('.')]
            latest_parts = [int(x) for x in latest_version.split('.')]
            
            while len(current_parts) < 3: current_parts.append(0)
            while len(latest_parts) < 3: latest_parts.append(0)
            
            update_available = latest_parts > current_parts
            
            result = {
                'available': update_available,
                'current_version': current_version,
                'latest_version': latest_version,
                'release_data': release_data
            }
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

class UpdateDownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, download_url, filename):
        super().__init__()
        self.download_url = download_url
        self.filename = filename

    def run(self):
        try:
            headers = {'Accept': 'application/octet-stream'}
            response = requests.get(self.download_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Create temp directory
            temp_dir = os.path.join(os.getcwd(), '.saturn_temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            filepath = os.path.join(temp_dir, self.filename)
            
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)
                            
            self.finished.emit(filepath)
            
        except Exception as e:
            self.error.emit(str(e))

class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saturn Updater")
        self.setFixedWidth(400)
        
        self.layout = QVBoxLayout(self)
        
        # Status Label
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # Changelog area (initially hidden)
        self.changelog_area = QTextEdit()
        self.changelog_area.setReadOnly(True)
        self.changelog_area.hide()
        self.layout.addWidget(self.changelog_area)
        
        # Progress Bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        self.update_button = QPushButton("Update Now")
        self.update_button.hide()
        self.update_button.clicked.connect(self.start_download)
        
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addWidget(self.update_button)
        self.layout.addLayout(self.button_layout)
        
        # Data
        self.release_data = None
        self.download_url = None
        self.filename = None
        
        # Start check
        self.check_thread = UpdateCheckThread()
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.error.connect(self.on_error)
        self.check_thread.start()

    def on_check_finished(self, result):
        if result['available']:
            self.release_data = result['release_data']
            self.status_label.setText(f"<h3>New Update Available!</h3>"
                                    f"Current: {result['current_version']} → "
                                    f"New: {result['latest_version']}")
            
            # Show changelog
            self.changelog_area.setHtml(f"<b>Changelog:</b><br>{self.release_data.get('body', 'No details').replace(chr(10), '<br>')}")
            self.changelog_area.show()
            self.resize(400, 500)
            
            # Setup update button
            self.determine_asset()
            
        else:
            self.status_label.setText(f"<h3>You are up to date!</h3>"
                                    f"Version: {result['current_version']}")
            self.close_button.setText("Close")

    def determine_asset(self):
        system = platform.system()
        if system == "Windows":
            asset_name = "saturn_gui_windows.exe"
        elif system == "Linux":
            asset_name = "saturn_gui_linux"
        else:
            self.status_label.setText("Unsupported platform for auto-update")
            return

        # Find asset
        assets = self.release_data.get('assets', [])
        for asset in assets:
            if asset['name'] == asset_name:
                self.download_url = asset['url']
                self.filename = asset_name
                self.update_button.show()
                return
        
        self.status_label.setText(f"Error: Asset '{asset_name}' not found in release")

    def start_download(self):
        self.update_button.hide()
        self.close_button.hide()
        self.changelog_area.hide()
        self.status_label.setText("Downloading update...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.resize(400, 200)
        
        self.download_thread = UpdateDownloadThread(self.download_url, self.filename)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_error)
        self.download_thread.start()

    def on_download_finished(self, filepath):
        self.status_label.setText("Installing update...")
        self.launch_updater(filepath)

    def launch_updater(self, new_exe_path):
        try:
            current_exe = sys.executable
            if not getattr(sys, 'frozen', False):
                QMessageBox.warning(self, "Warning", "Running from source. Cannot auto-update.")
                self.close()
                return

            system = platform.system()
            
            if system == "Windows":
                updater_script = os.path.join(os.getcwd(), 'saturn_updater.bat')
                with open(updater_script, 'w') as f:
                    f.write(f'''@echo off
timeout /t 2 /nobreak >nul
del "{current_exe}"
move "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
''')
                subprocess.Popen([updater_script], shell=True)
                
            elif system == "Linux":
                updater_script = os.path.join(os.getcwd(), 'saturn_updater.sh')
                with open(updater_script, 'w') as f:
                    f.write(f'''#!/bin/bash
sleep 2
mv "{new_exe_path}" "{current_exe}"
chmod +x "{current_exe}"
# Clear PyInstaller environment variables
export LD_LIBRARY_PATH=""
# Launch new version detached
(setsid "{current_exe}" &) >/dev/null 2>&1
rm "$0"
''')
                os.chmod(updater_script, 0o755)
                subprocess.Popen(['/bin/bash', updater_script], start_new_session=True)
            
            sys.exit(0)
            
        except Exception as e:
            self.on_error(f"Failed to launch updater: {e}")

    def on_error(self, message):
        self.progress_bar.hide()
        self.status_label.setText(f"<font color='red'>Error: {message}</font>")
        self.close_button.show()
