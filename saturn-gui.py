import subprocess
import uuid
import json
import os
import sys
import psutil
import shutil
import requests
import preset_manager
from io import BytesIO

# Heavy libraries - will be imported lazily when needed:
# - minecraft_launcher_lib (imported in get_versions, LaunchThread)

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        # Launcher compiled in PyInstaller
        base_path = sys._MEIPASS
    else:
        # Launcher starts with source code 
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QThread, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QSlider, QStatusBar, QStyle,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFrame, QFileDialog,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFrame, QFileDialog,
    QListWidget, QListWidgetItem, QScrollArea, QInputDialog, QProgressDialog)

class Ui_MainWindow(object):
    def __init__(self):
        self.launch_thread = None

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        
        # Initialize presets directory
        preset_manager.init_presets_directory()

        MainWindow.resize(720, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Create main vertical layout
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(50, 20, 50, 20)  # Increased left/right margins to center the frame
        self.mainLayout.setSpacing(10)

        # Logo label
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(800, 400))
        self.label.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.label)

        # Spacer
        self.mainLayout.addStretch()

        # Create frame for input controls
        self.inputFrame = QFrame(self.centralwidget)
        self.inputFrame.setObjectName(u"inputFrame")
        self.inputFrame.setFrameShape(QFrame.Box)
        self.inputFrame.setFrameShadow(QFrame.Sunken)
        self.inputFrame.setLineWidth(2)

        # Input widgets layout inside frame
        self.inputLayout = QVBoxLayout(self.inputFrame)
        self.inputLayout.setObjectName(u"inputLayout")
        self.inputLayout.setContentsMargins(15, 15, 15, 15)
        self.inputLayout.setSpacing(10)

        self.lineEdit = QLineEdit(self.inputFrame)
        self.lineEdit.setObjectName(u"lineEdit")
        self.inputLayout.addWidget(self.lineEdit)

        self.comboBox = QComboBox(self.inputFrame)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMaxVisibleItems(8)  # Limit dropdown to show maximum 8 items at once
        self.inputLayout.addWidget(self.comboBox)

        # Preset Layout
        self.presetLayout = QHBoxLayout()
        self.presetLayout.setObjectName(u"presetLayout")
        self.presetLayout.setSpacing(10)

        # Preset ComboBox
        self.presetComboBox = QComboBox(self.inputFrame)
        self.presetComboBox.setObjectName(u"presetComboBox")
        self.presetComboBox.setMinimumWidth(200)
        self.presetLayout.addWidget(self.presetComboBox, 2)  # Stretch factor 2

        # Create New Preset Button
        self.createPresetButton = QPushButton(self.inputFrame)
        self.createPresetButton.setObjectName(u"createPresetButton")
        self.createPresetButton.setFixedSize(30, 30)
        self.createPresetButton.setToolTip("Create New Preset")
        plus_icon = MainWindow.style().standardIcon(QStyle.SP_FileDialogNewFolder)
        self.createPresetButton.setIcon(plus_icon)
        self.presetLayout.addWidget(self.createPresetButton)
        
        # Archive/Unarchive Button
        self.archiveButton = QPushButton(self.inputFrame)
        self.archiveButton.setObjectName(u"archiveButton")
        self.archiveButton.setText("Archive")
        # self.archiveButton.setFixedWidth(100) # Let it size automatically or fixed
        self.presetLayout.addWidget(self.archiveButton)
        
        # self.presetLayout.addStretch() # Maybe not needed if we want them compact

        self.inputLayout.addLayout(self.presetLayout)

        self.pushButton = QPushButton(self.inputFrame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setStyleSheet("QPushButton { font-weight: bold; min-height: 35px; }")
        self.inputLayout.addWidget(self.pushButton)

        self.progressBar = QProgressBar(self.inputFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)  # Initially hidden
        self.inputLayout.addWidget(self.progressBar)

        # Buttons layout
        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.buttonsLayout.setSpacing(10)  # Reduced spacing between buttons

        self.modsButton = QPushButton(self.inputFrame)
        self.modsButton.setObjectName(u"modsButton")
        self.modsButton.setText("Open Mods Folder")
        self.modsButton.setFixedWidth(130)  # Fixed button width
        # Add folder icon
        folder_icon = MainWindow.style().standardIcon(QStyle.SP_DirIcon)
        self.modsButton.setIcon(folder_icon)
        self.buttonsLayout.addStretch()  # Add stretch before buttons to center them
        self.buttonsLayout.addWidget(self.modsButton)

        self.downloadModsButton = QPushButton(self.inputFrame)
        self.downloadModsButton.setObjectName(u"downloadModsButton")
        self.downloadModsButton.setText("Download Mods")
        self.downloadModsButton.setFixedWidth(130)  # Fixed button width
        # Add download/network icon
        download_icon = MainWindow.style().standardIcon(QStyle.SP_ComputerIcon)
        self.downloadModsButton.setIcon(download_icon)
        self.buttonsLayout.addWidget(self.downloadModsButton)

        self.downloadShadersButton = QPushButton(self.inputFrame)
        self.downloadShadersButton.setObjectName(u"downloadShadersButton")
        self.downloadShadersButton.setText("Download Shaders")
        self.downloadShadersButton.setFixedWidth(140)  # Slightly wider for text
        # Add shader/graphics icon
        shader_icon = MainWindow.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self.downloadShadersButton.setIcon(shader_icon)
        self.buttonsLayout.addWidget(self.downloadShadersButton)

        self.deleteButton = QPushButton(self.inputFrame)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setText("Delete Version")
        self.deleteButton.setFixedWidth(130)  # Fixed button width
        self.deleteButton.setStyleSheet("QPushButton { color: black; }")
        # Add trash/delete icon
        trash_icon = MainWindow.style().standardIcon(QStyle.SP_TrashIcon)
        self.deleteButton.setIcon(trash_icon)
        self.buttonsLayout.addWidget(self.deleteButton)
        self.buttonsLayout.addStretch()  # Add stretch after buttons to center them

        self.inputLayout.addLayout(self.buttonsLayout)

        self.mainLayout.addWidget(self.inputFrame)

        # Load background from config
        config = load_config()
        bg_file = config.get("background_path", "saturn-background.png")

        # Determine the correct background path
        if os.path.exists(bg_file) and os.path.isabs(bg_file):
            # User-selected custom background (absolute path that exists)
            background_path = bg_file
        else:
            # Use default bundled background
            background_path = get_resource_path("saturn-background.png")

        # Convert Windows backslashes to forward slashes for CSS compatibility
        background_path = background_path.replace('\\', '/')

        # Set background image and frame styling
        self.centralwidget.setStyleSheet(f"""
            #centralwidget {{
                background-image: url({background_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
            #inputFrame {{
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 5px;
            }}
            QComboBox QAbstractItemView {{
                min-width: 150px;
                max-width: 180px;
                padding: 2px;
                margin: 0px;
            }}
        """)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 720, 22))
        MainWindow.setMenuBar(self.menubar)

        # Settings button in top right
        self.settingsButton = QPushButton("Settings")
        self.settingsButton.setFixedSize(70, 35)  # Make it larger to accommodate text
        # Add computer/settings icon
        settings_icon = MainWindow.style().standardIcon(QStyle.SP_ComputerIcon)
        self.settingsButton.setIcon(settings_icon)
        self.settingsButton.setIconSize(QSize(16, 16))  # Slightly smaller icon to fit text
        self.menubar.setCornerWidget(self.settingsButton, Qt.TopRightCorner)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Set window icon
        icon_path = get_resource_path("logo.png")
        MainWindow.setWindowIcon(QIcon(icon_path))

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Saturn Launcher", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Username...", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Start Game", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Saturn Launcher", None))
    # retranslateUi



