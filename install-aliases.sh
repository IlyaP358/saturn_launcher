#!/bin/bash

# Script to install aliases/symlinks for Saturn Launcher
# This makes 'saturn' and 'saturn-gui' commands available in your terminal

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

echo "Installing aliases to $INSTALL_DIR..."

# Create wrapper for saturn CLI
cat > "$INSTALL_DIR/saturn" <<EOF
#!/bin/bash
flatpak run --command=saturn com.github.IlyaP358.SaturnLauncher "\$@"
EOF
chmod +x "$INSTALL_DIR/saturn"
echo "Created $INSTALL_DIR/saturn"

# Create wrapper for saturn-gui
cat > "$INSTALL_DIR/saturn-gui" <<EOF
#!/bin/bash
flatpak run com.github.IlyaP358.SaturnLauncher.GUI "\$@"
EOF
chmod +x "$INSTALL_DIR/saturn-gui"
echo "Created $INSTALL_DIR/saturn-gui"

echo "Done! Make sure $INSTALL_DIR is in your PATH."
echo "You may need to restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)"
