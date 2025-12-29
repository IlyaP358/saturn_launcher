import minecraft_launcher_lib
import subprocess
import uuid
import json
import os
import psutil
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
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFrame, QFileDialog)

class Ui_MainWindow(object):
    def __init__(self):
        self.launch_thread = None

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
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
        background_path = config.get("background_path", "saturn-background.png")

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

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Username...", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Start Game", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Saturn Launcher", None))
    # retranslateUi


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
        try:
            print(f"Starting launch process for version: {self.version}, username: {self.username}")

            minecraft_directory = os.path.abspath("saturn_launcher")
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
                        try:
                            minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_directory, callback=self.progress_callback)
                        except Exception as e:
                            print(f"Forge install with callback failed: {e}, trying without callback")
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
                print("Loading config.json...")
                with open('config.json', 'r') as f:
                    config = json.load(f)
                print(f"Config loaded: {config}")
                print(f"Config type: {type(config)}")
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
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {"ram": {"min": "1024M", "max": "2048M"}, "show_forge": False, "show_fabric": False, "show_snapshots": False, "last_version": "", "last_username": "", "background_path": "saturn-background.png"}


def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)


def is_version_installed(version):
    """Check if a version is installed"""
    try:
        minecraft_directory = os.path.abspath("saturn_launcher")

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
    bg_button.clicked.connect(lambda: change_background(config, bg_button))
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
    mods_path = os.path.abspath("saturn_launcher/mods")
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


def change_background(config, bg_button):
    """Change the background image"""
    try:
        # Get current background path for initial directory
        current_bg = config.get("background_path", "saturn-background.png")
        current_dir = os.path.dirname(os.path.abspath(current_bg)) if os.path.exists(current_bg) else ""

        # Open file dialog for image selection
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setWindowTitle("Select Background Image")
        if current_dir:
            file_dialog.setDirectory(current_dir)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                new_bg_path = selected_files[0]
                print(f"Selected new background: {new_bg_path}")

                # Update config
                config["background_path"] = new_bg_path
                save_config(config)

                # Update button text
                bg_button.setText(f"Background: {os.path.basename(new_bg_path)}")
                bg_button.setToolTip(f"Current background: {new_bg_path}\nClick to change")

                QMessageBox.information(None, "Success", "Background changed successfully!\n\nRestart the launcher to see the new background.")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to change background: {e}")


def restore_last_username(ui):
    """Restore the last entered username"""
    config = load_config()
    last_username = config.get("last_username", "")
    if last_username:
        ui.lineEdit.setText(last_username)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Populate versions comboBox
    update_versions_combo(ui)

    # Restore last username
    restore_last_username(ui)

    # Connect settings button
    ui.settingsButton.clicked.connect(lambda: open_settings(MainWindow, ui))

    # Connect start game button
    ui.pushButton.clicked.connect(lambda: start_game(ui))

    # Connect mods folder button
    ui.modsButton.clicked.connect(open_mods_folder)

    # Connect delete version button
    ui.deleteButton.clicked.connect(lambda: delete_version(ui))

    # Set window icon
    icon_pixmap = QPixmap("saturn_title.png")
    MainWindow.setWindowIcon(QIcon(icon_pixmap))

    # Set logo image in label
    ui.label.setPixmap(icon_pixmap.scaled(ui.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    ui.label.setAlignment(Qt.AlignCenter)

    MainWindow.show()
    sys.exit(app.exec())