class PresetThread(QThread):
    finished = Signal(bool, str)
    
    def __init__(self, operation, preset_name):
        super().__init__()
        self.operation = operation # 'archive' or 'unzip'
        self.preset_name = preset_name
        
    def run(self):
        try:
            success = False
            msg = "Unknown error"
            
            if self.operation == 'archive':
                success = preset_manager.compress_preset(self.preset_name)
                msg = f"Preset '{self.preset_name}' archived successfully." if success else f"Failed to archive '{self.preset_name}'."
            elif self.operation == 'unzip':
                success = preset_manager.decompress_preset(self.preset_name)
                msg = f"Preset '{self.preset_name}' decompressed successfully." if success else f"Failed to decompress '{self.preset_name}'."
            
            self.finished.emit(success, msg)
        except Exception as e:
            self.finished.emit(False, str(e))


class LaunchThread(QThread):
    progress = Signal(int)
    show_progress = Signal()
    hide_progress = Signal()
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, version, username):
        super().__init__()
        self.version = version
        self.username = username
        self.final_version = version  # Store final version separately

    def progress_callback(self, *args):
        print(f"Progress callback called with args: {args}")
        try:
            if len(args) >= 2:
                current, total = args[0], args[1]
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.progress.emit(percentage)
        except Exception as e:
            print(f"Error in progress callback: {e}")

    def run(self):
        import minecraft_launcher_lib  # Lazy import
        try:
            print(f"Starting launch process for version: {self.version}, username: {self.username}")

            print(f"Starting launch process for version: {self.version}, username: {self.username}")
            
            # Use active preset directory
            active_preset = preset_manager.get_active_preset()
            minecraft_directory = preset_manager.get_preset_path(active_preset)
            print(f"Using preset: {active_preset}")
            print(f"Using minecraft directory: {minecraft_directory}")

            if not os.path.exists(os.path.join(minecraft_directory, "versions")):
                os.makedirs(os.path.join(minecraft_directory, "versions"))
                print("Created versions directory")

            # Auto-install Forge
            if self.version.startswith("forge-"):
                mc_version = self.version.replace("forge-", "")
                print(f"Installing Forge for Minecraft {mc_version}")
                try:
                    forge_version = minecraft_launcher_lib.forge.find_forge_version(mc_version)
                    if forge_version is None:
                        error_msg = f"Forge version not found for Minecraft {mc_version}"
                        print(f"Error: {error_msg}")
                        self.error_occurred.emit(error_msg)
                        return

                    installed_version = minecraft_launcher_lib.forge.forge_to_installed_version(forge_version)
                    print(f"Forge installed version: {installed_version}")

                    # Check if already installed
                    version_path = os.path.join(minecraft_directory, "versions", installed_version, f"{installed_version}.json")
                    if not os.path.exists(version_path):
                        print("Forge not installed, installing...")
                        self.show_progress.emit()
                        minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_directory)
                        print("Forge installation completed")
                    else:
                        print("Forge already installed")

                    # Use the installed version name for launching (like CLI does)
                    self.final_version = installed_version
                    print(f"Final version for launch: {self.final_version}")

                except Exception as e:
                    error_msg = f"Forge setup error: {str(e)}"
                    print(f"Error: {error_msg}")
                    self.error_occurred.emit(error_msg)
                    return

            # Auto-install Fabric
            elif self.version.startswith("fabric-"):
                mc_version = self.version.replace("fabric-", "")
                print(f"Installing Fabric for Minecraft {mc_version}")
                loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
                self.final_version = f"fabric-loader-{loader_version}-{mc_version}"
                print(f"Final Fabric version: {self.final_version}")

                version_path = os.path.join(minecraft_directory, "versions", self.final_version, f"{self.final_version}.json")
                if not os.path.exists(version_path):
                    print("Fabric not installed, installing...")
                    self.show_progress.emit()
                    try:
                        minecraft_launcher_lib.fabric.install_fabric(mc_version, minecraft_directory, loader_version, callback=self.progress_callback)
                    except Exception as e:
                        print(f"Fabric install with callback failed: {e}, trying without callback")
                        minecraft_launcher_lib.fabric.install_fabric(mc_version, minecraft_directory, loader_version)
                    print("Fabric installation completed")
                else:
                    print("Fabric already installed")

            # Vanilla install
            else:
                self.final_version = self.version
                print(f"Checking vanilla version: {self.final_version}")
                version_path = os.path.join(minecraft_directory, "versions", self.final_version, f"{self.final_version}.json")
                if not os.path.exists(version_path):
                    print("Vanilla version not installed, installing...")
                    self.show_progress.emit()
                    try:
                        minecraft_launcher_lib.install.install_minecraft_version(version=self.final_version, minecraft_directory=minecraft_directory, callback=self.progress_callback)
                    except Exception as e:
                        print(f"Vanilla install with callback failed: {e}, trying without callback")
                        minecraft_launcher_lib.install.install_minecraft_version(version=self.final_version, minecraft_directory=minecraft_directory)
                    print("Vanilla installation completed")
                else:
                    print("Vanilla version already installed")

            # Load RAM settings
            try:
                print("Loading config...")
                config = load_config()
                print(f"Config loaded: {config}")
                ram_config = config.get('ram', {})
                print(f"RAM config: {ram_config}")
                min_ram = ram_config.get('min', '1024M')
                max_ram = ram_config.get('max', '2048M')
                print(f"RAM settings: min={min_ram}, max={max_ram}")
            except Exception as e:
                print(f"Error loading config: {e}")
                import traceback
                traceback.print_exc()
                min_ram = '1024M'
                max_ram = '2048M'

            offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.username))
            print(f"Generated UUID: {offline_uuid}")

            options = {
                "username": self.username,
                "uuid": offline_uuid,
                "token": "",
                "jvmArguments": [f"-Xms{min_ram}", f"-Xmx{max_ram}"]
            }

            print(f"Launching with options: {options}")

            # Set progress to 100% when launching
            self.progress.emit(100)
            self.show_progress.emit()

            command = minecraft_launcher_lib.command.get_minecraft_command(
                version=self.final_version,
                options=options,
                minecraft_directory=minecraft_directory
            )

            print(f"Generated command: {command}")

            # Execute command and check return code
            return_code = subprocess.call(command)
            print(f"Command completed with return code: {return_code}")

            if return_code != 0:
                error_msg = f"Command failed with return code {return_code}"
                print(f"Error: {error_msg}")
                self.error_occurred.emit(error_msg)
            else:
                print("Command executed successfully")
                # Save the launched version and username
                try:
                    config = load_config()
                    config["last_version"] = self.version  # Save the original selected version
                    config["last_username"] = self.username  # Save the username
                    save_config(config)
                    print(f"Saved {self.version} as last launched version and {self.username} as last username")
                except Exception as e:
                    print(f"Failed to save last settings: {e}")

            # Hide progress bar when finished
            self.hide_progress.emit()
            self.finished.emit()

        except Exception as e:
            error_msg = f"Launch error: {str(e)}"
            print(f"Exception: {error_msg}")
            self.error_occurred.emit(error_msg)
            # Hide progress bar on error
            self.hide_progress.emit()
            self.finished.emit()


