import sys
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QFileDialog,
                             QMessageBox, QFrame, QProgressBar, QTextEdit,
                             QTabWidget)
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSettings, QDir, QThread, pyqtSignal

class DownloadThread(QThread):
    progress_update = pyqtSignal(int, str)
    download_complete = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, folder):
        super().__init__()
        self.api_key = api_key
        self.folder = folder

    def run(self):
        try:
            url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={self.api_key}&subset=hebrew"
            response = requests.get(url)
            if response.status_code != 200:
                self.error_occurred.emit(f'Failed to fetch fonts: {response.text}')
                return

            fonts = response.json().get('items', [])
            hebrew_fonts = [font for font in fonts if 'hebrew' in font['subsets']]
            total_fonts = len(hebrew_fonts)
            new_fonts = 0

            for i, font in enumerate(hebrew_fonts):
                font_name = font['family']
                font_url = font['files'].get('regular', '')
                if not font_url:
                    self.progress_update.emit(i + 1, f"Skipping {font_name}: No regular style available")
                    continue

                font_path = os.path.join(self.folder, f"{font_name}.ttf")
                if os.path.exists(font_path):
                    self.progress_update.emit(i + 1, f"Skipping {font_name}: Already downloaded")
                    continue

                self.progress_update.emit(i + 1, f"Downloading {font_name}...")
                font_response = requests.get(font_url)
                if font_response.status_code == 200:
                    with open(font_path, 'wb') as f:
                        f.write(font_response.content)
                    new_fonts += 1
                    self.progress_update.emit(i + 1, f"Successfully downloaded {font_name}")
                else:
                    self.progress_update.emit(i + 1, f"Failed to download {font_name}")

            self.download_complete.emit(new_fonts)
        except Exception as e:
            self.error_occurred.emit(str(e))

class GoogleFontsDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Load custom fonts
        QFontDatabase.addApplicationFont("path/to/Outfit-Regular.ttf")
        QFontDatabase.addApplicationFont("path/to/RobotoCondensed-Regular.ttf")

        self.setWindowTitle('Hebrew Google Fonts Downloader')
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #ffffff; font-family: 'Roboto Condensed';")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add coverage image
        image_label = QLabel()
        pixmap = QPixmap(self.get_resource_path('Images/sloth.png'))
        scaled_pixmap = pixmap.scaledToWidth(760, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # Add title with Outfit font
        title_label = QLabel('Hebrew Google Fonts Downloader')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Outfit", 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0038b8; margin: 20px 0;")
        main_layout.addWidget(title_label)

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont("Roboto Condensed", 12))

        # Config tab
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        self.setup_config_tab(config_layout)
        tab_widget.addTab(config_tab, "Config")

        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        self.setup_about_tab(about_layout)
        tab_widget.addTab(about_tab, "About")

        main_layout.addWidget(tab_widget)

        # Add credits
        credits_label = QLabel('Built by Claude Sonnet 3.5 with prompting by Daniel Rosehill (danielrosehill.com)')
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setStyleSheet('font-size: 12px; color: #333; margin-top: 10px; font-weight: bold;')
        main_layout.addWidget(credits_label)

        self.setLayout(main_layout)

        # Load saved settings
        self.settings = QSettings('HebrewFontsDownloader', 'Settings')
        self.load_settings()

    def setup_config_tab(self, layout):
        layout.setSpacing(20)

        # Notice
        notice = QLabel('Note: You need a Google Fonts API key to use this utility.')
        notice.setStyleSheet('color: #0038b8; font-weight: bold; font-size: 14px;')
        layout.addWidget(notice)

        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('API Key:')
        api_key_label.setStyleSheet('font-size: 14px; min-width: 80px;')
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Google Fonts API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel('Select folder:')
        folder_label.setStyleSheet('font-size: 14px; min-width: 80px;')
        self.folder_button = QPushButton('Browse')
        self.folder_button.clicked.connect(self.select_folder)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_button)
        folder_layout.addStretch()
        layout.addLayout(folder_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Save Config button
        self.save_config_button = QPushButton('Save Config')
        self.save_config_button.clicked.connect(self.save_config)
        self.save_config_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #007B9A;
            }
        """)
        buttons_layout.addWidget(self.save_config_button)

        # Download button
        self.download_button = QPushButton('Download Fonts')
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #002c8f;
            }
        """)
        self.download_button.clicked.connect(self.download_fonts)
        buttons_layout.addWidget(self.download_button)

        layout.addLayout(buttons_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0038b8;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0038b8;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Terminal output pane
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.terminal_output.setMinimumHeight(100)
        layout.addWidget(self.terminal_output)

        # Last run date
        self.last_run_label = QLabel('Last run: Never')
        self.last_run_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_run_label.setStyleSheet('font-size: 12px; color: #666; margin-top: 10px;')
        layout.addWidget(self.last_run_label)

    def setup_about_tab(self, layout):
        description_text = (
            "This utility uses the Google Fonts API to search for fonts in the Google Fonts "
            "collection in Hebrew and saves them to a repository of your choosing. This utility "
            "is designed for graphic designers, web designers, or anyone looking to diversify "
            "the Hebrew fonts that they use for documents and graphics.\n\n"
            "If you like a font, please consider giving credit to its creator. The fonts can "
            "also be downloaded directly at fonts.google.com"
        )
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #333333; font-size: 14px; margin: 10px 0;")
        layout.addWidget(description_label)

    def get_resource_path(self, relative_path):
        base_path = QDir.currentPath()
        return os.path.join(base_path, relative_path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.settings.setValue('folder', folder)
            self.folder_button.setText('Selected: ' + os.path.basename(folder))

    def load_settings(self):
        api_key = self.settings.value('api_key', '')
        folder = self.settings.value('folder', '')
        last_run = self.settings.value('last_run', 'Never')

        self.api_key_input.setText(api_key)
        if folder:
            self.folder_button.setText('Selected: ' + os.path.basename(folder))
        self.last_run_label.setText(f'Last run: {last_run}')

    def save_config(self):
        self.settings.setValue('api_key', self.api_key_input.text())
        QMessageBox.information(self, 'Success', 'Configuration saved successfully.')

    def save_settings(self):
        self.settings.setValue('api_key', self.api_key_input.text())
        self.settings.setValue('last_run', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def download_fonts(self):
        api_key = self.api_key_input.text()
        folder = self.settings.value('folder', '')
        if not api_key or not folder:
            QMessageBox.warning(self, 'Error', 'Please provide API key and select a folder.')
            return

        self.terminal_output.clear()
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(False)

        self.download_thread = DownloadThread(api_key, folder)
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.download_complete.connect(self.download_finished)
        self.download_thread.error_occurred.connect(self.download_error)
        self.download_thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.terminal_output.append(message)

    def download_finished(self, new_fonts):
        self.save_settings()
        self.load_settings()
        self.download_button.setEnabled(True)
        QMessageBox.information(self, 'Success', f'Download complete!\n{new_fonts} new fonts were added to the repository.')

    def download_error(self, error_message):
        self.download_button.setEnabled(True)
        QMessageBox.warning(self, 'Error', error_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a more modern look
    ex = GoogleFontsDownloader()
    ex.show()
    sys.exit(app.exec())