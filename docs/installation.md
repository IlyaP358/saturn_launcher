# Installation Guide

## Pre-compiled Versions

Pre-compiled versions are available in the [Releases](https://github.com/IlyaP358/saturn_launcher/releases) tab.

> [!TIP]
> **Recommendation**: It is highly recommended to create a dedicated folder (e.g., `SaturnLauncher`) and place the executable script there. The launcher will download game files and assets into the same directory where it is located.

## <img src="https://raw.githubusercontent.com/IlyaP358/saturn-web/main/windows_logo.png" width="20" alt="Windows"> Windows

1. Download `saturn_win.exe` from the [Releases](https://github.com/IlyaP358/saturn_launcher/releases) page.
2. Place it in your desired folder (e.g., `C:\Games\SaturnLauncher`).
3. Double-click `saturn_win.exe` to launch.
   * *Note: You might need to approve the application in Windows Defender as it is a self-signed executable.*

## <img src="https://raw.githubusercontent.com/IlyaP358/saturn-web/main/linux_logo.png" width="16" alt="Linux"> Linux

1. Download `saturn_linux` from the [Releases](https://github.com/IlyaP358/saturn_launcher/releases) page.
2. Place it in your desired folder (e.g., `~/Games/SaturnLauncher`).
3. Open a terminal in that folder.
4. Make the file executable:
   ```bash
   chmod +x saturn_linux
   ```
5. Run the launcher:
   ```bash
   ./saturn_linux
   ```

## macOS

*Support for macOS is currently in planning stages.*

## <img src="https://raw.githubusercontent.com/IlyaP358/saturn-web/main/linux_logo.png" width="16" alt="Linux"> Linux (Flatpak)

Flatpak packages are available for easy installation on Linux distributions.

### Prerequisites
- Flatpak installed on your system
- Flathub repository added (usually included by default)

### Installation

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

### Usage

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
