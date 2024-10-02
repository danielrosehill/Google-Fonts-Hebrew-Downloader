import sys
import os
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QFileDialog, 
                             QMessageBox)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSettings

class GoogleFontsDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Hebrew Google Fonts Downloader')
        self.setGeometry(100, 100, 400, 300)
        
        # Set window icon (Israel flag)
        self.setWindowIcon(QIcon('israel_flag.png'))
        
        layout = QVBoxLayout()
        
        # Notice
        notice = QLabel('<b>Note: You need a Google Fonts API key to use this utility.</b>')
        notice.setStyleSheet('color: #0038b8;')  # Israel blue
        layout.addWidget(notice)
        
        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel('Select folder:')
        self.folder_button = QPushButton('Browse')
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)
        
        # Download button
        self.download_button = QPushButton('Download Fonts')
        self.download_button.setStyleSheet('background-color: #0038b8; color: white;')
        self.download_button.clicked.connect(self.download_fonts)
        layout.addWidget(self.download_button)
        
        # Last run date
        self.last_run_label = QLabel('Last run: Never')
        layout.addWidget(self.last_run_label)
        
        self.setLayout(layout)
        
        # Load saved settings
        self.settings = QSettings('HebrewFontsDownloader', 'Settings')
        self.load_settings()
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_label.setText(f'Selected: {folder}')
            self.settings.setValue('folder', folder)
        
    def load_settings(self):
        api_key = self.settings.value('api_key', '')
        folder = self.settings.value('folder', '')
        last_run = self.settings.value('last_run', 'Never')
        
        self.api_key_input.setText(api_key)
        if folder:
            self.folder_label.setText(f'Selected: {folder}')
        self.last_run_label.setText(f'Last run: {last_run}')
        
    def save_settings(self):
        self.settings.setValue('api_key', self.api_key_input.text())
        self.settings.setValue('last_run', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
    def download_fonts(self):
        api_key = self.api_key_input.text()
        folder = self.settings.value('folder', '')
        
        if not api_key or not folder:
            QMessageBox.warning(self, 'Error', 'Please provide API key and select a folder.')
            return
        
        # Here you would implement the actual font downloading logic
        # For demonstration, we'll just simulate the process
        
        QMessageBox.information(self, 'Success', f'Fonts downloaded to {folder}')
        self.save_settings()
        self.load_settings()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoogleFontsDownloader()
    ex.show()
    sys.exit(app.exec())