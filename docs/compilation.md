# Compilation Guide

## Building Standalone Executables

To create a standalone executable, use PyInstaller:

```bash
pyinstaller saturn_windows.spec  # For Windows
# or
pyinstaller saturn_linux.spec    # For Linux
```

## Flatpak Packaging

To build Flatpak packages for Linux distribution:

### Prerequisites
- `flatpak` and `flatpak-builder` installed
- `org.freedesktop.Platform` and `org.freedesktop.Sdk` runtime installed

### Building
```bash
# Make build script executable
chmod +x build-flatpak.sh

# Build both CLI and GUI versions
./build-flatpak.sh
```

This will create `SaturnLauncher.flatpak` and `SaturnLauncher.GUI.flatpak` bundles.
