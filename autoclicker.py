import sys
import pyautogui
import keyboard
import time
import random
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QComboBox,
    QTabWidget, QSpinBox, QLineEdit, QHBoxLayout, QCheckBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer

class AutoClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Autoclicker")
        self.setGeometry(300, 300, 600, 400)
        
        # Autoclicker settings
        self.clicking = False
        self.interval = 0.05
        self.click_type = "Single Click"
        self.target_mode = "Follow Mouse"
        self.target_location = (0, 0)
        self.pattern = "Standard"
        self.total_clicks = 0
        self.start_time = None
        self.hotkey = "f6"
        self.dark_mode = False
        self.always_on_top = False
        
        # GUI creation
        self.init_ui()
        
        # Start hotkey monitor in separate thread
        threading.Thread(target=self.monitor_hotkey, daemon=True).start()

    def init_ui(self):
        # Tab Widget for organized sections
        tab_widget = QTabWidget()

        # === Click Settings Tab ===
        click_tab = QWidget()
        click_layout = QVBoxLayout()

        # Click Type Dropdown
        click_type_label = QLabel("Click Type:")
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Single Click", "Double Click", "Randomized Click"])
        self.click_type_combo.currentTextChanged.connect(self.update_click_type)
        click_layout.addWidget(click_type_label)
        click_layout.addWidget(self.click_type_combo)

        # Click Interval Slider
        interval_label = QLabel("Click Interval (ms):")
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(1)
        self.interval_slider.setMaximum(1000)
        self.interval_slider.setValue(int(self.interval * 1000))
        self.interval_slider.valueChanged.connect(self.update_interval)
        click_layout.addWidget(interval_label)
        click_layout.addWidget(self.interval_slider)

        # Real-time display of interval
        self.interval_display = QLabel(f"Interval: {self.interval * 1000:.0f} ms")
        click_layout.addWidget(self.interval_display)

        # Click Pattern Dropdown
        pattern_label = QLabel("Click Pattern:")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Standard", "Zig-Zag", "Circular", "Randomized"])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern)
        click_layout.addWidget(pattern_label)
        click_layout.addWidget(self.pattern_combo)

        click_tab.setLayout(click_layout)
        tab_widget.addTab(click_tab, "Click Settings")

        # === Targeting Tab ===
        target_tab = QWidget()
        target_layout = QVBoxLayout()

        # Target Mode Dropdown
        target_mode_label = QLabel("Target Mode:")
        self.target_mode_combo = QComboBox()
        self.target_mode_combo.addItems(["Follow Mouse", "Fixed Position"])
        self.target_mode_combo.currentTextChanged.connect(self.update_target_mode)
        target_layout.addWidget(target_mode_label)
        target_layout.addWidget(self.target_mode_combo)

        # Position Controls
        pos_layout = QHBoxLayout()
        pos_label = QLabel("Position (x, y):")
        self.pos_x = QSpinBox()
        self.pos_x.setRange(0, 1920)  # Adjust for screen size
        self.pos_y = QSpinBox()
        self.pos_y.setRange(0, 1080)  # Adjust for screen size
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self.pos_x)
        pos_layout.addWidget(self.pos_y)
        target_layout.addLayout(pos_layout)

        target_tab.setLayout(target_layout)
        tab_widget.addTab(target_tab, "Targeting")

        # === Preferences Tab ===
        pref_tab = QWidget()
        pref_layout = QVBoxLayout()

        # Dark Mode Checkbox
        dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        pref_layout.addWidget(dark_mode_checkbox)

        # Always-on-Top Checkbox
        always_on_top_checkbox = QCheckBox("Always on Top")
        always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)
        pref_layout.addWidget(always_on_top_checkbox)

        # Hotkey Customization
        hotkey_label = QLabel("Set Hotkey:")
        self.hotkey_input = QLineEdit(self.hotkey)
        self.hotkey_input.setPlaceholderText("Set Hotkey (default: F6)")
        self.hotkey_input.textChanged.connect(self.update_hotkey)
        pref_layout.addWidget(hotkey_label)
        pref_layout.addWidget(self.hotkey_input)

        pref_tab.setLayout(pref_layout)
        tab_widget.addTab(pref_tab, "Preferences")

        # === Statistics Tab ===
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()

        # Real-time Click Count and CPS
        self.click_count_label = QLabel("Total Clicks: 0")
        self.cps_label = QLabel("Clicks Per Second: 0")
        self.elapsed_time_label = QLabel("Elapsed Time: 0s")
        stats_layout.addWidget(self.click_count_label)
        stats_layout.addWidget(self.cps_label)
        stats_layout.addWidget(self.elapsed_time_label)

        stats_tab.setLayout(stats_layout)
        tab_widget.addTab(stats_tab, "Statistics")

        # === Emergency Stop Button ===
        emergency_layout = QVBoxLayout()
        self.emergency_button = QPushButton("Emergency STOP")
        self.emergency_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 16px;")
        self.emergency_button.clicked.connect(self.stop_immediately)
        emergency_layout.addWidget(self.emergency_button)

        # Main Control Buttons
        control_layout = QVBoxLayout()
        self.start_stop_button = QPushButton("Start / Stop Autoclicker (F6)")
        self.start_stop_button.clicked.connect(self.toggle_clicking)
        control_layout.addWidget(self.start_stop_button)
        
        # Main Layout Assembly
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(emergency_layout)
        self.setLayout(main_layout)

    def update_click_type(self):
        self.click_type = self.click_type_combo.currentText()

    def update_interval(self):
        self.interval = self.interval_slider.value() / 1000
        self.interval_display.setText(f"Interval: {self.interval * 1000:.0f} ms")

    def update_pattern(self):
        self.pattern = self.pattern_combo.currentText()

    def update_target_mode(self):
        self.target_mode = self.target_mode_combo.currentText()
        if self.target_mode == "Fixed Position":
            self.target_location = (self.pos_x.value(), self.pos_y.value())

    def update_hotkey(self):
        self.hotkey = self.hotkey_input.text()

    def toggle_clicking(self):
        self.clicking = not self.clicking
        if self.clicking:
            self.start_time = time.time()
            self.total_clicks = 0
            self.start_stop_button.setText("Stop Autoclicker")
            self.click_thread = threading.Thread(target=self.perform_clicking)
            self.click_thread.start()
        else:
            self.start_stop_button.setText("Start Autoclicker")

    def toggle_dark_mode(self, state):
        self.dark_mode = state == Qt.Checked
        self.setStyleSheet("background-color: #333; color: #fff;" if self.dark_mode else "")

    def toggle_always_on_top(self, state):
        self.always_on_top = state == Qt.Checked
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.always_on_top)
        self.show()

    def stop_immediately(self):
        self.clicking = False
        self.start_stop_button.setText("Start Autoclicker")

    def perform_clicking(self):
        while self.clicking:
            if self.target_mode == "Follow Mouse":
                pyautogui.click()
            else:
                pyautogui.click(self.target_location[0], self.target_location[1])
            
            self.total_clicks += 1
            self.update_statistics()
            time.sleep(self.interval)

    def update_statistics(self):
        self.click_count_label.setText(f"Total Clicks: {self.total_clicks}")
        elapsed_time = time.time() - self.start_time
        self.elapsed_time_label.setText(f"Elapsed Time: {int(elapsed_time)}s")
        cps = self.total_clicks / elapsed_time if elapsed_time > 0 else 0
        self.cps_label.setText(f"Clicks Per Second: {cps:.2f}")

    def monitor_hotkey(self):
        while True:
            if keyboard.is_pressed(self.hotkey):
                self.toggle_clicking()
                keyboard.wait(self.hotkey)

# Run the application
app = QApplication(sys.argv)
clicker = AutoClicker()
clicker.show()
sys.exit(app.exec_())
