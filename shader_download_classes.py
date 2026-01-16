# Shader Download Dialog and Supporting Classes
# This file contains the shader download functionality for Saturn Launcher GUI

import os
import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QScrollArea, QWidget, QComboBox,
    QFrame, QMessageBox
)


class ShaderItemWidget(QFrame):
    """Widget for displaying a single shader in the search results"""
    def __init__(self, shader_data):
        super().__init__()
        self.shader_data = shader_data
        self.setup_ui()

    def setup_ui(self):
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QFrame:hover {
                border: 1px solid #4CAF50;
                background-color: #f9f9f9;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setScaledContents(False)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
        self.icon_label.setText("🎨")  # Default shader icon
        layout.addWidget(self.icon_label)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        # Title
        self.title_label = QLabel(f"<b>{self.shader_data['title']}</b>")
        self.title_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        info_layout.addWidget(self.title_label)

        # Description
        description = self.shader_data.get('description', 'No description')
        if len(description) > 100:
            description = description[:100] + "..."
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("font-size: 10px; color: #666;")
        self.desc_label.setWordWrap(True)
        info_layout.addWidget(self.desc_label)

        # Stats (downloads, author)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        # Author
        author = self.shader_data.get('author', 'Unknown')
        self.author_label = QLabel(f"👤 {author}")
        self.author_label.setStyleSheet("font-size: 9px; color: #888;")
        stats_layout.addWidget(self.author_label)

        # Downloads
        downloads = self.shader_data.get('downloads', 0)
        self.downloads_label = QLabel(f"⬇ {downloads:,}")
        self.downloads_label.setStyleSheet("font-size: 9px; color: #888;")
        stats_layout.addWidget(self.downloads_label)

        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)

        layout.addLayout(info_layout, 1)

        # Install button
        self.install_button = QPushButton("Install")
        self.install_button.setFixedWidth(70)
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.install_button)

    def set_icon(self, pixmap):
        """Set the shader icon"""
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
            self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        else:
            self.icon_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
            self.icon_label.setText("🎨")


class ShaderDownloadThread(QThread):
    """Thread for downloading shader icons and searching"""
    icon_loaded = Signal(str, QPixmap)  # project_id, pixmap
    search_completed = Signal(list)  # list of shader data
    error_occurred = Signal(str)

    def __init__(self, query=""):
        super().__init__()
        self.query = query

    def run(self):
        try:
            # Search shaders on Modrinth
            url = f"https://api.modrinth.com/v2/search?query={self.query}&limit=20&facets=[[\"project_type:shader\"]]"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            shaders = []
            for hit in data.get("hits", []):
                shader_info = {
                    "project_id": hit.get("project_id"),
                    "title": hit.get("title", "Unknown"),
                    "description": hit.get("description", ""),
                    "downloads": hit.get("downloads", 0),
                    "categories": hit.get("categories", []),
                    "icon_url": hit.get("icon_url"),
                    "author": hit.get("author", "Unknown"),
                    "date_created": hit.get("date_created", ""),
                    "date_modified": hit.get("date_modified", ""),
                }
                shaders.append(shader_info)

            # Send shaders without icons first
            self.search_completed.emit(shaders)

            # Then load icons
            for shader_info in shaders:
                if shader_info["icon_url"]:
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        icon_response = requests.get(
                            shader_info["icon_url"],
                            timeout=10,
                            headers=headers,
                            allow_redirects=True
                        )
                        icon_response.raise_for_status()

                        pixmap = QPixmap()
                        success = pixmap.loadFromData(icon_response.content)

                        if success and not pixmap.isNull():
                            self.icon_loaded.emit(shader_info["project_id"], pixmap)

                    except Exception as e:
                        print(f"Failed to load icon for {shader_info['title']}: {e}")

        except Exception as e:
            self.error_occurred.emit(f"Search failed: {str(e)}")


class ShaderInstallThread(QThread):
    """Thread for installing shaders"""
    progress = Signal(int)
    finished = Signal(str)  # success message
    error_occurred = Signal(str)

    def __init__(self, shader_data, mc_version):
        super().__init__()
        self.shader_data = shader_data
        self.mc_version = mc_version

    def run(self):
        try:
            project_id = self.shader_data["project_id"]
            shader_title = self.shader_data["title"]

            # Get versions
            version_url = f"https://api.modrinth.com/v2/project/{project_id}/version?game_versions=[\"{self.mc_version}\"]"
            version_response = requests.get(version_url, timeout=10)
            version_response.raise_for_status()
            versions = version_response.json()

            if not versions:
                self.error_occurred.emit(f"No compatible version found for {shader_title} on MC {self.mc_version}")
                return

            # Take the latest version
            version_data = versions[0]
            primary_file = version_data["files"][0]
            download_url = primary_file["url"]
            filename = primary_file["filename"]

            # Create shaderpacks directory
            shaders_dir = os.path.abspath("saturn_launcher/shaderpacks")
            if not os.path.exists(shaders_dir):
                os.makedirs(shaders_dir)

            # Download
            self.progress.emit(10)
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                filepath = os.path.join(shaders_dir, filename)

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
            self.finished.emit(f"Successfully installed {shader_title}!")

        except Exception as e:
            self.error_occurred.emit(f"Installation failed: {str(e)}")


