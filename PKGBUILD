pkgbase=saturn-launcher
pkgname=('saturn-launcher' 'saturn-launcher-gui')
pkgver=1.0.0
pkgrel=1
pkgdesc="Saturn Launcher - Minecraft launcher with shader support"
arch=('x86_64' 'aarch64')
url="https://github.com/IlyaP358/saturn_launcher"
license=('custom')
depends=('python')
makedepends=('git' 'python-pip')
optdepends_saturn_launcher=('java-runtime: for running Minecraft')
optdepends_saturn_launcher_gui=('java-runtime: for running Minecraft')
source=("git+https://github.com/IlyaP358/saturn_launcher.git")
md5sums=('SKIP')

package_saturn-launcher() {
  pkgdesc="Saturn Launcher - CLI Minecraft launcher with shader support"
  depends=('python')
  
  cd "${srcdir}/saturn_launcher"
  
  # Создаем директорию для Python пакета
  install -d "${pkgdir}/opt/saturn-launcher"
  
  # Копируем всё содержимое репо
  cp -r . "${pkgdir}/opt/saturn-launcher/"
  
  # Удаляем ненужные файлы
  rm -rf "${pkgdir}/opt/saturn-launcher/.git" \
         "${pkgdir}/opt/saturn-launcher/.gitignore" \
         "${pkgdir}/opt/saturn-launcher/saturn-gui.py" \
         "${pkgdir}/opt/saturn-launcher/update_gui_classes.py" \
         "${pkgdir}/opt/saturn-launcher/shader_download_classes.py" \
         "${pkgdir}/opt/saturn-launcher/saturn_gui_windows.spec" \
         "${pkgdir}/opt/saturn-launcher/saturn_gui_linux.spec" \
         "${pkgdir}/opt/saturn-launcher/com.github.IlyaP358.SaturnLauncher.GUI*"
  
  # Устанавливаем Python зависимости в виртуальное окружение
  python -m venv "${pkgdir}/opt/saturn-launcher/venv"
  source "${pkgdir}/opt/saturn-launcher/venv/bin/activate"
  pip install --upgrade pip
  pip install -r "${pkgdir}/opt/saturn-launcher/requirements.txt"
  deactivate
  
  # Создаем wrapper script
  install -d "${pkgdir}/usr/bin"
  cat > "${pkgdir}/usr/bin/saturn" << 'EOF'
#!/bin/bash
source /opt/saturn-launcher/venv/bin/activate
/usr/bin/python3 /opt/saturn-launcher/saturn.py "$@"
EOF
  chmod +x "${pkgdir}/usr/bin/saturn"
  
  # Копируем лицензию
  install -d "${pkgdir}/usr/share/licenses/${pkgbase}"
  install -m 644 LICENSE "${pkgdir}/usr/share/licenses/${pkgbase}/"
}

package_saturn-launcher-gui() {
  pkgdesc="Saturn Launcher - GUI Minecraft launcher with shader support"
  depends=('python')
  
  cd "${srcdir}/saturn_launcher"
  
  # Создаем директорию для Python пакета
  install -d "${pkgdir}/opt/saturn-launcher-gui"
  
  # Копируем всё содержимое репо
  cp -r . "${pkgdir}/opt/saturn-launcher-gui/"
  
  # Удаляем ненужные файлы
  rm -rf "${pkgdir}/opt/saturn-launcher-gui/.git" \
         "${pkgdir}/opt/saturn-launcher-gui/.gitignore" \
         "${pkgdir}/opt/saturn-launcher-gui/saturn_windows.spec" \
         "${pkgdir}/opt/saturn-launcher-gui/saturn_linux.spec"
  
  # Устанавливаем Python зависимости в виртуальное окружение
  python -m venv "${pkgdir}/opt/saturn-launcher-gui/venv"
  source "${pkgdir}/opt/saturn-launcher-gui/venv/bin/activate"
  pip install --upgrade pip
  pip install -r "${pkgdir}/opt/saturn-launcher-gui/requirements.txt"
  # Добавляем PyQt5 если его нет в requirements.txt
  pip install PySide6
  deactivate
  
  # Создаем wrapper script
  install -d "${pkgdir}/usr/bin"
  cat > "${pkgdir}/usr/bin/saturn-gui" << 'EOF'
#!/bin/bash
source /opt/saturn-launcher-gui/venv/bin/activate
/usr/bin/python3 /opt/saturn-launcher-gui/saturn-gui.py "$@"
EOF
  chmod +x "${pkgdir}/usr/bin/saturn-gui"
  
  # Desktop файл
  install -d "${pkgdir}/usr/share/applications"
  [ -f "com.github.IlyaP358.SaturnLauncher.GUI.desktop" ] && \
    install -m 644 com.github.IlyaP358.SaturnLauncher.GUI.desktop \
      "${pkgdir}/usr/share/applications/saturn-launcher-gui.desktop"
  
  # Метаинформация
  install -d "${pkgdir}/usr/share/metainfo"
  [ -f "com.github.IlyaP358.SaturnLauncher.GUI.metainfo.xml" ] && \
    install -m 644 com.github.IlyaP358.SaturnLauncher.GUI.metainfo.xml \
      "${pkgdir}/usr/share/metainfo/saturn-launcher-gui.metainfo.xml"
  
  # Копируем лицензию
  install -d "${pkgdir}/usr/share/licenses/${pkgbase}"
  install -m 644 LICENSE "${pkgdir}/usr/share/licenses/${pkgbase}/"
}
