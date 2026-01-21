#!/bin/bash

# Build script for Saturn Launcher Flatpak packages

set -e

echo "Building Saturn Launcher Flatpak packages..."

# Build binaries with PyInstaller first
echo "Building binaries with PyInstaller..."
# Use pyinstaller from venv
./venv/bin/pyinstaller --clean saturn_linux.spec
./venv/bin/pyinstaller --clean saturn_gui_linux.spec

# Build CLI Flatpak
echo "Building CLI Flatpak..."
# We need --repo to create an OSTree repository that build-bundle can read
flatpak-builder --force-clean --repo=repo-cli build-cli com.github.IlyaP358.SaturnLauncher.yml

# Build GUI Flatpak
echo "Building GUI Flatpak..."
flatpak-builder --force-clean --repo=repo-gui build-gui com.github.IlyaP358.SaturnLauncher.GUI.yml

echo "Building bundles..."

# Create bundles
flatpak build-bundle repo-cli SaturnLauncher.flatpak com.github.IlyaP358.SaturnLauncher
flatpak build-bundle repo-gui SaturnLauncher.GUI.flatpak com.github.IlyaP358.SaturnLauncher.GUI

echo "Flatpak packages built successfully!"
echo "Install with:"
echo "flatpak install SaturnLauncher.flatpak"
echo "flatpak install SaturnLauncher.GUI.flatpak"
echo ""
echo "Or run directly:"
echo "flatpak run com.github.IlyaP358.SaturnLauncher"
echo "flatpak run com.github.IlyaP358.SaturnLauncher.GUI"