class ShaderDownloadDialog(QDialog):
    """Dialog for downloading shaders from Modrinth"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_thread = None
        self.install_thread = None
        self.shader_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Download Shaders - Saturn Launcher")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for shaders (e.g., BSL, Complementary, Seus)...")
        self.search_input.returnPressed.connect(self.search_shaders)
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_shaders)
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

    def search_shaders(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search query")
            return

        # Clear previous results
        self.clear_results()
        self.status_label.setText("Searching for shaders...")
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Start search thread
        self.search_thread = ShaderDownloadThread(query)
        self.search_thread.search_completed.connect(self.on_search_completed)
        self.search_thread.icon_loaded.connect(self.on_icon_loaded)
        self.search_thread.error_occurred.connect(self.on_search_error)
        self.search_thread.start()

    def clear_results(self):
        """Clear all shader widgets"""
        for widget in self.shader_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.shader_widgets.clear()

    def on_search_completed(self, shaders):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

        if not shaders:
            self.status_label.setText("No shaders found")
            return

        self.status_label.setText(f"Found {len(shaders)} shaders")

        for shader_data in shaders:
            widget = ShaderItemWidget(shader_data)
            widget.install_button.clicked.connect(lambda checked=False, s=shader_data: self.install_shader(s))
            self.results_layout.insertWidget(self.results_layout.count() - 1, widget)
            self.shader_widgets[shader_data["project_id"]] = widget

    def on_icon_loaded(self, project_id, pixmap):
        """Handle icon loading"""
        if project_id in self.shader_widgets:
            self.shader_widgets[project_id].set_icon(pixmap)

    def on_search_error(self, error_msg):
        """Handle search error"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Search Error", error_msg)

    def install_shader(self, shader_data):
        """Start shader installation"""
        self.fetch_shader_versions(shader_data)

    def fetch_shader_versions(self, shader_data):
        """Fetch available versions for a specific shader"""
        try:
            project_id = shader_data["project_id"]
            url = f"https://api.modrinth.com/v2/project/{project_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            project_data = response.json()

            # Get available game versions
            game_versions = project_data.get("game_versions", [])

            # Sort versions
            def version_key(v):
                try:
                    parts = v.split('.')
                    return [int(p) for p in parts] + [0] * (3 - len(parts))
                except:
                    return [0, 0, 0]

            available_versions = sorted(game_versions, key=version_key, reverse=True)

            self.show_install_dialog(shader_data, available_versions)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch shader versions: {str(e)}")

    def show_install_dialog(self, shader_data, available_versions):
        """Show the installation dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Install {shader_data['title']}")
        dialog.resize(350, 180)

        layout = QVBoxLayout(dialog)

        # Shader info
        info_label = QLabel(f"<b>{shader_data['title']}</b><br>"
                           f"Author: {shader_data.get('author', 'Unknown')}<br>"
                           f"Downloads: {shader_data.get('downloads', 0):,}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addWidget(QLabel(""))  # Spacer

        # MC Version selection
        layout.addWidget(QLabel("Minecraft Version:"))
        mc_combo = QComboBox()
        mc_combo.addItems(available_versions)
        if available_versions:
            mc_combo.setCurrentIndex(0)
        layout.addWidget(mc_combo)

        layout.addWidget(QLabel(""))  # Spacer

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        install_btn = QPushButton("Install")
        install_btn.clicked.connect(lambda: self.start_installation(
            shader_data, mc_combo.currentText(), dialog
        ))
        buttons_layout.addWidget(install_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        dialog.exec()

    def start_installation(self, shader_data, mc_version, dialog):
        """Start the actual installation"""
        dialog.accept()

        # Show progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Installing Shader")
        progress_dialog.resize(300, 100)
        progress_layout = QVBoxLayout(progress_dialog)

        progress_layout.addWidget(QLabel(f"Installing {shader_data['title']}..."))

        progress_bar = QProgressBar()
        progress_layout.addWidget(progress_bar)

        progress_dialog.show()

        # Start installation thread
        self.install_thread = ShaderInstallThread(shader_data, mc_version)
        self.install_thread.progress.connect(progress_bar.setValue)
        self.install_thread.finished.connect(lambda msg: self.on_install_finished(msg, progress_dialog))
        self.install_thread.error_occurred.connect(lambda msg: self.on_install_error(msg, progress_dialog))
        self.install_thread.start()

    def on_install_finished(self, message, progress_dialog):
        """Handle successful installation"""
        progress_dialog.close()
        QMessageBox.information(self, "Success", message)

    def on_install_error(self, message, progress_dialog):
        """Handle installation error"""
        progress_dialog.close()
        QMessageBox.critical(self, "Error", message)


def open_shader_download_dialog(parent):
    """Open the shader download dialog"""
    dialog = ShaderDownloadDialog(parent)
    dialog.exec()
