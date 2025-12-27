from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(720, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Create main vertical layout
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(10)

        # Logo label
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(800, 400))
        self.label.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.label)

        # Spacer
        self.mainLayout.addStretch()

        # Input widgets layout
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(10)

        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.inputLayout.addWidget(self.lineEdit)

        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.setObjectName(u"comboBox")
        self.inputLayout.addWidget(self.comboBox)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.inputLayout.addWidget(self.pushButton)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.inputLayout.addWidget(self.progressBar)

        self.mainLayout.addLayout(self.inputLayout)

        # Set background image
        self.centralwidget.setStyleSheet("#centralwidget { background-image: url(saturn-background.png); background-repeat: no-repeat; background-size: 100% 100%; }")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 720, 22))
        MainWindow.setMenuBar(self.menubar)

        # Settings button in top right
        self.settingsButton = QPushButton("⚙")
        self.settingsButton.setFixedSize(30, 30)
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


def open_settings(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Settings")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Settings Options:"))
    check1 = QCheckBox("Show FPS")
    layout.addWidget(check1)
    check2 = QCheckBox("Auto-start")
    layout.addWidget(check2)
    button = QPushButton("Close")
    button.clicked.connect(dialog.accept)
    layout.addWidget(button)
    dialog.setLayout(layout)
    dialog.exec()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Connect settings button
    ui.settingsButton.clicked.connect(lambda: open_settings(MainWindow))

    # Set window icon
    icon_pixmap = QPixmap("saturn_title.png")
    MainWindow.setWindowIcon(QIcon(icon_pixmap))

    # Set logo image in label
    ui.label.setPixmap(icon_pixmap.scaled(ui.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    ui.label.setAlignment(Qt.AlignCenter)

    MainWindow.show()
    sys.exit(app.exec())
