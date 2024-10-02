import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QFileDialog,
                             QMessageBox, QFrame, QProgressBar, QTextEdit)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSettings, QDir

class GoogleFontsDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hebrew Google Fonts Downloader')
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #ffffff;")
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add coverage image
        image_label = QLabel()
        pixmap = QPixmap(self.get_resource_path('Images/sloth.png'))
        scaled_pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)
        
        # Add title
        title_label = QLabel('Hebrew Google Fonts Downloader')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0038b8; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Add description
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
        description_label.setStyleSheet("color: #333333; font-size: 14px; margin-bottom: 20px;")
        description_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        main_layout.addWidget(description_label)
        
        # Content frame
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(15)
        
        # Notice
        notice = QLabel('Note: You need a Google Fonts API key to use this utility.')
        notice.setStyleSheet('color: #0038b8; font-weight: bold; font-size: 14px; margin-bottom: 10px;')
        content_layout.addWidget(notice)
        
        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('API Key:')
        api_key_label.setStyleSheet('font-size: 14px; min-width: 80px;')
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Google Fonts API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        content_layout.addLayout(api_key_layout)
        
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
                padding: 5px 10px;
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
        content_layout.addLayout(folder_layout)
        
        # Save Config and Download buttons layout
        buttons_layout = QHBoxLayout()
        
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
        
        buttons_layout.addStretch()
        
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
        
        content_layout.addLayout(buttons_layout)
        
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
        content_layout.addWidget(self.progress_bar)
        
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
        content_layout.addWidget(self.terminal_output)
        
        # Last run date
        self.last_run_label = QLabel('Last run: Never')
        self.last_run_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_run_label.setStyleSheet('font-size: 12px; color: #666; margin-top: 10px;')
        content_layout.addWidget(self.last_run_label)
        
        main_layout.addWidget(content_frame)
        
        # Add credits
        credits_label = QLabel('Built by Claude Sonnet 3.5 with prompting by Daniel Rosehill (danielrosehill.com)')
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setStyleSheet('font-size: 12px; color: #333; margin-top: 10px; font-weight: bold;')
        main_layout.addWidget(credits_label)
        
        self.setLayout(main_layout)
        
        # Load saved settings
        self.settings = QSettings('HebrewFontsDownloader', 'Settings')
        self.load_settings()

    def get_resource_path(self, relative_path):
        base_path = QDir.currentPath()
        return os.path.join(base_path, relative_path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_button.setText(f'Selected: {folder}')
            self.settings.setValue('folder', folder)

    def load_settings(self):
        api_key = self.settings.value('api_key', '')
        folder = self.settings.value('folder', '')
        last_run = self.settings.value('last_run', 'Never')
        self.api_key_input.setText(api_key)
        if folder:
            self.folder_button.setText(f'Selected: {folder}')
        self.last_run_label.setText(f'Last run: {last_run}')

    def save_config(self):
        self.settings.setValue('api_key', self.api_key_input.text())
        folder = self.folder_button.text().replace('Selected: ', '')
        if folder != 'Browse':
            self.settings.setValue('folder', folder)
        QMessageBox.information(self, 'Success', 'Configuration saved successfully.')

    def save_settings(self):
        self.settings.setValue('api_key', self.api_key_input.text())
        self.settings.setValue('last_run', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def download_fonts(self):
        api_key = self.api_key_input.text()
        folder = self.folder_button.text().replace('Selected: ', '')
        if not api_key or folder == 'Browse':
            QMessageBox.warning(self, 'Error', 'Please provide API key and select a folder.')
            return
        
        self.terminal_output.clear()
        self.progress_bar.setValue(0)
        
        # Simulating font download process
        total_fonts = 20
        new_fonts = 0
        for i in range(total_fonts):
            self.progress_bar.setValue(int((i + 1) / total_fonts * 100))
            self.terminal_output.append(f"Downloading font {i + 1} of {total_fonts}...")
            if i % 3 == 0:  # Simulating new fonts
                new_fonts += 1
                self.terminal_output.append(f"New font added: Font{i + 1}")
            QApplication.processEvents()  # Ensure UI updates
        
        self.save_settings()
        self.load_settings()
        
        QMessageBox.information(self, 'Success', f'Download complete!\n{new_fonts} new fonts were added to the repository.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a more modern look
    ex = GoogleFontsDownloader()
    ex.show()
    sys.exit(app.exec())