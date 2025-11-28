"""
W-Rebuild Main Application Window
Entry point for the PySide6 desktop application
"""

import sys
import os

# Suppress Qt display warnings (harmless Qt/Windows monitor query errors)
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.screen=false'

from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QToolBar, QMessageBox, QTabWidget,
    QTextEdit, QSplitter, QGroupBox, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QScreen

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.detector import SystemDetector, DetectedTool
from src.core.backup import BackupManager
from src.core.restore import RestoreManager


class BackupWorker(QThread):
    """Worker thread for running backup without blocking UI"""
    
    finished = Signal(dict)  # Emits backup results
    error = Signal(str)  # Emits error message
    progress = Signal(str)  # Emits progress messages
    
    def __init__(self, backup_manager: BackupManager, selected_tools: list, selected_env_vars: list):
        super().__init__()
        self.backup_manager = backup_manager
        self.selected_tools = selected_tools
        self.selected_env_vars = selected_env_vars
    
    def run(self):
        """Run backup in background thread"""
        try:
            self.progress.emit("Initializing backup...")
            results = self.backup_manager.create_backup(
                self.selected_tools,
                self.selected_env_vars
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class DetectionWorker(QThread):
    """Worker thread for running detection without blocking UI"""
    
    finished = Signal(list)  # Emits list of DetectedTool objects
    error = Signal(str)  # Emits error message
    
    def __init__(self, detector: SystemDetector):
        super().__init__()
        self.detector = detector
    
    def run(self):
        """Run detection in background thread"""
        try:
            tools = self.detector.detect_all_tools(force_refresh=True)
            self.finished.emit(tools)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for W-Rebuild"""
    
    def __init__(self):
        super().__init__()
        self.detector = SystemDetector()
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager()
        self.detection_worker = None
        self.backup_worker = None
        self.detected_tools = []
        self.available_backups = []
        
        # Get screen size for responsive design
        self.setup_screen_dimensions()
        
        self.init_ui()
    
    def setup_screen_dimensions(self):
        """Calculate responsive dimensions based on screen size"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        
        # Determine device type and set responsive sizes with better scaling
        if self.screen_width >= 2560:  # 4K/Ultra-wide monitor
            self.window_width_percent = 0.65
            self.window_height_percent = 0.70
            self.font_size_title = 20
            self.font_size_normal = 13
            self.font_size_small = 12
            self.button_height = 44
            self.button_min_width = 200
            self.table_row_height = 38
            self.padding = 25
        elif self.screen_width >= 1920:  # Desktop/Large monitor (1080p)
            self.window_width_percent = 0.70
            self.window_height_percent = 0.75
            self.font_size_title = 18
            self.font_size_normal = 12
            self.font_size_small = 11
            self.button_height = 40
            self.button_min_width = 180
            self.table_row_height = 36
            self.padding = 20
        elif self.screen_width >= 1366:  # Laptop/Medium screen
            self.window_width_percent = 0.80
            self.window_height_percent = 0.80
            self.font_size_title = 14
            self.font_size_normal = 10
            self.font_size_small = 9
            self.button_height = 36
            self.button_min_width = 160
            self.table_row_height = 32
            self.padding = 15
        else:  # Small laptop/tablet
            self.window_width_percent = 0.90
            self.window_height_percent = 0.85
            self.font_size_title = 13
            self.font_size_normal = 9
            self.font_size_small = 8
            self.button_height = 32
            self.button_min_width = 140
            self.table_row_height = 30
            self.padding = 10
        
        # Calculate actual window size
        self.window_width = int(self.screen_width * self.window_width_percent)
        self.window_height = int(self.screen_height * self.window_height_percent)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("W-Rebuild - System Detection & Backup Tool")
        
        # Set responsive window size
        self.resize(self.window_width, self.window_height)
        self.setMinimumSize(800, 500)
        
        # Center window on screen
        self.center_window()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        main_layout.setSpacing(15)
        
        # Create toolbar
        self.create_toolbar()
        
        # Compact header with scan button and status
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        # Scan button (left side)
        self.scan_button = QPushButton("🔍 Scan System")
        self.scan_button.setMinimumHeight(self.button_height - 5)
        self.scan_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: {self.font_size_normal}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #005A9E;
            }}
            QPushButton:pressed {{
                background-color: #004578;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
        """)
        self.scan_button.clicked.connect(self.start_detection)
        header_layout.addWidget(self.scan_button)
        
        header_layout.addSpacing(15)
        
        # Compact info label
        self.info_label = QLabel("Ready to scan")
        self.info_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_small}px; padding: 5px;")
        header_layout.addWidget(self.info_label)
        
        header_layout.addStretch()
        
        # Progress bar (inline, hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #E0E0E0;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078D4;
            }
            QTabBar::tab:hover {
                background-color: #E8E8E8;
            }
        """)
        
        # Create tabs in order: User Profile, Detected Tools, Environment Variables, Restore
        self.create_environment_tab()
        self.create_tools_tab()
        self.create_env_variables_tab()
        self.create_restore_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Horizontal Backup Summary section
        backup_section = QGroupBox("Backup Summary")
        backup_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 2px solid #0078D4;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 12px;
                background-color: #F0F8FF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078D4;
            }
        """)
        backup_layout = QHBoxLayout(backup_section)
        backup_layout.setSpacing(15)
        backup_layout.setContentsMargins(15, 10, 15, 10)
        
        # Tools info (compact)
        self.tools_info_label = QLabel("🔧 <b>0</b> Tools")
        self.tools_info_label.setStyleSheet(f"font-size: {self.font_size_normal}px; color: #333333;")
        self.tools_info_label.setMinimumWidth(110)
        backup_layout.addWidget(self.tools_info_label)
        
        # Tools list (scrollable)
        self.tools_list_label = QLabel("None selected")
        self.tools_list_label.setStyleSheet(f"font-size: {self.font_size_small}px; color: #666666; padding: 2px 8px;")
        self.tools_list_label.setWordWrap(False)
        backup_layout.addWidget(self.tools_list_label, 1)
        
        # Separator
        separator1 = QLabel("|")
        separator1.setStyleSheet("color: #CCCCCC; font-size: 18px;")
        backup_layout.addWidget(separator1)
        
        # Environment variables info (compact)
        self.env_info_label = QLabel("🌍 <b>0</b> Variables")
        self.env_info_label.setStyleSheet(f"font-size: {self.font_size_normal}px; color: #333333;")
        self.env_info_label.setMinimumWidth(120)
        backup_layout.addWidget(self.env_info_label)
        
        # Environment variables list (scrollable)
        self.env_list_label = QLabel("None selected")
        self.env_list_label.setStyleSheet(f"font-size: {self.font_size_small}px; color: #666666; padding: 2px 8px;")
        self.env_list_label.setWordWrap(False)
        backup_layout.addWidget(self.env_list_label, 1)
        
        # Separator
        separator2 = QLabel("|")
        separator2.setStyleSheet("color: #CCCCCC; font-size: 18px;")
        backup_layout.addWidget(separator2)
        
        # Backup button (compact)
        self.unified_backup_btn = QPushButton("💾 Create Backup")
        self.unified_backup_btn.setMinimumHeight(self.button_height - 4)
        self.unified_backup_btn.setMinimumWidth(self.button_min_width)
        self.unified_backup_btn.clicked.connect(self.backup_selected_items)
        self.unified_backup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: {self.font_size_normal + 1}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #005A9E;
            }}
            QPushButton:pressed {{
                background-color: #004578;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
        """)
        backup_layout.addWidget(self.unified_backup_btn)
        
        main_layout.addWidget(backup_section)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply modern styling
        self.apply_styles()
        
        # Load environment variables on startup
        self.load_environment_variables()
    
    def create_tools_tab(self):
        """Create the tools detection tab"""
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        tools_layout.setContentsMargins(10, 10, 10, 10)
        
        # Results table
        self.create_results_table()
        self.results_table.itemChanged.connect(self.on_tool_checkbox_changed)
        tools_layout.addWidget(self.results_table)
        
        # Action buttons at bottom
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Select All button
        self.select_all_btn = QPushButton("✓ Select All")
        self.select_all_btn.setMinimumHeight(self.button_height - 8)
        self.select_all_btn.clicked.connect(self.select_all_tools)
        self.select_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #E8E8E8;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: {self.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: #D8D8D8;
            }}
        """)
        actions_layout.addWidget(self.select_all_btn)
        
        # Deselect All button
        self.deselect_all_btn = QPushButton("✗ Deselect All")
        self.deselect_all_btn.setMinimumHeight(self.button_height - 8)
        self.deselect_all_btn.clicked.connect(self.deselect_all_tools)
        self.deselect_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #E8E8E8;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: {self.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: #D8D8D8;
            }}
        """)
        actions_layout.addWidget(self.deselect_all_btn)
        
        actions_layout.addStretch()
        
        # Selected count label
        self.selected_count_label = QLabel("Selected: 0")
        self.selected_count_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_normal}px; padding: 5px;")
        actions_layout.addWidget(self.selected_count_label)
        
        tools_layout.addLayout(actions_layout)
        
        self.tab_widget.addTab(tools_widget, "🔧 Detected Tools")
    
    def create_environment_tab(self):
        """Create the user profile tab"""
        profile_widget = QWidget()
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(15, 15, 15, 15)
        profile_layout.setSpacing(15)
        
        # Header
        profile_header = QLabel("👤 User Profile Information")
        profile_header.setFont(QFont("Segoe UI", self.font_size_title, QFont.Weight.Bold))
        profile_header.setStyleSheet("color: #0078D4; padding: 5px;")
        profile_layout.addWidget(profile_header)
        
        # Description
        desc_label = QLabel("System and user account information")
        desc_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_small}px; padding-left: 5px;")
        profile_layout.addWidget(desc_label)
        
        # Profile table
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(2)
        self.profile_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.profile_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.profile_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Responsive column width
        prop_width = 220 if self.screen_width >= 1920 else 200 if self.screen_width >= 1366 else 180
        self.profile_table.setColumnWidth(0, prop_width)
        self.profile_table.verticalHeader().setDefaultSectionSize(self.table_row_height)
        
        self.profile_table.setAlternatingRowColors(True)
        self.profile_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.profile_table.verticalHeader().setVisible(False)
        self.profile_table.setStyleSheet(f"""
            QTableWidget {{
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #F0F0F0;
                font-size: {self.font_size_small}px;
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: #E3F2FD;
                color: #000000;
            }}
            QHeaderView::section {{
                background-color: #F8F9FA;
                padding: 10px;
                border: none;
                border-bottom: 3px solid #0078D4;
                font-weight: bold;
                font-size: {self.font_size_normal}px;
            }}
        """)
        profile_layout.addWidget(self.profile_table)
        
        self.tab_widget.addTab(profile_widget, "👤 User Profile")
    
    def create_env_variables_tab(self):
        """Create the environment variables tab"""
        env_widget = QWidget()
        env_layout = QVBoxLayout(env_widget)
        env_layout.setContentsMargins(15, 15, 15, 15)
        env_layout.setSpacing(15)
        
        # Header with search
        env_header = QHBoxLayout()
        env_title = QLabel("🌍 Environment Variables")
        env_title.setFont(QFont("Segoe UI", self.font_size_title, QFont.Weight.Bold))
        env_title.setStyleSheet("color: #0078D4; padding: 5px;")
        env_header.addWidget(env_title)
        
        env_header.addStretch()
        
        # Search box
        self.env_search = QLineEdit()
        self.env_search.setPlaceholderText("🔍 Search variables...")
        search_width = 350 if self.screen_width >= 1920 else 300 if self.screen_width >= 1366 else 250
        self.env_search.setMinimumWidth(search_width)
        self.env_search.textChanged.connect(self.filter_environment_variables)
        self.env_search.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: {self.font_size_normal}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: #0078D4;
            }}
        """)
        env_header.addWidget(self.env_search)
        
        env_layout.addLayout(env_header)
        
        # Description
        desc_label = QLabel("System and user environment variables (PATH, JAVA_HOME, etc.)")
        desc_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_small}px; padding-left: 5px;")
        env_layout.addWidget(desc_label)
        
        # Environment table
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(3)
        self.env_table.setHorizontalHeaderLabels(["Select", "Variable Name", "Value"])
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.env_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.env_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Responsive column widths
        var_name_width = 300 if self.screen_width >= 1920 else 280 if self.screen_width >= 1366 else 250
        self.env_table.setColumnWidth(0, 60)
        self.env_table.setColumnWidth(1, var_name_width)
        self.env_table.verticalHeader().setDefaultSectionSize(self.table_row_height)
        
        self.env_table.setAlternatingRowColors(True)
        self.env_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.env_table.verticalHeader().setVisible(False)
        self.env_table.setSortingEnabled(True)
        self.env_table.setStyleSheet(f"""
            QTableWidget {{
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #F0F0F0;
                font-size: {self.font_size_small}px;
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: #E3F2FD;
                color: #000000;
            }}
            QHeaderView::section {{
                background-color: #F8F9FA;
                padding: 10px;
                border: none;
                border-bottom: 3px solid #0078D4;
                font-weight: bold;
                font-size: {self.font_size_normal}px;
            }}
        """)
        self.env_table.itemChanged.connect(self.on_env_checkbox_changed)
        env_layout.addWidget(self.env_table)
        
        # Action buttons at bottom
        env_actions_layout = QHBoxLayout()
        env_actions_layout.setSpacing(10)
        
        # Select All button
        self.select_all_env_btn = QPushButton("✓ Select All")
        self.select_all_env_btn.setMinimumHeight(self.button_height - 8)
        self.select_all_env_btn.clicked.connect(self.select_all_env_vars)
        self.select_all_env_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #E8E8E8;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: {self.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: #D8D8D8;
            }}
        """)
        env_actions_layout.addWidget(self.select_all_env_btn)
        
        # Deselect All button
        self.deselect_all_env_btn = QPushButton("✗ Deselect All")
        self.deselect_all_env_btn.setMinimumHeight(self.button_height - 8)
        self.deselect_all_env_btn.clicked.connect(self.deselect_all_env_vars)
        self.deselect_all_env_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #E8E8E8;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: {self.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: #D8D8D8;
            }}
        """)
        env_actions_layout.addWidget(self.deselect_all_env_btn)
        
        env_actions_layout.addStretch()
        
        # Variable count label
        self.env_count_label = QLabel("Total variables: 0")
        self.env_count_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_normal}px; padding: 5px;")
        env_actions_layout.addWidget(self.env_count_label)
        
        # Selected count label
        self.selected_env_count_label = QLabel("Selected: 0")
        self.selected_env_count_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_normal}px; padding: 5px;")
        env_actions_layout.addWidget(self.selected_env_count_label)
        
        env_layout.addLayout(env_actions_layout)
        
        self.tab_widget.addTab(env_widget, "🌍 Environment Variables")
    
    def create_restore_tab(self):
        """Create the restore tab for restoring from backups"""
        restore_widget = QWidget()
        restore_layout = QVBoxLayout(restore_widget)
        restore_layout.setContentsMargins(15, 15, 15, 15)
        restore_layout.setSpacing(15)
        
        # Header with actions
        restore_header = QHBoxLayout()
        restore_title = QLabel("💾 Restore from Backup")
        restore_title.setFont(QFont("Segoe UI", self.font_size_title, QFont.Weight.Bold))
        restore_title.setStyleSheet("color: #0078D4; padding: 5px;")
        restore_header.addWidget(restore_title)
        
        restore_header.addStretch()
        
        # Scan for backups button
        self.scan_backups_btn = QPushButton("🔍 Scan for Backups")
        self.scan_backups_btn.setMinimumHeight(self.button_height - 5)
        self.scan_backups_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: {self.font_size_normal}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #005A9E;
            }}
            QPushButton:pressed {{
                background-color: #004578;
            }}
        """)
        self.scan_backups_btn.clicked.connect(self.scan_for_backups)
        restore_header.addWidget(self.scan_backups_btn)
        
        restore_layout.addLayout(restore_header)
        
        # Description
        desc_label = QLabel("Select a backup to restore your tools and environment variables")
        desc_label.setStyleSheet(f"color: #666666; font-size: {self.font_size_small}px; padding-left: 5px;")
        restore_layout.addWidget(desc_label)
        
        # Backup selection section
        backup_selection = QGroupBox("Available Backups")
        backup_selection.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 2px solid #0078D4;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078D4;
            }
        """)
        backup_selection_layout = QVBoxLayout(backup_selection)
        
        # Backups table
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(5)
        self.backups_table.setHorizontalHeaderLabels(["Select", "Backup Name", "Date/Time", "Tools", "Env Vars"])
        self.backups_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.backups_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.backups_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.backups_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.backups_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.backups_table.setColumnWidth(0, 60)
        self.backups_table.setColumnWidth(2, 180 if self.screen_width >= 1920 else 160)
        self.backups_table.setColumnWidth(3, 80)
        self.backups_table.setColumnWidth(4, 80)
        self.backups_table.verticalHeader().setDefaultSectionSize(self.table_row_height)
        self.backups_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backups_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.backups_table.setAlternatingRowColors(True)
        self.backups_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.backups_table.verticalHeader().setVisible(False)
        self.backups_table.setStyleSheet(f"""
            QTableWidget {{
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #F0F0F0;
                font-size: {self.font_size_small}px;
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: #E3F2FD;
                color: #000000;
            }}
            QHeaderView::section {{
                background-color: #F8F9FA;
                padding: 10px;
                border: none;
                border-bottom: 3px solid #0078D4;
                font-weight: bold;
                font-size: {self.font_size_normal}px;
            }}
        """)
        self.backups_table.itemSelectionChanged.connect(self.on_backup_selected)
        backup_selection_layout.addWidget(self.backups_table)
        
        restore_layout.addWidget(backup_selection)
        
        # Backup details section
        details_section = QGroupBox("Backup Contents")
        details_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 2px solid #28A745;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28A745;
            }
        """)
        details_layout = QVBoxLayout(details_section)
        
        # Backup details text display
        self.backup_details_text = QTextEdit()
        self.backup_details_text.setReadOnly(True)
        
        # Use size policy to allow dynamic resizing instead of fixed height
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.backup_details_text.setSizePolicy(size_policy)
        
        self.backup_details_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {self.font_size_normal}px;
                padding: 15px;
                line-height: 1.6;
            }}
        """)
        self.backup_details_text.setHtml(
            f"<div style='color: #666666; padding: 20px; text-align: center;'>"
            f"<p style='font-size: {self.font_size_title}px;'><b>📦 No backup selected</b></p>"
            f"<p style='font-size: {self.font_size_normal}px;'>Click 'Scan for Backups' to view available backups</p>"
            "</div>"
        )
        details_layout.addWidget(self.backup_details_text)
        
        restore_layout.addWidget(details_section)
        
        # Restore button
        restore_actions = QHBoxLayout()
        restore_actions.addStretch()
        
        self.restore_btn = QPushButton("♻️ Restore Selected Backup")
        self.restore_btn.setMinimumHeight(self.button_height)
        self.restore_btn.setMinimumWidth(self.button_min_width + 70)
        self.restore_btn.setEnabled(False)
        self.restore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: {self.font_size_title - 2}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:pressed {{
                background-color: #1E7E34;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
        """)
        self.restore_btn.clicked.connect(self.restore_selected_backup)
        restore_actions.addWidget(self.restore_btn)
        
        restore_actions.addStretch()
        restore_layout.addLayout(restore_actions)
        
        self.tab_widget.addTab(restore_widget, "♻️ Restore")
    
    def style_table(self, table):
        """Apply consistent styling to tables with responsive font sizes"""
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background-color: white;
                gridline-color: #F0F0F0;
                font-size: {self.font_size_small}px;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: #E3F2FD;
                color: #000000;
            }}
            QHeaderView::section {{
                background-color: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #0078D4;
                font-weight: bold;
                font-size: {self.font_size_normal}px;
            }}
        """)
    
    def load_environment_variables(self):
        """Load and display environment variables and user profile"""
        # Load user profile information
        profile_data = [
            ("Username", os.environ.get("USERNAME", "N/A")),
            ("Computer Name", os.environ.get("COMPUTERNAME", "N/A")),
            ("User Domain", os.environ.get("USERDOMAIN", "N/A")),
            ("User Profile", os.environ.get("USERPROFILE", "N/A")),
            ("Home Drive", os.environ.get("HOMEDRIVE", "N/A")),
            ("Home Path", os.environ.get("HOMEPATH", "N/A")),
            ("Temp Folder", os.environ.get("TEMP", "N/A")),
            ("OS", os.environ.get("OS", "N/A")),
            ("Processor", os.environ.get("PROCESSOR_IDENTIFIER", "N/A")),
        ]
        
        self.profile_table.setRowCount(len(profile_data))
        for row, (key, value) in enumerate(profile_data):
            key_item = QTableWidgetItem(key)
            key_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.profile_table.setItem(row, 0, key_item)
            
            value_item = QTableWidgetItem(value)
            self.profile_table.setItem(row, 1, value_item)
        
        # Load all environment variables
        self.all_env_vars = sorted(os.environ.items(), key=lambda x: x[0].upper())
        self.display_environment_variables(self.all_env_vars)
    
    def display_environment_variables(self, env_vars):
        """Display environment variables in the table"""
        self.env_table.setSortingEnabled(False)  # Disable sorting while populating
        self.env_table.setRowCount(len(env_vars))
        
        for row, (key, value) in enumerate(env_vars):
            # Checkbox for selection
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.env_table.setItem(row, 0, checkbox_item)
            
            # Variable name
            key_item = QTableWidgetItem(key)
            key_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            key_item.setForeground(Qt.GlobalColor.darkBlue)
            self.env_table.setItem(row, 1, key_item)
            
            # Variable value
            value_item = QTableWidgetItem(value)
            value_item.setToolTip(value)  # Show full value on hover
            self.env_table.setItem(row, 2, value_item)
        
        self.env_table.setSortingEnabled(True)  # Re-enable sorting
        # Update count label
        self.env_count_label.setText(f"Total variables: {len(env_vars)}")
    
    def filter_environment_variables(self, text):
        """Filter environment variables based on search text"""
        if not text:
            self.display_environment_variables(self.all_env_vars)
            return
        
        text_lower = text.lower()
        filtered = [(k, v) for k, v in self.all_env_vars 
                   if text_lower in k.lower() or text_lower in v.lower()]
        self.display_environment_variables(filtered)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Refresh action
        refresh_action = QAction("⟳ Refresh", self)
        refresh_action.triggered.connect(self.start_detection)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # About action
        about_action = QAction("ℹ About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def create_results_table(self):
        """Create the results table widget"""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Select", "Tool Name", "Version", "Type", "Installation Path"])
        
        # Set column widths with responsive sizing
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Responsive column widths based on screen size
        select_width = 60 if self.screen_width >= 1920 else 55
        name_width = 220 if self.screen_width >= 1920 else 180
        version_width = 120 if self.screen_width >= 1920 else 100
        type_width = 100 if self.screen_width >= 1920 else 90
        
        self.results_table.setColumnWidth(0, select_width)  # Select checkbox
        self.results_table.setColumnWidth(1, name_width)  # Tool Name
        self.results_table.setColumnWidth(2, version_width)  # Version
        self.results_table.setColumnWidth(3, type_width)  # Type
        
        # Set row height
        self.results_table.verticalHeader().setDefaultSectionSize(self.table_row_height)
        
        # Style the table
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSortingEnabled(True)  # Enable column sorting
        
        self.style_table(self.results_table)
    
    def apply_styles(self):
        """Apply modern styling to the window"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QLabel {
                color: #333333;
            }
            QToolBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #DDDDDD;
                padding: 5px;
                spacing: 10px;
            }
            QStatusBar {
                background-color: #F5F5F5;
                border-top: 1px solid #DDDDDD;
            }
        """)
    
    def start_detection(self):
        """Start the detection process"""
        if self.detection_worker and self.detection_worker.isRunning():
            return  # Already running
        
        # Switch to Detected Tools tab (2nd tab, index 1)
        self.tab_widget.setCurrentIndex(1)
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.detected_tools.clear()
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Scanning system for installed tools...")
        self.info_label.setText("⏳ Scanning system...")
        
        # Start detection in background thread
        self.detection_worker = DetectionWorker(self.detector)
        self.detection_worker.finished.connect(self.on_detection_complete)
        self.detection_worker.error.connect(self.on_detection_error)
        self.detection_worker.start()
    
    def on_detection_complete(self, tools: list):
        """Handle detection completion"""
        self.detected_tools = tools
        self.populate_results_table(tools)
        
        # Update UI
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Detection complete - Found {len(tools)} tool(s)")
        
        if len(tools) > 0:
            self.info_label.setText(f"✓ Found {len(tools)} tool(s)")
        else:
            self.info_label.setText("⚠ No tools detected")
        
        # Initialize backup summary
        self.update_backup_summary()
    
    def on_detection_error(self, error_msg: str):
        """Handle detection error"""
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Detection failed")
        self.info_label.setText(f"❌ Scan failed: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Detection Error",
            f"Failed to detect installed tools:\n{error_msg}"
        )
    
    def populate_results_table(self, tools: list):
        """Populate the results table with detected tools"""
        self.results_table.setSortingEnabled(False)  # Disable sorting while populating
        self.results_table.setRowCount(len(tools))
        
        for row, tool in enumerate(tools):
            # Checkbox for selection
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 0, checkbox_item)
            
            # Tool name
            name_item = QTableWidgetItem(tool.name)
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.results_table.setItem(row, 1, name_item)
            
            # Version
            version_item = QTableWidgetItem(tool.version)
            self.results_table.setItem(row, 2, version_item)
            
            # Type
            type_item = QTableWidgetItem(tool.tool_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 3, type_item)
            
            # Path
            path_item = QTableWidgetItem(tool.path)
            path_item.setForeground(Qt.GlobalColor.darkGray)
            self.results_table.setItem(row, 4, path_item)
        
        self.results_table.setSortingEnabled(True)  # Re-enable sorting
    
    def select_all_tools(self):
        """Select all tools in the table"""
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
        self.update_selected_count()
    
    def deselect_all_tools(self):
        """Deselect all tools in the table"""
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Update the selected count label for tools"""
        count = 0
        selected_names = []
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                count += 1
                tool_name = self.results_table.item(row, 1).text()
                selected_names.append(tool_name)
        
        self.selected_count_label.setText(f"Selected: {count}")
        self.update_backup_summary()
    
    def on_tool_checkbox_changed(self, item):
        """Handle tool checkbox state change"""
        if item and item.column() == 0:  # Only for checkbox column
            self.update_selected_count()
    
    def select_all_env_vars(self):
        """Select all environment variables in the table"""
        for row in range(self.env_table.rowCount()):
            item = self.env_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
        self.update_selected_env_count()
    
    def deselect_all_env_vars(self):
        """Deselect all environment variables in the table"""
        for row in range(self.env_table.rowCount()):
            item = self.env_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
        self.update_selected_env_count()
    
    def update_selected_env_count(self):
        """Update the selected count label for environment variables"""
        count = 0
        for row in range(self.env_table.rowCount()):
            item = self.env_table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                count += 1
        self.selected_env_count_label.setText(f"Selected: {count}")
        self.update_backup_summary()
    
    def on_env_checkbox_changed(self, item):
        """Handle environment variable checkbox state change"""
        if item and item.column() == 0:  # Only for checkbox column
            self.update_selected_env_count()
    
    def update_backup_summary(self):
        """Update the unified backup summary section"""
        # Get selected tools
        selected_tools = []
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                tool_name = self.results_table.item(row, 1).text()
                tool_version = self.results_table.item(row, 2).text()
                selected_tools.append(f"{tool_name}")
        
        # Get selected environment variables
        selected_vars = []
        for row in range(self.env_table.rowCount()):
            checkbox = self.env_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                var_name = self.env_table.item(row, 1).text()
                selected_vars.append(var_name)
        
        # Update tools info (compact)
        tools_count = len(selected_tools)
        self.tools_info_label.setText(f"🔧 <b>{tools_count}</b> Tools")
        if tools_count > 0:
            tools_display = ", ".join(selected_tools[:3])
            if tools_count > 3:
                tools_display += f" +{tools_count - 3} more"
            self.tools_list_label.setText(tools_display)
            self.tools_list_label.setStyleSheet("font-size: 10px; color: #0078D4; font-weight: bold;")
        else:
            self.tools_list_label.setText("None selected")
            self.tools_list_label.setStyleSheet("font-size: 10px; color: #666666;")
        
        # Update environment variables info (compact)
        env_count = len(selected_vars)
        self.env_info_label.setText(f"🌍 <b>{env_count}</b> Variables")
        if env_count > 0:
            env_display = ", ".join(selected_vars[:4])
            if env_count > 4:
                env_display += f" +{env_count - 4} more"
            self.env_list_label.setText(env_display)
            self.env_list_label.setStyleSheet("font-size: 10px; color: #0078D4; font-weight: bold;")
        else:
            self.env_list_label.setText("None selected")
            self.env_list_label.setStyleSheet("font-size: 10px; color: #666666;")
        
        # Enable/disable backup button
        total_selected = tools_count + env_count
        self.unified_backup_btn.setEnabled(total_selected > 0)
    
    def backup_selected_items(self):
        """Backup selected tools and environment variables together"""
        if self.backup_worker and self.backup_worker.isRunning():
            return  # Backup already in progress
        
        # Get selected tools
        selected_tools = []
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                tool_name = self.results_table.item(row, 1).text()
                tool_version = self.results_table.item(row, 2).text()
                tool_path = self.results_table.item(row, 4).text()
                selected_tools.append({
                    'name': tool_name,
                    'version': tool_version,
                    'path': tool_path
                })
        
        # Get selected environment variables
        selected_vars = []
        for row in range(self.env_table.rowCount()):
            checkbox = self.env_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                var_name = self.env_table.item(row, 1).text()
                var_value = self.env_table.item(row, 2).text()
                selected_vars.append({
                    'name': var_name,
                    'value': var_value
                })
        
        if not selected_tools and not selected_vars:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one tool or environment variable to backup."
            )
            return
        
        # Confirm backup
        confirm_msg = f"Do you want to backup {len(selected_tools)} tool(s) and {len(selected_vars)} environment variable(s)?\n\n"
        confirm_msg += f"Backup location:\n{self.backup_manager.backup_root}"
        
        reply = QMessageBox.question(
            self,
            "Confirm Backup",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable all controls during backup
        self.set_controls_enabled(False)
        self.unified_backup_btn.setEnabled(True)  # Keep backup button enabled for cancel
        self.unified_backup_btn.setText("⏹ Cancel Backup")
        self.unified_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        self.unified_backup_btn.clicked.disconnect()
        self.unified_backup_btn.clicked.connect(self.cancel_backup)
        
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Creating backup...")
        self.setWindowTitle("W-Rebuild - Backup in Progress...")
        
        # Start backup in background thread
        self.backup_worker = BackupWorker(self.backup_manager, selected_tools, selected_vars)
        self.backup_worker.finished.connect(self.on_backup_complete)
        self.backup_worker.error.connect(self.on_backup_error)
        self.backup_worker.progress.connect(self.on_backup_progress)
        self.backup_worker.start()
    
    def on_backup_progress(self, message: str):
        """Handle backup progress updates"""
        self.status_bar.showMessage(message)
    
    def on_backup_complete(self, results: dict):
        """Handle backup completion"""
        self.restore_backup_button()
        self.set_controls_enabled(True)
        self.progress_bar.setVisible(False)
        self.setWindowTitle("W-Rebuild - System Detection & Backup Tool")
        
        if results.get('success'):
            summary = self.backup_manager.get_backup_summary(results)
            
            # Show success dialog with details
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Backup Complete")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText(f"<h3>✓ Backup Created Successfully!</h3>")
            msg_box.setInformativeText(
                f"<p><b>Timestamp:</b> {results['timestamp']}</p>"
                f"<p><b>Location:</b><br><code>{results['backup_dir']}</code></p>"
            )
            msg_box.setDetailedText(summary)
            msg_box.exec()
            
            self.status_bar.showMessage("Backup completed successfully", 5000)
            
            # Ask if user wants to open backup folder
            reply = QMessageBox.question(
                self,
                "Open Backup Folder",
                "Do you want to open the backup folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import subprocess
                subprocess.Popen(f'explorer "{results["backup_dir"]}"')
        else:
            self.status_bar.showMessage("Backup failed", 5000)
    
    def on_backup_error(self, error_msg: str):
        """Handle backup error"""
        self.restore_backup_button()
        self.set_controls_enabled(True)
        self.progress_bar.setVisible(False)
        self.setWindowTitle("W-Rebuild - System Detection & Backup Tool")
        self.status_bar.showMessage("Backup failed")
        
        QMessageBox.critical(
            self,
            "Backup Error",
            f"Failed to create backup:\n\n{error_msg}"
        )
    
    def set_controls_enabled(self, enabled: bool):
        """Enable or disable all interactive controls"""
        self.scan_button.setEnabled(enabled)
        self.results_table.setEnabled(enabled)
        self.env_table.setEnabled(enabled)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        self.select_all_env_btn.setEnabled(enabled)
        self.deselect_all_env_btn.setEnabled(enabled)
        self.tab_widget.setEnabled(enabled)
    
    def restore_backup_button(self):
        """Restore backup button to its original state"""
        self.unified_backup_btn.clicked.disconnect()
        self.unified_backup_btn.clicked.connect(self.backup_selected_items)
        self.unified_backup_btn.setText("💾 Create Backup")
        self.unified_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        # Update enabled state based on selection
        self.update_backup_summary()
    
    def cancel_backup(self):
        """Cancel the ongoing backup operation"""
        if self.backup_worker and self.backup_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Cancel Backup",
                "Are you sure you want to cancel the backup?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.backup_worker.terminate()
                self.backup_worker.wait()
                self.restore_backup_button()
                self.set_controls_enabled(True)
                self.progress_bar.setVisible(False)
                self.setWindowTitle("W-Rebuild - System Detection & Backup Tool")
                self.status_bar.showMessage("Backup cancelled", 3000)
    
    def scan_for_backups(self):
        """Scan for available backups in the backup folder"""
        self.status_bar.showMessage("Scanning for backups...")
        
        try:
            # Get list of available backups
            self.available_backups = self.restore_manager.list_available_backups()
            
            # Clear existing table
            self.backups_table.setRowCount(0)
            
            if not self.available_backups:
                self.backup_details_text.setPlainText("No backups found in:\n" + str(self.restore_manager.backup_root))
                self.status_bar.showMessage("No backups found", 3000)
                return
            
            # Populate table with backups
            self.backups_table.setRowCount(len(self.available_backups))
            
            for row, backup in enumerate(self.available_backups):
                # Radio button for selection
                radio_item = QTableWidgetItem()
                radio_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                radio_item.setCheckState(Qt.CheckState.Checked if row == 0 else Qt.CheckState.Unchecked)
                self.backups_table.setItem(row, 0, radio_item)
                
                # Backup name
                name_item = QTableWidgetItem(backup['backup_name'])
                self.backups_table.setItem(row, 1, name_item)
                
                # Date/time
                datetime_str = backup.get('datetime', backup['timestamp'])
                if datetime_str:
                    try:
                        # Format datetime nicely
                        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                        formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_dt = datetime_str
                else:
                    formatted_dt = backup['timestamp']
                
                datetime_item = QTableWidgetItem(formatted_dt)
                self.backups_table.setItem(row, 2, datetime_item)
                
                # Tools count
                tools_item = QTableWidgetItem(str(backup['tools_count']))
                tools_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.backups_table.setItem(row, 3, tools_item)
                
                # Env vars count
                env_item = QTableWidgetItem(str(backup['env_vars_count']))
                env_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.backups_table.setItem(row, 4, env_item)
            
            # Select the first (most recent) backup by default
            if self.available_backups:
                self.backups_table.selectRow(0)
                self.show_backup_details(self.available_backups[0])
            
            self.status_bar.showMessage(f"Found {len(self.available_backups)} backup(s)", 3000)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Scan Error",
                f"Failed to scan for backups:\n\n{str(e)}"
            )
            self.status_bar.showMessage("Scan failed", 3000)
    
    def on_backup_selected(self):
        """Handle backup selection change"""
        selected_rows = self.backups_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            
            # Update radio buttons
            for r in range(self.backups_table.rowCount()):
                item = self.backups_table.item(r, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Checked if r == row else Qt.CheckState.Unchecked)
            
            if 0 <= row < len(self.available_backups):
                backup = self.available_backups[row]
                self.show_backup_details(backup)
                self.restore_btn.setEnabled(True)
        else:
            self.restore_btn.setEnabled(False)
    
    def show_backup_details(self, backup):
        """Display detailed information about a selected backup in HTML format"""
        try:
            backup_path = backup['backup_path']
            details = self.restore_manager.load_backup_details(backup_path)
            
            # Enhanced responsive sizing variables with better scaling
            if self.screen_width >= 2560:  # 4K monitors
                icon_size = "22px"
                padding_lg = "20px"
                padding_md = "16px"
                padding_sm = "12px"
                margin_section = "25px"
            elif self.screen_width >= 1920:  # 1080p monitors
                icon_size = "20px"
                padding_lg = "18px"
                padding_md = "14px"
                padding_sm = "10px"
                margin_section = "22px"
            elif self.screen_width >= 1366:  # Laptop screens
                icon_size = "16px"
                padding_lg = "12px"
                padding_md = "10px"
                padding_sm = "8px"
                margin_section = "15px"
            else:  # Small screens
                icon_size = "14px"
                padding_lg = "10px"
                padding_md = "8px"
                padding_sm = "6px"
                margin_section = "12px"
            
            h3_size = f"{self.font_size_title + 2}px"
            h4_size = f"{self.font_size_title - 1}px"
            text_size = f"{self.font_size_normal}px"
            small_size = f"{self.font_size_small}px"
            
            if not details:
                self.backup_details_text.setHtml(
                    f"<div style='color: red; padding: {padding_lg};'>"
                    f"<p style='font-size: {text_size};'><b>⚠️ Error loading backup details</b></p>"
                    f"<p style='font-size: {small_size};'>Manifest file may be corrupted or missing.</p>"
                    "</div>"
                )
                return
            
            # Build HTML content with responsive sizing
            html = f"<div style='font-family: Segoe UI, Arial; padding: {padding_sm};'>"
            
            # Header section
            html += f"<div style='background-color: #E3F2FD; padding: {padding_md}; border-radius: 6px; margin-bottom: {margin_section};'>"
            html += f"<h3 style='margin: 0; color: #0078D4; font-size: {h3_size};'>"
            html += f"<span style='font-size: {icon_size};'>📦</span> {details['backup_name']}</h3>"
            html += f"<p style='margin: 5px 0 0 0; color: #666; font-size: {small_size};'>"
            html += f"<span style='font-size: {icon_size};'>🕐</span> Created: {details['datetime'][:19] if details['datetime'] else details['timestamp']}</p>"
            html += f"</div>"
            
            # Tools section
            html += f"<div style='margin-bottom: {margin_section};'>"
            html += f"<h4 style='color: #0078D4; margin: 0 0 10px 0; border-bottom: 2px solid #0078D4; padding-bottom: 5px; font-size: {h4_size};'>"
            html += f"<span style='font-size: {icon_size};'>🔧</span> Tools ({details['tools_count']})</h4>"
            
            if details['tools']:
                html += "<table style='width: 100%; border-collapse: collapse;'>"
                for tool in details['tools']:
                    html += "<tr style='border-bottom: 1px solid #E0E0E0;'>"
                    html += f"<td style='padding: {padding_sm} 5px;'>"
                    html += f"<div style='font-weight: bold; color: #333; font-size: {text_size};'>{tool['name']}</div>"
                    html += f"<div style='font-size: {small_size}; color: #666;'>Version: {tool['version']}</div>"
                    html += f"<div style='font-size: {small_size}; color: #28A745;'>✓ {tool['backed_up_count']} item(s) backed up</div>"
                    html += "</td>"
                    html += "</tr>"
                html += "</table>"
            else:
                html += f"<p style='color: #999; font-style: italic; font-size: {text_size};'>No tools backed up</p>"
            
            html += "</div>"
            
            # Environment Variables section
            html += "<div>"
            html += f"<h4 style='color: #0078D4; margin: 0 0 10px 0; border-bottom: 2px solid #0078D4; padding-bottom: 5px; font-size: {h4_size};'>"
            html += f"<span style='font-size: {icon_size};'>🌍</span> Environment Variables ({details['env_vars_count']})</h4>"
            
            if details['environment_variables']:
                html += f"<div style='background-color: #F5F5F5; padding: {padding_sm}; border-radius: 4px;'>"
                # Show first 10 variables
                for i, env_var in enumerate(details['environment_variables'][:10]):
                    html += f"<div style='padding: 3px 0; font-family: Consolas, monospace; font-size: {small_size};'>"
                    html += f"<span style='color: #0078D4; font-weight: bold;'>{env_var['name']}</span>"
                    html += f"<span style='color: #666;'> = {env_var['value'][:50]}{'...' if len(env_var['value']) > 50 else ''}</span>"
                    html += "</div>"
                
                if details['env_vars_count'] > 10:
                    html += f"<div style='padding: 8px 0; color: #666; font-style: italic; font-size: {small_size};'>"
                    html += f"... and {details['env_vars_count'] - 10} more variables"
                    html += "</div>"
                
                html += "</div>"
            else:
                html += f"<p style='color: #999; font-style: italic; font-size: {text_size};'>No environment variables backed up</p>"
            
            html += "</div>"
            html += "</div>"
            
            self.backup_details_text.setHtml(html)
            
        except Exception as e:
            self.backup_details_text.setHtml(
                f"<div style='color: red; padding: {padding_lg};'>"
                f"<p style='font-size: {text_size};'><b>⚠️ Error loading backup details</b></p>"
                f"<p style='font-size: {small_size};'>{str(e)}</p>"
                "</div>"
            )
    
    def restore_selected_backup(self):
        """Restore the selected backup - Phase 1: Check and Install Missing Tools"""
        selected_rows = self.backups_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a backup to restore."
            )
            return
        
        row = selected_rows[0].row()
        if row < 0 or row >= len(self.available_backups):
            return
        
        backup = self.available_backups[row]
        backup_path = backup['backup_path']
        
        # Compare backup tools with currently detected tools
        comparison = self.restore_manager.compare_tools_with_system(backup_path, self.detected_tools)
        
        missing_tools = comparison['missing_tools']
        installed_tools = comparison['installed_tools']
        version_mismatch = comparison['version_mismatch']
        
        # Show installation dialog
        self.show_installation_dialog(backup, backup_path, missing_tools, installed_tools, version_mismatch)
    
    def show_installation_dialog(self, backup, backup_path, missing_tools, installed_tools, version_mismatch):
        """Show dialog for selecting tools to install"""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Restore Backup - Install Missing Tools")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel(f"<h3>📦 Backup: {backup['backup_name']}</h3>")
        layout.addWidget(header_label)
        
        # Status summary
        status_text = f"<p><b>Status Summary:</b></p><ul>"
        status_text += f"<li>✅ <b>{len(installed_tools)}</b> tool(s) already installed</li>"
        status_text += f"<li>❌ <b>{len(missing_tools)}</b> tool(s) need installation</li>"
        if version_mismatch:
            status_text += f"<li>⚠️ <b>{len(version_mismatch)}</b> tool(s) have version mismatch (will be skipped)</li>"
        status_text += "</ul>"
        
        status_label = QLabel(status_text)
        layout.addWidget(status_label)
        
        if not missing_tools:
            info_label = QLabel("<p style='color: green;'><b>✓ All tools from backup are already installed!</b></p>"
                               "<p>No installation needed. Click Close to finish.</p>")
            layout.addWidget(info_label)
            
            # Close button only
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec()
            return
        
        # Missing tools section
        missing_label = QLabel("<p><b>Select tools to install:</b></p>")
        layout.addWidget(missing_label)
        
        # Tools table
        tools_table = QTableWidget()
        tools_table.setColumnCount(4)
        tools_table.setHorizontalHeaderLabels(["Install", "Tool Name", "Version", "Install Method"])
        tools_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        tools_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tools_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        tools_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        tools_table.setColumnWidth(0, 60)
        tools_table.setColumnWidth(2, 100)
        tools_table.setColumnWidth(3, 120)
        tools_table.setAlternatingRowColors(True)
        tools_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tools_table.verticalHeader().setVisible(False)
        
        tools_table.setRowCount(len(missing_tools))
        
        for row, tool in enumerate(missing_tools):
            # Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Checked)
            tools_table.setItem(row, 0, check_item)
            
            # Tool name
            name_item = QTableWidgetItem(tool['name'])
            tools_table.setItem(row, 1, name_item)
            
            # Version
            version_item = QTableWidgetItem(tool['version'])
            tools_table.setItem(row, 2, version_item)
            
            # Install method
            winget_id = tool.get('winget_id') or self.restore_manager.get_winget_package_id(tool['name'])
            download_url = tool.get('download_url') or self.restore_manager.get_download_url(tool['name'], tool.get('version'))
            
            if winget_id:
                method_text = "winget"
            elif download_url:
                method_text = "URL Download"
            else:
                method_text = "Manual"
            
            method_item = QTableWidgetItem(method_text)
            tools_table.setItem(row, 3, method_item)
        
        self.style_table(tools_table)
        layout.addWidget(tools_table)
        
        # Select all/none buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("✓ Select All")
        select_all_btn.clicked.connect(lambda: self.toggle_all_checkboxes(tools_table, True))
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("✗ Deselect All")
        select_none_btn.clicked.connect(lambda: self.toggle_all_checkboxes(tools_table, False))
        button_layout.addWidget(select_none_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Warning about manual installs
        manual_tools = []
        for t in missing_tools:
            winget_id = t.get('winget_id') or self.restore_manager.get_winget_package_id(t['name'])
            download_url = t.get('download_url') or self.restore_manager.get_download_url(t['name'], t.get('version'))
            if not winget_id and not download_url:
                manual_tools.append(t)
        
        if manual_tools:
            warning_label = QLabel(
                f"<p style='color: #FF8C00;'>⚠️ <b>Note:</b> {len(manual_tools)} tool(s) marked as 'Manual' "
                "cannot be auto-installed. Download links will be provided.</p>"
            )
            layout.addWidget(warning_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox()
        install_btn = button_box.addButton("🚀 Install Selected Tools", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = button_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        
        button_box.accepted.connect(lambda: self.start_installation(dialog, backup_path, tools_table, missing_tools))
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def toggle_all_checkboxes(self, table, checked):
        """Toggle all checkboxes in the table"""
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                item.setCheckState(state)
    
    def start_installation(self, dialog, backup_path, tools_table, missing_tools):
        """Start installing selected tools"""
        # Get selected tools
        selected_tools = []
        for row in range(tools_table.rowCount()):
            check_item = tools_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.CheckState.Checked:
                selected_tools.append(missing_tools[row])
        
        if not selected_tools:
            QMessageBox.warning(dialog, "No Selection", "Please select at least one tool to install.")
            return
        
        # Close the dialog
        dialog.accept()
        
        # Show progress dialog and start installation
        self.show_installation_progress(backup_path, selected_tools)
    
    def show_installation_progress(self, backup_path, selected_tools):
        """Show installation progress dialog"""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextEdit
        
        # Create progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Installing Tools")
        progress_dialog.setMinimumWidth(600)
        progress_dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(progress_dialog)
        
        # Progress label
        self.install_progress_label = QLabel(f"Installing 0 of {len(selected_tools)} tools...")
        layout.addWidget(self.install_progress_label)
        
        # Progress bar
        self.install_progress_bar = QProgressBar()
        self.install_progress_bar.setMaximum(len(selected_tools))
        self.install_progress_bar.setValue(0)
        layout.addWidget(self.install_progress_bar)
        
        # Log text area
        self.install_log_text = QTextEdit()
        self.install_log_text.setReadOnly(True)
        self.install_log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: Consolas, monospace;
                font-size: {self.font_size_small}px;
                border: 1px solid #444;
            }}
        """)
        layout.addWidget(self.install_log_text)
        
        # Close button (disabled during installation)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.install_close_btn = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.install_close_btn.setEnabled(False)
        button_box.rejected.connect(progress_dialog.reject)
        layout.addWidget(button_box)
        
        # Start installation in background
        self.install_selected_tools_background(backup_path, selected_tools, progress_dialog)
        
        progress_dialog.exec()
    
    def install_selected_tools_background(self, backup_path, selected_tools, progress_dialog):
        """Install tools in background thread"""
        from PySide6.QtCore import QTimer
        import threading
        
        # Store results for UI updates
        self.install_results = []
        self.install_current = 0
        self.install_total = len(selected_tools)
        
        def install_worker():
            for i, tool in enumerate(selected_tools):
                tool_name = tool['name']
                tool_version = tool.get('version')
                tool_backup_data = tool.get('backup_data', {})
                winget_id = tool.get('winget_id') or self.restore_manager.get_winget_package_id(tool_name)
                download_url = tool.get('download_url') or self.restore_manager.get_download_url(tool_name, tool_version)
                
                # Store progress info
                self.install_current = i + 1
                
                # Immediately show what we're starting
                progress_info = {
                    'index': i + 1,
                    'tool_name': tool_name,
                    'version': tool_version,
                    'winget_id': winget_id,
                    'download_url': download_url,
                    'restore_result': None,
                    'stage': 'starting'
                }
                self.install_results.append(progress_info)
                
                # Step 1: Install the tool
                install_success = False
                install_result = None
                
                if winget_id:
                    # Show installing status
                    progress_info = {
                        'index': i + 1,
                        'tool_name': tool_name,
                        'version': tool_version,
                        'winget_id': winget_id,
                        'download_url': download_url,
                        'stage': 'installing',
                        'result': None,
                        'restore_result': None
                    }
                    self.install_results.append(progress_info)
                    
                    # Install via winget
                    install_result = self.restore_manager.install_tool_via_winget(tool_name, winget_id)
                    install_success = install_result['success']
                    
                elif download_url:
                    # Show installing status
                    progress_info = {
                        'index': i + 1,
                        'tool_name': tool_name,
                        'version': tool_version,
                        'winget_id': winget_id,
                        'download_url': download_url,
                        'stage': 'installing',
                        'result': None,
                        'restore_result': None
                    }
                    self.install_results.append(progress_info)
                    
                    # Install via URL download
                    install_result = self.restore_manager.install_tool_via_url(tool_name, download_url)
                    install_success = install_result['success']
                else:
                    install_result = {'success': False, 'message': 'Manual installation required'}
                
                # Show installation result
                progress_info = {
                    'index': i + 1,
                    'tool_name': tool_name,
                    'version': tool_version,
                    'winget_id': winget_id,
                    'download_url': download_url,
                    'stage': 'install_complete',
                    'result': install_result,
                    'restore_result': None
                }
                self.install_results.append(progress_info)
                
                # Step 2: Restore configurations
                # Restore configs even if installation failed (for manual installs like Oracle SQL Developer)
                if tool_backup_data:
                    # Show restoring status
                    progress_info = {
                        'index': i + 1,
                        'tool_name': tool_name,
                        'version': tool_version,
                        'stage': 'restoring',
                        'result': install_result,
                        'restore_result': None
                    }
                    self.install_results.append(progress_info)
                    
                    # Wait for successful installations to complete fully
                    if install_success:
                        import time
                        time.sleep(3)
                    
                    restore_result = self.restore_manager.restore_tool_configs(backup_path, tool_name, tool_backup_data)
                    
                    # Show restore result
                    progress_info = {
                        'index': i + 1,
                        'tool_name': tool_name,
                        'version': tool_version,
                        'stage': 'complete',
                        'result': install_result,
                        'restore_result': restore_result,
                        'manual_install': not install_success and install_result.get('requires_manual', False)
                    }
                    self.install_results.append(progress_info)
        
        # Timer to update UI from main thread
        def update_ui():
            if self.install_results:
                info = self.install_results.pop(0)
                
                stage = info.get('stage', 'complete')
                
                if stage == 'starting':
                    # Initial message
                    self.install_progress_label.setText(
                        f"Starting {info['index']} of {self.install_total}: {info['tool_name']}..."
                    )
                    self.install_log_text.append(f"\n{'='*60}")
                    self.install_log_text.append(f"📦 {info['index']}/{self.install_total}: {info['tool_name']} v{info['version']}")
                    
                elif stage == 'installing':
                    # Show installation starting
                    self.install_progress_label.setText(
                        f"Installing {info['index']} of {self.install_total}: {info['tool_name']}..."
                    )
                    
                    if info.get('winget_id'):
                        self.install_log_text.append(f"   🔽 Installing via winget...")
                        self.install_log_text.append(f"      ID: {info['winget_id']}")
                    elif info.get('download_url'):
                        self.install_log_text.append(f"   🔽 Downloading from URL...")
                        self.install_log_text.append(f"      {info['download_url']}")
                    
                elif stage == 'install_complete':
                    # Show installation result
                    result = info.get('result', {})
                    already_installed = result.get('already_installed', False)
                    
                    if result.get('success'):
                        if already_installed:
                            self.install_log_text.append(f"   ℹ️  Already installed - skipping installation")
                        else:
                            self.install_log_text.append(f"   ✅ Installation successful")
                    else:
                        self.install_log_text.append(f"   ❌ Installation failed: {result.get('message', 'Unknown error')}")
                        # Show additional output if available
                        if 'output' in result and result['output']:
                            output_lines = result['output'].strip().split('\n')
                            for line in output_lines[:3]:
                                if line.strip():
                                    self.install_log_text.append(f"      {line.strip()}")
                    
                elif stage == 'restoring':
                    # Show restoration starting
                    result = info.get('result', {})
                    manual_install = result.get('requires_manual', False)
                    
                    if manual_install:
                        self.install_progress_label.setText(
                            f"Pre-restoring configs {info['index']} of {self.install_total}: {info['tool_name']}..."
                        )
                        self.install_log_text.append(f"   🔧 Pre-restoring configurations for manual installation...")
                        self.install_log_text.append(f"      (Configs will be ready when you install the tool)")
                    else:
                        self.install_progress_label.setText(
                            f"Restoring configs {info['index']} of {self.install_total}: {info['tool_name']}..."
                        )
                        self.install_log_text.append(f"   🔧 Restoring configurations...")
                    
                elif stage == 'complete':
                    # Show final restoration results
                    manual_install = info.get('manual_install', False)
                    restore = info.get('restore_result')
                    
                    if restore:
                        if restore['restored_items']:
                            if manual_install:
                                self.install_log_text.append(f"   ✅ Pre-restored {len(restore['restored_items'])} item(s) (ready for when you install):")
                            else:
                                self.install_log_text.append(f"   ✅ Restored {len(restore['restored_items'])} item(s):")
                            
                            for item in restore['restored_items'][:3]:
                                self.install_log_text.append(f"      • {item}")
                            if len(restore['restored_items']) > 3:
                                self.install_log_text.append(f"      • ... and {len(restore['restored_items']) - 3} more")
                        
                        if restore['failed_items']:
                            self.install_log_text.append(f"   ⚠️  Failed {len(restore['failed_items'])} item(s):")
                            for item in restore['failed_items'][:2]:
                                self.install_log_text.append(f"      • {item}")
                        
                        if restore['skipped_items']:
                            self.install_log_text.append(f"   ⏭️  Skipped {len(restore['skipped_items'])} item(s)")
                    
                    # Show helpful message for manual installations
                    if manual_install:
                        self.install_log_text.append(f"   💡 Please install {info['tool_name']} manually, your configs are already restored")
                    
                    # Update progress bar after complete
                    self.install_progress_bar.setValue(info['index'])
            
            # Check if installation complete
            if hasattr(self, 'install_thread') and not self.install_thread.is_alive() and not self.install_results:
                self.install_timer.stop()
                self.install_progress_label.setText(
                    f"✅ Installation complete! ({self.install_total} tools processed)"
                )
                self.install_close_btn.setEnabled(True)
                self.install_log_text.append(f"\n{'='*60}")
                self.install_log_text.append(f"Installation process finished.")
        
        # Start worker thread
        self.install_thread = threading.Thread(target=install_worker, daemon=True)
        self.install_thread.start()
        
        # Start UI update timer (100ms interval)
        self.install_timer = QTimer()
        self.install_timer.timeout.connect(update_ui)
        self.install_timer.start(100)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About W-Rebuild",
            "<h3>W-Rebuild v3.0</h3>"
            "<p>Windows System Detection, Backup & Restore Tool</p>"
            "<p>Detects installed development tools and manages configurations via OneDrive.</p>"
            "<p><b>✓ Step 1:</b> Detection - Scan for installed software<br>"
            "<b>✓ Step 2:</b> Backup - Save configurations & settings<br>"
            "<b>⚙️ Step 3:</b> Restore - Install missing tools and restore configs</p>"
        )
    
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("W-Rebuild")
    app.setStyle("Fusion")  # Modern style
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
