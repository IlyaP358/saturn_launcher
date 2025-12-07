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