def load_config():
    # For compiled version, save config in user's home directory
    if getattr(sys, 'frozen', False):
        config_dir = os.path.expanduser("~/.saturn_launcher")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_path = os.path.join(config_dir, 'config.json')
    else:
        # For development, use config.json in current directory
        config_path = 'config.json'

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {
            "ram": {"min": "1024M", "max": "2048M"},
            "show_forge": False,
            "show_fabric": False,
            "show_snapshots": False,
            "last_version": "",
            "last_username": "",
            "background_path": "saturn-background.png"
        }

def save_config(config):
    # For compiled version, save config in user's home directory
    if getattr(sys, 'frozen', False):
        config_dir = os.path.expanduser("~/.saturn_launcher")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_path = os.path.join(config_dir, 'config.json')
    else:
        # For development, use config.json in current directory
        config_path = 'config.json'

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def is_version_installed(version):
    """Check if a version is installed"""
    import minecraft_launcher_lib  # Lazy import
    try:
        active_preset = preset_manager.get_active_preset()
        minecraft_directory = preset_manager.get_preset_path(active_preset)

        if version.startswith("forge-"):
            # For Forge versions, we need to find the actual installed version name
            mc_version = version.replace("forge-", "")
            print(f"Checking Forge installation for MC {mc_version}")
            forge_version = minecraft_launcher_lib.forge.find_forge_version(mc_version)
            print(f"Found Forge version: {forge_version}")
            if forge_version:
                installed_version = minecraft_launcher_lib.forge.forge_to_installed_version(forge_version)
                print(f"Installed version name: {installed_version}")
                version_path = os.path.join(minecraft_directory, "versions", installed_version, f"{installed_version}.json")
                exists = os.path.exists(version_path)
                print(f"Version path exists: {exists} (path: {version_path})")
                return exists
        elif version.startswith("fabric-"):
            # For Fabric versions, we need to construct the installed version name
            mc_version = version.replace("fabric-", "")
            loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
            installed_version = f"fabric-loader-{loader_version}-{mc_version}"
            version_path = os.path.join(minecraft_directory, "versions", installed_version, f"{installed_version}.json")
            return os.path.exists(version_path)
        else:
            # For vanilla versions
            version_path = os.path.join(minecraft_directory, "versions", version, f"{version}.json")
            return os.path.exists(version_path)

        return False
    except:
        return False


def get_versions(show_forge=False, show_fabric=False, show_snapshots=False):
    import minecraft_launcher_lib  # Lazy import
    try:
        versions_data = minecraft_launcher_lib.utils.get_version_list()
        versions = []

        # Add release versions with status indicators
        for version in versions_data:
            if version["type"] == "release":
                status = "✓" if is_version_installed(version["id"]) else "↓"
                versions.append(f"{status} {version['id']}")

        if show_snapshots:
            snapshots = [v["id"] for v in versions_data if v["type"] == "snapshot"]
            for snapshot in reversed(snapshots):
                status = "✓" if is_version_installed(snapshot) else "↓"
                versions.append(f"{status} {snapshot}")

        if show_forge:
            try:
                # Group Forge versions by Minecraft version and get the latest for each
                forge_versions_raw = minecraft_launcher_lib.forge.list_forge_versions()
                print(f"Raw Forge versions: {len(forge_versions_raw)} items")
                forge_by_mc = {}

                for forge_ver in forge_versions_raw:
                    # Extract Minecraft version from Forge version string (e.g., "1.20.1-47.2.0" -> "1.20.1")
                    if '-' in forge_ver:
                        mc_ver = forge_ver.split('-')[0]
                        if mc_ver not in forge_by_mc or forge_ver > forge_by_mc[mc_ver]:
                            forge_by_mc[mc_ver] = forge_ver

                print(f"Grouped Forge versions: {len(forge_by_mc)} unique MC versions")

                # Sort by Minecraft version (newest first) - handle version parsing more safely
                def version_key(v):
                    try:
                        parts = v.split('.')
                        return [int(p) for p in parts[:3]]  # Take only first 3 parts to avoid issues
                    except:
                        return [0, 0, 0]  # Fallback for unparseable versions

                sorted_mc_versions = sorted(forge_by_mc.keys(), key=version_key, reverse=True)
                print(f"Sorted MC versions: {sorted_mc_versions[:5]}...")  # Show first 5

                for mc_ver in sorted_mc_versions:
                    forge_display = f"forge-{mc_ver}"
                    status = "✓" if is_version_installed(forge_display) else "↓"
                    versions.append(f"{status} Forge {mc_ver}")
            except Exception as e:
                print(f"Error processing Forge versions: {e}")
                pass

        if show_fabric:
            try:
                fabric_versions = [v["id"] for v in versions_data if v["type"] == "release" and v["id"] >= "1.14"]
                latest_loader = minecraft_launcher_lib.fabric.get_latest_loader_version()
                for mc_version in reversed(fabric_versions):
                    fabric_display = f"fabric-{mc_version}"
                    status = "✓" if is_version_installed(fabric_display) else "↓"
                    versions.append(f"{status} Fabric {mc_version}")
            except:
                pass

        return versions
    except:
        return []


