# Saturn Launcher 🪐

![Status](https://img.shields.io/badge/Status-Early_Development-orange)
![Platform](https://img.shields.io/badge/Platform-Windows_|_Linux-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)

**Saturn Launcher** is a lightweight, fast, and easy-to-use console-based Minecraft launcher. 

> [!NOTE]
> **Early Development**: This project is currently in early development. 
> - ✅ **CLI Version**: Fully functional and ready for use.
> - 🚧 **GUI Version**: Coming soon in future updates.

## 🚀 Features

- **Fast & Lightweight**: Optimized for performance with minimal resource usage.
- **Cross-Platform**: Runs on Windows and Linux (macOS support planned).
- **User Friendly**: Simple command-line interface with rich text formatting.

## 📥 Installation & Usage

Pre-compiled versions are available in the `saturn-builds` directory. 

> [!TIP]
> **Recommendation**: It is highly recommended to create a dedicated folder (e.g., `SaturnLauncher`) and place the executable script there. The launcher will download game files and assets into the same directory where it is located.

### 🪟 Windows

1.  Navigate to the `saturn-builds` folder.
2.  Copy `saturn_win.exe` to your desired folder (e.g., `C:\Games\SaturnLauncher`).
3.  Double-click `saturn_win.exe` to launch.
    *   *Note: You might need to approve the application in Windows Defender as it is a self-signed executable.*

### 🐧 Linux

1.  Navigate to the `saturn-builds` folder.
2.  Copy `saturn_linux` to your desired folder (e.g., `~/Games/SaturnLauncher`).
3.  Open a terminal in that folder.
4.  Make the file executable:
    ```bash
    chmod +x saturn_linux
    ```
5.  Run the launcher:
    ```bash
    ./saturn_linux
    ```

### 🍎 macOS
*Support for macOS is currently in planning stages.*

### 🐧 Linux (Flatpak)

Flatpak packages are available for easy installation on Linux distributions.

#### Prerequisites
- Flatpak installed on your system
- Flathub repository added (usually included by default)

#### Installation

**From Flathub** (when published):
```bash
# CLI version
flatpak install flathub com.github.IlyaP358.SaturnLauncher

# GUI version
flatpak install flathub com.github.IlyaP358.SaturnLauncher.GUI
```

**From local bundle** (for testing or manual distribution):
```bash
# Build the packages
./build-flatpak.sh

# Install the bundles
flatpak install SaturnLauncher.flatpak
flatpak install SaturnLauncher.GUI.flatpak
```

#### Usage

After installation, you can run the launchers:

**CLI Version:**
```bash
saturn
# or
flatpak run com.github.IlyaP358.SaturnLauncher
```

**GUI Version:**
```bash
saturn-gui
# or
flatpak run com.github.IlyaP358.SaturnLauncher.GUI
```

The applications will also appear in your desktop environment's application menu.

## 🛠️ Development

If you want to modify the source code or run the latest version from the repository, follow these steps.

### Prerequisites
- Python 3.x installed.

### Setup

1.  Clone the repository or download the source code.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows**: `venv\Scripts\activate`
    *   **Linux/macOS**: `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Source
To run the launcher from source:
```bash
python saturn.py
```

## 📦 Building

To create a standalone executable, use PyInstaller:

```bash
pyinstaller saturn_windows.spec  # For Windows
# or
pyinstaller saturn_linux.spec    # For Linux
```

### Flatpak Packaging

To build Flatpak packages for Linux distribution:

#### Prerequisites
- `flatpak` and `flatpak-builder` installed
- `org.freedesktop.Platform` and `org.freedesktop.Sdk` runtime installed

#### Building
```bash
# Make build script executable
chmod +x build-flatpak.sh

# Build both CLI and GUI versions
./build-flatpak.sh
```

This will create `SaturnLauncher.flatpak` and `SaturnLauncher.GUI.flatpak` bundles.

#### Publishing to Flathub

1. **Fork and clone the Flathub repository:**
   ```bash
   git clone https://github.com/flathub/flathub.git
   cd flathub
   ```

2. **Create a new directory for your application:**
   ```bash
   mkdir -p com.github.IlyaP358.SaturnLauncher
   cd com.github.IlyaP358.SaturnLauncher
   ```

3. **Copy the manifest file:**
   Copy `com.github.IlyaP358.SaturnLauncher.yml` to this directory.

4. **Create metadata files:**
   - `com.github.IlyaP358.SaturnLauncher.metainfo.xml` (AppStream metadata)
   - Screenshots and icons as needed

5. **Test the build locally:**
   ```bash
   flatpak run org.flatpak.Builder --force-clean --repo=repo build com.github.IlyaP358.SaturnLauncher.yml
   ```

6. **Submit a pull request** to the Flathub repository with your manifest and metadata.

For the GUI version, repeat the process with `com.github.IlyaP358.SaturnLauncher.GUI.yml`.