def update_versions_combo(ui):
    config = load_config()
    versions = get_versions(
        show_forge=config.get("show_forge", False),
        show_fabric=config.get("show_fabric", False),
        show_snapshots=config.get("show_snapshots", False)
    )
    ui.comboBox.clear()

    # Get standard icons
    apply_icon = ui.comboBox.style().standardIcon(QStyle.SP_DialogApplyButton)
    down_icon = ui.comboBox.style().standardIcon(QStyle.SP_ArrowDown)

    for version in versions:
        # Remove the text indicator and add the item with appropriate icon
        if version.startswith("✓ "):
            display_text = version[2:]  # Remove "✓ "
            ui.comboBox.addItem(display_text)
            ui.comboBox.setItemIcon(ui.comboBox.count() - 1, apply_icon)
        elif version.startswith("↓ "):
            display_text = version[2:]  # Remove "↓ "
            ui.comboBox.addItem(display_text)
            ui.comboBox.setItemIcon(ui.comboBox.count() - 1, down_icon)
        else:
            ui.comboBox.addItem(version)

    if ui.comboBox.count() > 0:
        # Try to select the last launched version, otherwise select the first one
        last_version = config.get("last_version", "")
        # Find the index that corresponds to the last version
        selected_index = 0
        for i in range(ui.comboBox.count()):
            item_text = ui.comboBox.itemText(i)
            # Convert display text back to actual version format
            if item_text.startswith("Forge "):
                actual_version = f"forge-{item_text[6:]}"
            elif item_text.startswith("Fabric "):
                actual_version = f"fabric-{item_text[7:]}"
            else:
                actual_version = item_text

            if actual_version == last_version:
                selected_index = i
                break
        ui.comboBox.setCurrentIndex(selected_index)


def open_settings(parent, ui):
    config = load_config()

    dialog = QDialog(parent)
    dialog.setWindowTitle("Settings")
    dialog.resize(500, 450)  # Keep width at 500px, reduce height from 600px to 450px
    layout = QVBoxLayout()

    # Version display settings
    layout.addWidget(QLabel("Version Display Options:"))
    show_forge_check = QCheckBox("Show Forge versions")
    show_forge_check.setChecked(config.get("show_forge", False))
    layout.addWidget(show_forge_check)

    show_fabric_check = QCheckBox("Show Fabric versions")
    show_fabric_check.setChecked(config.get("show_fabric", False))
    layout.addWidget(show_fabric_check)

    show_snapshots_check = QCheckBox("Show Snapshot versions")
    show_snapshots_check.setChecked(config.get("show_snapshots", False))
    layout.addWidget(show_snapshots_check)

    layout.addWidget(QLabel(""))  # Spacer

    # RAM settings
    layout.addWidget(QLabel("RAM Settings:"))

    # Min RAM slider
    min_layout = QVBoxLayout()
    min_ram_val = config.get("ram", {}).get("min", "1024M")
    if min_ram_val.endswith("G"):
        min_slider_val = int(min_ram_val.replace("G", "")) * 1024  # Convert GB to MB for slider
        min_label_text = min_ram_val
    else:
        min_slider_val = int(min_ram_val.replace("M", ""))
        min_label_text = min_ram_val

    min_label = QLabel(f"Min RAM: {min_label_text}")
    min_slider = QSlider(Qt.Horizontal)
    min_slider.setRange(512, 4096)
    min_slider.setValue(min_slider_val)
    min_slider.valueChanged.connect(lambda v: min_label.setText(f"Min RAM: {v}M"))
    min_layout.addWidget(min_label)
    min_layout.addWidget(min_slider)
    layout.addLayout(min_layout)

    # Max RAM slider
    max_layout = QVBoxLayout()
    max_ram_val = config.get("ram", {}).get("max", "2048M")
    if max_ram_val.endswith("G"):
        max_slider_val = int(max_ram_val.replace("G", ""))
        max_label_text = max_ram_val
    else:
        max_slider_val = int(max_ram_val.replace("M", "")) // 1024  # Convert MB to GB for slider
        max_label_text = f"{max_slider_val}G"

    max_label = QLabel(f"Max RAM: {max_label_text}")
    max_slider = QSlider(Qt.Horizontal)
    total_ram_gb = psutil.virtual_memory().total // (1024**3)
    max_slider.setRange(1, total_ram_gb)
    max_slider.setValue(max_slider_val)
    max_slider.valueChanged.connect(lambda v: max_label.setText(f"Max RAM: {v}G"))
    max_layout.addWidget(max_label)
    max_layout.addWidget(max_slider)
    layout.addLayout(max_layout)

    layout.addWidget(QLabel(""))  # Spacer

    # Background settings
    layout.addWidget(QLabel("Background:"))
    current_bg_path = config.get("background_path", "saturn-background.png")
    bg_button = QPushButton(f"Background: {os.path.basename(current_bg_path)}")
    bg_button.setToolTip(f"Current background: {current_bg_path}\nClick to change")
    bg_button.clicked.connect(lambda: change_background(config, bg_button, parent, ui))
    layout.addWidget(bg_button)

    layout.addWidget(QLabel(""))  # Spacer

    # Auto RAM button
    layout.addWidget(QLabel("Quick Actions:"))
    auto_ram_button = QPushButton("Auto-detect Max RAM")
    auto_ram_button.setToolTip("Automatically set recommended Max RAM based on your system")
    auto_ram_button.clicked.connect(lambda: auto_detect_ram(max_slider, max_label, config))
    layout.addWidget(auto_ram_button)

    layout.addWidget(QLabel(""))  # Spacer

    # Buttons
    button_layout = QHBoxLayout()
    save_button = QPushButton("Save")
    save_button.clicked.connect(lambda: save_settings_and_update(
        config, show_forge_check, show_fabric_check, show_snapshots_check,
        min_slider, max_slider, ui, dialog))
    button_layout.addWidget(save_button)

    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)

    layout.addWidget(QLabel(""))  # Spacer

    # Update Section
    layout.addWidget(QLabel("Updates:"))
    update_layout = QHBoxLayout()
    
    from update_gui_classes import get_current_version, UpdateDialog
    version_label = QLabel(f"Current Version: {get_current_version()}")
    update_layout.addWidget(version_label)
    
    check_update_btn = QPushButton("Check for Updates")
    check_update_btn.clicked.connect(lambda: UpdateDialog(dialog).exec())
    update_layout.addWidget(check_update_btn)
    
    layout.addLayout(update_layout)

    layout.addWidget(QLabel(""))  # Spacer

    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()


def save_settings_and_update(config, show_forge_check, show_fabric_check, show_snapshots_check, min_slider, max_slider, ui, dialog):
    config["show_forge"] = show_forge_check.isChecked()
    config["show_fabric"] = show_fabric_check.isChecked()
    config["show_snapshots"] = show_snapshots_check.isChecked()
    config["ram"]["min"] = f"{min_slider.value()}M"
    config["ram"]["max"] = f"{max_slider.value()}G"
    save_config(config)
    update_versions_combo(ui)
    dialog.accept()


def start_game(ui):
    username = ui.lineEdit.text().strip()
    if not username:
        QMessageBox.warning(None, "Error", "Please enter a username")
        return
    version_display = ui.comboBox.currentText()
    if not version_display:
        QMessageBox.warning(None, "Error", "Please select a version")
        return

    # Extract actual version name from display string (remove status indicator)
    if version_display.startswith("✓ ") or version_display.startswith("↓ "):
        version = version_display[2:]  # Remove the indicator and space
    else:
        version = version_display

    # Handle Forge/Fabric display format
    if version.startswith("Forge "):
        version = f"forge-{version[6:]}"  # Convert back to forge-1.20.1 format
    elif version.startswith("Fabric "):
        version = f"fabric-{version[7:]}"  # Convert back to fabric-1.20.1 format

    # Clean up any existing thread
    if ui.launch_thread and ui.launch_thread.isRunning():
        ui.launch_thread.wait()

    ui.pushButton.setEnabled(False)

    ui.launch_thread = LaunchThread(version, username)
    ui.launch_thread.progress.connect(ui.progressBar.setValue)
    ui.launch_thread.show_progress.connect(lambda: ui.progressBar.setVisible(True))
    ui.launch_thread.hide_progress.connect(lambda: ui.progressBar.setVisible(False))
    ui.launch_thread.error_occurred.connect(lambda msg: QMessageBox.critical(None, "Launch Error", msg))
    ui.launch_thread.finished.connect(lambda: ui.pushButton.setEnabled(True))
    ui.launch_thread.start()


def open_mods_folder():
    """Open the mods folder in file explorer"""
    active_preset = preset_manager.get_active_preset()
    preset_path = preset_manager.get_preset_path(active_preset)
    mods_path = os.path.join(preset_path, "mods")
    try:
        # Create mods folder if it doesn't exist
        if not os.path.exists(mods_path):
            os.makedirs(mods_path)

        # Open folder in system file explorer
        if os.name == 'nt':  # Windows
            os.startfile(mods_path)
        elif os.name == 'posix':  # Linux/Mac
            if 'darwin' in os.sys.platform:  # macOS
                subprocess.run(['open', mods_path])
            else:  # Linux
                subprocess.run(['xdg-open', mods_path])
        print(f"Opened mods folder: {mods_path}")
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Could not open mods folder: {e}")


def auto_detect_ram(max_slider, max_label, config):
    """Auto-detect and set recommended Max RAM"""
    try:
        # Get total system RAM in GB
        total_ram_gb = psutil.virtual_memory().total // (1024**3)

        # Calculate recommended RAM (half of total, minimum 2GB)
        recommended_gb = max(2, total_ram_gb // 2)
        recommended_str = f"{recommended_gb}G"

        # Show confirmation dialog
        reply = QMessageBox.question(
            None,
            "Auto-detect RAM",
            f"System RAM: {total_ram_gb}GB\n\nRecommended Max RAM for Minecraft: {recommended_str}\n\nApply this setting?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes  # Default to Yes since it's recommended
        )

        if reply == QMessageBox.Yes:
            # Update the slider and label immediately
            max_slider.setValue(recommended_gb)
            max_label.setText(f"Max RAM: {recommended_str}")

            # Update config
            if 'ram' not in config:
                config['ram'] = {}
            config['ram']['max'] = recommended_str

            QMessageBox.information(None, "Success", f"Max RAM set to {recommended_str}")
        else:
            QMessageBox.information(None, "Cancelled", "RAM setting unchanged")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to detect RAM: {e}")


def delete_version(ui):
    """Delete the selected version"""
    version_display = ui.comboBox.currentText()
    if not version_display:
        QMessageBox.warning(None, "Error", "Please select a version to delete")
        return

    # Extract actual version name from display string
    if version_display.startswith("✓ ") or version_display.startswith("↓ "):
        version = version_display[2:]
        if version.startswith("Forge "):
            version = f"forge-{version[6:]}"
        elif version.startswith("Fabric "):
            version = f"fabric-{version[7:]}"
    else:
        version = version_display

    # Confirm deletion
    reply = QMessageBox.question(
        None,
        "Confirm Deletion",
        f"Are you sure you want to delete version '{version}'?\n\nThis will permanently remove all files for this version.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )

    if reply != QMessageBox.Yes:
        return

    try:
        minecraft_directory = os.path.abspath("saturn_launcher")

        # Determine the actual folder name to delete
        if version.startswith("forge-"):
            mc_version = version.replace("forge-", "")
            forge_version = minecraft_launcher_lib.forge.find_forge_version(mc_version)
            if forge_version:
                folder_name = minecraft_launcher_lib.forge.forge_to_installed_version(forge_version)
            else:
                QMessageBox.warning(None, "Error", "Could not find Forge version to delete")
                return
        elif version.startswith("fabric-"):
            mc_version = version.replace("fabric-", "")
            loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
            folder_name = f"fabric-loader-{loader_version}-{mc_version}"
        else:
            folder_name = version

        # Delete the version folder
        version_path = os.path.join(minecraft_directory, "versions", folder_name)
        if os.path.exists(version_path):
            import shutil
            shutil.rmtree(version_path)
            QMessageBox.information(None, "Success", f"Version '{version}' has been deleted successfully.")
            # Refresh the versions list
            update_versions_combo(ui)
        else:
            QMessageBox.warning(None, "Error", f"Version folder not found: {version_path}")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to delete version: {e}")


def get_backgrounds_dir():
    """Получить директорию для пользовательских фонов"""
    # Создаём папку в home директории
    bg_dir = os.path.expanduser("~/.saturn_launcher/backgrounds")
    if not os.path.exists(bg_dir):
        os.makedirs(bg_dir)
    return bg_dir


def change_background(config, bg_button, MainWindow, ui):
    """Change the background image"""
    try:
        # Open file dialog for image selection
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setWindowTitle("Select Background Image")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                selected_path = selected_files[0]
                print(f"Selected new background: {selected_path}")

                # Копируем файл в папку пользователя
                import shutil
                
                bg_dir = get_backgrounds_dir()
                filename = os.path.basename(selected_path)
                dest_path = os.path.join(bg_dir, filename)
                
                # Копируем файл
                shutil.copy2(selected_path, dest_path)
                print(f"Background copied to: {dest_path}")

                # Сохраняем полный путь (так как это уже не временная папка)
                config["background_path"] = dest_path
                save_config(config)

                # Обновляем кнопку
                bg_button.setText(f"Background: {filename}")
                bg_button.setToolTip(f"Current background: {filename}\nClick to change")

                # Convert Windows backslashes to forward slashes for CSS
                css_path = dest_path.replace('\\', '/')

                # Применяем фон немедленно
                ui.centralwidget.setStyleSheet(f"""
                    #centralwidget {{
                        background-image: url({css_path});
                        background-repeat: no-repeat;
                        background-position: center;
                    }}
                    #inputFrame {{
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 5px;
                    }}
                    QComboBox QAbstractItemView {{
                        min-width: 150px;
                        max-width: 180px;
                        padding: 2px;
                        margin: 0px;
                    }}
                """)

                QMessageBox.information(None, "Success", "Background changed successfully!")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to change background: {e}")
        import traceback
        traceback.print_exc()

def restore_last_username(ui):
    """Restore the last entered username"""
    config = load_config()
    last_username = config.get("last_username", "")
    if last_username:
        ui.lineEdit.setText(last_username)


class ModItemWidget(QWidget):
    """Custom widget for displaying mod information with icon"""
    def __init__(self, mod_data, parent=None):
        super().__init__(parent)
        self.mod_data = mod_data
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Mod icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        layout.addWidget(self.icon_label)

        # Mod info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Title and author
        title_text = self.mod_data.get("title", "Unknown Mod")
        author = self.mod_data.get("author", "Unknown")
        self.title_label = QLabel(f"{title_text} <span style='font-weight: normal; font-size: 10px; color: #666;'>(by {author})</span>")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(self.title_label)

        # Description
        desc = self.mod_data.get("description", "No description")
        if len(desc) > 120:
            desc = desc[:120] + "..."
        self.desc_label = QLabel(desc)
        self.desc_label.setStyleSheet("font-size: 10px; color: #666;")
        self.desc_label.setWordWrap(True)
        info_layout.addWidget(self.desc_label)

        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Downloads
        downloads = self.mod_data.get("downloads", 0)
        self.downloads_label = QLabel(f"📥 {downloads:,}")
        self.downloads_label.setStyleSheet("font-size: 9px; color: #888;")
        stats_layout.addWidget(self.downloads_label)

        # Categories
        categories = self.mod_data.get("categories", [])
        if categories:
            cat_text = ", ".join(categories[:2])  # Show max 2 categories
            if len(categories) > 2:
                cat_text += "..."
            self.categories_label = QLabel(f"🏷️ {cat_text}")
            self.categories_label.setStyleSheet("font-size: 9px; color: #888;")
            stats_layout.addWidget(self.categories_label)

        # Last updated
        date_modified = self.mod_data.get("date_modified", "")
        if date_modified:
            try:
                # Parse and format date
                from datetime import datetime
                dt = datetime.fromisoformat(date_modified.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%b %Y")
                self.date_label = QLabel(f"🔄 {formatted_date}")
                self.date_label.setStyleSheet("font-size: 9px; color: #888;")
                stats_layout.addWidget(self.date_label)
            except:
                pass

        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)

        layout.addLayout(info_layout, 1)

        # Install button
        self.install_button = QPushButton("Install")
        self.install_button.setFixedWidth(70)
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.install_button)

    def set_icon(self, pixmap):
        """Set the mod icon"""
        print(f"set_icon called with pixmap: {pixmap}, isNull: {pixmap.isNull() if pixmap else 'None'}")
        try:
            if pixmap and not pixmap.isNull():
                # Масштабируем изображение
                scaled_pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                print(f"Scaled pixmap size: {scaled_pixmap.width()}x{scaled_pixmap.height()}")

                # Устанавливаем изображение
                self.icon_label.setPixmap(scaled_pixmap)
                print(f"Pixmap set to label")

                # Убираем background color чтобы изображение было видно
                self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
            else:
                print(f"Pixmap is null or None, showing default icon")
                # Default icon
                self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
                self.icon_label.setText("📦")
        except Exception as e:
            print(f"Error in set_icon: {e}")
            import traceback
            traceback.print_exc()


class ModDownloadThread(QThread):
    """Thread for downloading mod icons"""
    icon_loaded = Signal(str, QPixmap)  # project_id, pixmap
    search_completed = Signal(list)  # list of mod data
    error_occurred = Signal(str)

    def __init__(self, query=""):
        super().__init__()
        self.query = query

    def run(self):
        try:
            # Search mods
            url = f"https://api.modrinth.com/v2/search?query={self.query}&limit=20"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            mods = []
            for hit in data.get("hits", []):
                mod_info = {
                    "project_id": hit.get("project_id"),
                    "title": hit.get("title", "Unknown"),
                    "description": hit.get("description", ""),
                    "downloads": hit.get("downloads", 0),
                    "categories": hit.get("categories", []),
                    "icon_url": hit.get("icon_url"),
                    "author": hit.get("author", "Unknown"),
                    "date_created": hit.get("date_created", ""),
                    "date_modified": hit.get("date_modified", ""),
                    "gallery": hit.get("gallery", []),
                    "versions": [],
                    "loaders": []
                }
                mods.append(mod_info)

            # Отправляем моды БЕЗ иконок
            self.search_completed.emit(mods)

            # ПОТОМ загружаем иконки
            for mod_info in mods:
                if mod_info["icon_url"]:
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        icon_response = requests.get(
                            mod_info["icon_url"],
                            timeout=10,
                            headers=headers,
                            allow_redirects=True
                        )
                        icon_response.raise_for_status()

                        image_bytes = icon_response.content

                        pixmap = QPixmap()
                        success = pixmap.loadFromData(image_bytes)

                        if success and not pixmap.isNull():
                            print(f"Successfully loaded icon for {mod_info['title']}: {pixmap.width()}x{pixmap.height()}")
                            self.icon_loaded.emit(mod_info["project_id"], pixmap)
                        else:
                            print(f"Failed to load icon for {mod_info['title']}: loadFromData returned False")

                    except requests.exceptions.Timeout:
                        print(f"Timeout loading icon for {mod_info['title']}")
                    except requests.exceptions.RequestException as e:
                        print(f"Network error loading icon for {mod_info['title']}: {e}")
                    except Exception as e:
                        print(f"Failed to process icon for {mod_info['title']}: {type(e).__name__}: {e}")

        except Exception as e:
            self.error_occurred.emit(f"Search failed: {str(e)}")


class ModInstallThread(QThread):
    """Thread for installing mods"""
    progress = Signal(int)
    finished = Signal(str)  # success message
    error_occurred = Signal(str)

    def __init__(self, mod_data, mc_version, loader):
        super().__init__()
        self.mod_data = mod_data
        self.mc_version = mc_version
        self.loader = loader

    def run(self):
        try:
            project_id = self.mod_data["project_id"]
            mod_title = self.mod_data["title"]

            # Get versions
            version_url = f"https://api.modrinth.com/v2/project/{project_id}/version?game_versions=[\"{self.mc_version}\"]&loaders=[\"{self.loader}\"]"
            version_response = requests.get(version_url, timeout=10)
            version_response.raise_for_status()
            versions = version_response.json()

            if not versions:
                self.error_occurred.emit(f"No compatible version found for {mod_title} on MC {self.mc_version} with {self.loader}")
                return

            # Take the latest version
            version_data = versions[0]
            primary_file = version_data["files"][0]
            download_url = primary_file["url"]
            filename = primary_file["filename"]

            # Create mods directory
            mods_dir = os.path.abspath("saturn_launcher/mods")
            if not os.path.exists(mods_dir):
                os.makedirs(mods_dir)

            # Download
            self.progress.emit(10)
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                filepath = os.path.join(mods_dir, filename)

                with open(filepath, 'wb') as f:
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = int(10 + (downloaded / total_size) * 90)
                                self.progress.emit(progress)

            self.progress.emit(100)
            self.finished.emit(f"Successfully installed {mod_title}!")

        except Exception as e:
            self.error_occurred.emit(f"Installation failed: {str(e)}")


class ModDownloadDialog(QDialog):
    """Dialog for downloading mods from Modrinth"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_thread = None
        self.install_thread = None
        self.mod_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Download Mods - Saturn Launcher")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for mods...")
        self.search_input.returnPressed.connect(self.search_mods)
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_mods)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(5)
        self.results_layout.setContentsMargins(10, 10, 10, 10)

        # Add stretch at the end
        self.results_layout.addStretch()

        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

    def search_mods(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search query")
            return

        # Clear previous results
        self.clear_results()
        self.status_label.setText("Searching...")
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Start search thread
        self.search_thread = ModDownloadThread(query)
        self.search_thread.search_completed.connect(self.on_search_completed)
        self.search_thread.icon_loaded.connect(self.on_icon_loaded)
        self.search_thread.error_occurred.connect(self.on_search_error)
        self.search_thread.start()

    def clear_results(self):
        """Clear all mod widgets"""
        for widget in self.mod_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.mod_widgets.clear()

    def on_search_completed(self, mods):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

        if not mods:
            self.status_label.setText("No mods found")
            return

        self.status_label.setText(f"Found {len(mods)} mods")

        for mod_data in mods:
            print(f"Mod: {mod_data['title']}, Icon URL: {mod_data['icon_url']}")

        for mod_data in mods:
            widget = ModItemWidget(mod_data)
            widget.install_button.clicked.connect(lambda checked=False, m=mod_data: self.install_mod(m))
            self.results_layout.addWidget(widget)
            self.mod_widgets[mod_data["project_id"]] = widget

    def on_icon_loaded(self, project_id, pixmap):
        """Handle icon loading"""
        print(f"on_icon_loaded called for project: {project_id}, pixmap: {pixmap}")
        if project_id in self.mod_widgets:
            widget = self.mod_widgets[project_id]
            print(f"Setting icon for widget: {widget}")
            widget.set_icon(pixmap)
            print(f"Icon set successfully")
        else:
            print(f"Widget not found for project_id: {project_id}")

    def on_search_error(self, error_msg):
        """Handle search error"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Search Error", error_msg)

    def install_mod(self, mod_data):
        """Start mod installation"""
        # First fetch available versions for this mod
        self.fetch_mod_versions(mod_data)

    def fetch_mod_versions(self, mod_data):
        """Fetch available versions for a specific mod"""
        try:
            project_id = mod_data["project_id"]
            url = f"https://api.modrinth.com/v2/project/{project_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            project_data = response.json()

            # Get available game versions and loaders
            game_versions = project_data.get("game_versions", [])
            loaders = project_data.get("loaders", [])

            # Sort versions by semantic version (newest first)
            def version_key(v):
                try:
                    parts = v.split('.')
                    # Pad parts to ensure consistent sorting
                    return [int(p) for p in parts] + [0] * (3 - len(parts))
                except:
                    return [0, 0, 0]

            available_versions = sorted(game_versions, key=version_key, reverse=True)

            # Filter loaders to supported ones
            available_loaders = [l for l in loaders if l in ["fabric", "forge", "quilt", "neoforge"]]

            print(f"Mod {mod_data['title']}: {len(available_versions)} versions, {len(available_loaders)} loaders")

            self.show_install_dialog(mod_data, available_versions, available_loaders)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch mod versions: {str(e)}")

    def show_install_dialog(self, mod_data, available_versions, available_loaders):
        """Show the installation dialog with actual available options"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Install {mod_data['title']}")
        dialog.resize(350, 200)

        layout = QVBoxLayout(dialog)

        # Mod info
        info_label = QLabel(f"<b>{mod_data['title']}</b><br>"
                           f"Author: {mod_data.get('author', 'Unknown')}<br>"
                           f"Downloads: {mod_data.get('downloads', 0):,}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addWidget(QLabel(""))  # Spacer

        # MC Version selection
        layout.addWidget(QLabel("Minecraft Version:"))
        self.mc_combo = QComboBox()
        self.mc_combo.addItems(available_versions)
        if available_versions:
            self.mc_combo.setCurrentIndex(0)
        layout.addWidget(self.mc_combo)

        # Loader selection
        layout.addWidget(QLabel("Mod Loader:"))
        self.loader_combo = QComboBox()
        self.loader_combo.addItems(available_loaders)
        if available_loaders:
            self.loader_combo.setCurrentIndex(0)
        layout.addWidget(self.loader_combo)

        # Compatibility info
        compat_label = QLabel(f"<i>Available versions: {', '.join(available_versions[:5])}{'...' if len(available_versions) > 5 else ''}</i>")
        compat_label.setWordWrap(True)
        compat_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(compat_label)

        layout.addWidget(QLabel(""))  # Spacer

        # Buttons
        buttons_layout = QHBoxLayout()
        install_btn = QPushButton("Install")
        install_btn.clicked.connect(lambda: self.start_install(dialog, mod_data))
        buttons_layout.addWidget(install_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        dialog.exec()

    def start_install(self, dialog, mod_data):
        """Start the installation process"""
        mc_version = self.mc_combo.currentText()
        loader = self.loader_combo.currentText()
        dialog.accept()

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Installing {mod_data['title']}...")

        # Start install thread
        self.install_thread = ModInstallThread(mod_data, mc_version, loader)
        self.install_thread.progress.connect(self.progress_bar.setValue)
        self.install_thread.finished.connect(self.on_install_finished)
        self.install_thread.error_occurred.connect(self.on_install_error)
        self.install_thread.start()

    def on_install_finished(self, message):
        """Handle successful installation"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        QMessageBox.information(self, "Success", message)

    def on_install_error(self, error_msg):
        """Handle installation error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Installation failed")
        QMessageBox.critical(self, "Installation Error", error_msg)


def open_mod_download_dialog(parent):
    """Open the mod download dialog"""
    dialog = ModDownloadDialog(parent)
    dialog.exec()


# ================================
# PRESET UI FUNCTIONS
# ================================

def update_presets_combo(ui):
    """Update the presets combobox list"""
    ui.presetComboBox.blockSignals(True)
    ui.presetComboBox.clear()
    
    presets = preset_manager.list_presets()
    active_preset = preset_manager.get_active_preset()
    
    # Get icons
    try:
        # Use standard icons from QApplication style if possible, or fallback
        active_icon = ui.presetComboBox.style().standardIcon(QStyle.SP_DialogYesButton)
        folder_icon = ui.presetComboBox.style().standardIcon(QStyle.SP_DirIcon)
        zip_icon = ui.presetComboBox.style().standardIcon(QStyle.SP_FileIcon) 
    except:
        active_icon = QIcon()
        
    for preset in presets:
        name = preset['name']
        ui.presetComboBox.addItem(name)
        
        # Set icon for active preset
        index = ui.presetComboBox.count() - 1
        if name == active_preset:
            ui.presetComboBox.setItemIcon(index, active_icon)
        elif preset.get('compressed', False):
             # Maybe show zip icon for compressed?
             pass
        
    # Select active preset
    index = ui.presetComboBox.findText(active_preset)
    if index >= 0:
        ui.presetComboBox.setCurrentIndex(index)
    
    ui.presetComboBox.blockSignals(False)
    update_preset_status(ui)

def create_new_preset(ui):
    """Create a new preset via dialog"""
    name, ok = QInputDialog.getText(None, "New Preset", "Enter name for new preset:")
    if ok and name:
        name = name.strip()
        if not name:
             return
             
        if preset_manager.preset_exists(name):
             QMessageBox.warning(None, "Error", f"Preset '{name}' already exists.")
             return
             
        # Create it
        final_name = preset_manager.create_preset(name)
        
        # Switch to it
        preset_manager.switch_preset(final_name)
        
        # Update UI
        update_presets_combo(ui)
        update_versions_combo(ui)
        QMessageBox.information(None, "Success", f"Created and switched to preset '{final_name}'")

def update_preset_status(ui):
    """Update buttons based on selected preset"""
    preset_name = ui.presetComboBox.currentText()
    
    # Check if preset exists
    if preset_manager.preset_exists(preset_name):
        is_compressed = preset_manager.is_preset_compressed(preset_name)
        
        # Update Archive button
        if is_compressed:
            ui.archiveButton.setText("Unzip")
            ui.archiveButton.setStyleSheet("background-color: #FFAA00; color: black; font-weight: bold;")
        else:
            ui.archiveButton.setText("Archive...")
            ui.archiveButton.setStyleSheet("")
            
    else:
        # New preset (typed in manually)
        ui.archiveButton.setText("Archive...")

def on_preset_changed(ui):
    """Handle preset selection change"""
    preset_name = ui.presetComboBox.currentText()
    
    if not preset_manager.preset_exists(preset_name):
        update_preset_status(ui)
        return

    if preset_manager.is_preset_compressed(preset_name):
         update_preset_status(ui)
         return

    # Auto-switch if it's a valid directory preset
    old_preset = preset_manager.get_active_preset()
    if preset_name != old_preset:
        success = preset_manager.switch_preset(preset_name)
        if success:
             # Refresh combo to update icons (move checkmark)
             # This will trigger on_preset_changed again but since name match active, it fall through
             update_presets_combo(ui)
             # Update versions list
             update_versions_combo(ui)
             print(f"Switched GUI to preset: {preset_name}")
    
    # Always ensure button state is correct (fixes bug when switching back to active preset)
    update_preset_status(ui)

def toggle_archive_preset(ui):
    """Handle archive/unzip button click"""
    preset_name = ui.presetComboBox.currentText()
    
    operation = None
    target_preset = None
    
    # If selected is a compressed preset, UNZIP it
    if preset_manager.preset_exists(preset_name) and preset_manager.is_preset_compressed(preset_name):
        operation = 'unzip'
        target_preset = preset_name

    else:
        # Otherwise, show Archive Dialog to choose a preset to ARCHIVE
        presets = preset_manager.list_presets()
        active_preset = preset_manager.get_active_preset()
        
        # Filter: exists, directory (not compressed), not active
        archivable = [p['name'] for p in presets 
                      if not p['compressed'] and p['name'] != active_preset]
        
        if not archivable:
            QMessageBox.information(None, "Archive Preset", "No inactive presets available to archive.\n\nNote: You cannot archive the currently active preset.")
            return
            
        item, ok = QInputDialog.getItem(None, "Archive Preset", "Select preset to archive:", archivable, 0, False)
        
        if ok and item:
            confirm = QMessageBox.question(None, "Confirm Archive", 
                                          f"Are you sure you want to archive '{item}'?\nThe original folder will be deleted after verification.",
                                          QMessageBox.Yes | QMessageBox.No)
            
            if confirm == QMessageBox.Yes:
                operation = 'archive'
                target_preset = item
            else:
                return
        else:
            return

    # Execute operation with progress dialog
    if operation and target_preset:
        # Create progress dialog
        op_text = "Archiving" if operation == 'archive' else "Decompressing"
        progress = QProgressDialog(f"{op_text} '{target_preset}'...", None, 0, 0, None)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None) # Disable cancel
        progress.show()
        
        ui.archiveButton.setEnabled(False)
        
        # Create and run thread
        ui.preset_thread = PresetThread(operation, target_preset)
        
        def on_finished(success, msg):
            progress.close()
            ui.archiveButton.setEnabled(True)
            if success:
                QMessageBox.information(None, "Success", msg)
                update_presets_combo(ui) # Refresh list
            else:
                QMessageBox.critical(None, "Error", msg)
                
        ui.preset_thread.finished.connect(on_finished)
        ui.preset_thread.start()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Populate presets comboBox
    update_presets_combo(ui)

    # Populate versions comboBox
    update_versions_combo(ui)

    # Restore last username
    restore_last_username(ui)

    # Connect settings button
    ui.settingsButton.clicked.connect(lambda: open_settings(MainWindow, ui))
    
    # Connect preset controls
    ui.presetComboBox.currentTextChanged.connect(lambda: on_preset_changed(ui))
    ui.createPresetButton.clicked.connect(lambda: create_new_preset(ui))
    ui.archiveButton.clicked.connect(lambda: toggle_archive_preset(ui))

    # Connect start game button
    ui.pushButton.clicked.connect(lambda: start_game(ui))

    # Connect mods folder button
    ui.modsButton.clicked.connect(open_mods_folder)

    # Connect download mods button
    ui.downloadModsButton.clicked.connect(lambda: open_mod_download_dialog(MainWindow))
    
    # Import shader download functionality
    from shader_download_classes import open_shader_download_dialog
    from update_gui_classes import UpdateDialog
    ui.downloadShadersButton.clicked.connect(lambda: open_shader_download_dialog(MainWindow))
    
    # Connect delete version button
    ui.deleteButton.clicked.connect(lambda: delete_version(ui))

    # Set window icon
    icon_pixmap = QPixmap(get_resource_path("saturn_title.png"))
    MainWindow.setWindowIcon(QIcon(icon_pixmap))

    # Set logo image in label
    ui.label.setPixmap(icon_pixmap.scaled(ui.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    ui.label.setAlignment(Qt.AlignCenter)

    MainWindow.show()
    sys.exit(app.exec())
