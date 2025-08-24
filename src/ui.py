from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from translations import TRANSLATIONS
from constants import PLOT_BOUNDS


class UIMixin:
    """Mixin containing UI-related functionality for the visualizer."""

    current_language: str

    def tr(self, key):
        """Translate a key based on current language."""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['en']).get(key, key)

    def set_language(self, lang):
        """Set current language and refresh UI text."""
        self.current_language = lang
        if hasattr(self, 'lang_en_action'):
            self.lang_en_action.setChecked(lang == 'en')
        if hasattr(self, 'lang_zh_action'):
            self.lang_zh_action.setChecked(lang == 'zh_CN')
        self.update_ui_texts()

    def update_ui_texts(self):
        """Update all translatable UI elements."""
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(self.tr('file_menu'))
        if hasattr(self, 'help_menu'):
            self.help_menu.setTitle(self.tr('help_menu'))
        if hasattr(self, 'language_menu'):
            self.language_menu.setTitle(self.tr('language_menu'))
        if hasattr(self, 'exit_action'):
            self.exit_action.setText(self.tr('exit_action'))
        if hasattr(self, 'about_action'):
            self.about_action.setText(self.tr('about_action'))
        if hasattr(self, 'lang_en_action'):
            self.lang_en_action.setText(self.tr('language_english'))
        if hasattr(self, 'lang_zh_action'):
            self.lang_zh_action.setText(self.tr('language_chinese'))
        if hasattr(self, 'controls_box'):
            self.controls_box.setTitle(self.tr('controls_group'))
        if hasattr(self, 'line_group'):
            self.line_group.setTitle(self.tr('line_management_group'))
        if hasattr(self, 'rotation_group'):
            self.rotation_group.setTitle(self.tr('rotation_group'))
        if hasattr(self, 'toggle_3d_button'):
            if self.view.isVisible():
                self.toggle_3d_button.setText(self.tr('hide_3d_view'))
            else:
                self.toggle_3d_button.setText(self.tr('show_3d_view'))
        if hasattr(self, 'projection_label'):
            self.projection_label.setText(self.tr('projection_label'))
        if hasattr(self, 'projection_combo'):
            self.projection_combo.setItemText(0, self.tr('projection_stereographic'))
            self.projection_combo.setItemText(1, self.tr('projection_azimuthal'))
            self.projection_combo.setItemText(2, self.tr('projection_orthographic'))
        if hasattr(self, 'line_visible'):
            self.line_visible.setText(self.tr('line_visible'))
        if hasattr(self, 'line_color'):
            self.line_color.setText(self.tr('line_color'))
        if hasattr(self, 'rename_button'):
            self.rename_button.setText(self.tr('line_rename'))
        if hasattr(self, 'line_delete'):
            self.line_delete.setText(self.tr('line_delete'))
        if hasattr(self, 'theta_label'):
            self.theta_label.setText(self.tr('theta_label'))
        if hasattr(self, 'phi_label'):
            self.phi_label.setText(self.tr('phi_label'))
        if hasattr(self, 'divisions_label'):
            self.divisions_label.setText(self.tr('divisions_label'))
        if hasattr(self, 'add_line_button'):
            self.add_line_button.setText(self.tr('add_line_set'))
        if hasattr(self, 'tilt_slider'):
            self.tilt_slider['name'] = self.tr('tilt')
            self.tilt_slider['on_val_change'](self.tilt_slider['slider'].value())
        if hasattr(self, 'roll_slider'):
            self.roll_slider['name'] = self.tr('roll')
            self.roll_slider['on_val_change'](self.roll_slider['slider'].value())
        if hasattr(self, 'pan_slider'):
            self.pan_slider['name'] = self.tr('pan')
            self.pan_slider['on_val_change'](self.pan_slider['slider'].value())

    # --- UI setup helpers -------------------------------------------------
    def setup_ui(self):
        """Initialize all UI components"""
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # LEFT panel - Projection view and controls
        left_panel = QtWidgets.QFrame()
        left_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        # Projection controls
        self.setup_projection_controls(left_layout)

        # 2D Projection plot
        self.setup_projection_plot(left_layout)

        # RIGHT panel - 3D view and controls
        right_panel = QtWidgets.QFrame()
        right_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # 3D View
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 5
        # right_layout.addWidget(self.view, 1)

        # Controls section
        self.controls_box = QtWidgets.QGroupBox(self.tr('controls_group'))
        control_layout = QtWidgets.QVBoxLayout(self.controls_box)
        right_layout.addWidget(self.controls_box, 1)

        # Toggle 3D view button
        self.toggle_3d_button = QtWidgets.QPushButton(self.tr('hide_3d_view'))
        self.toggle_3d_button.clicked.connect(self.toggle_3d_view)
        # control_layout.addWidget(self.toggle_3d_button)

        # Rotation controls
        self.rotation_group = QtWidgets.QGroupBox(self.tr('rotation_group'))
        rotation_layout = QtWidgets.QVBoxLayout(self.rotation_group)
        control_layout.addWidget(self.rotation_group, 0)

        self.setup_rotation_controls(rotation_layout)

        # Line management
        self.line_group = QtWidgets.QGroupBox(self.tr('line_management_group'))
        line_layout = QtWidgets.QVBoxLayout(self.line_group)
        control_layout.addWidget(self.line_group)

        self.setup_line_management(line_layout)

        control_layout.addStretch()

        # Add panels to main layout
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)

    def setup_projection_controls(self, parent_layout):
        """Setup projection selection controls"""
        projection_layout = QtWidgets.QHBoxLayout()
        self.projection_label = QtWidgets.QLabel(self.tr('projection_label'))
        self.projection_combo = QtWidgets.QComboBox()
        self.projection_combo.addItems([
            self.tr('projection_stereographic'),
            self.tr('projection_azimuthal'),
            self.tr('projection_orthographic')
        ])
        self.projection_combo.currentIndexChanged.connect(self.schedule_projection_update)
        projection_layout.addWidget(self.projection_label)
        projection_layout.addWidget(self.projection_combo)
        parent_layout.addLayout(projection_layout)

    def setup_projection_plot(self, parent_layout):
        """Setup the 2D projection plot"""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        # Use the configured plot bounds directly so the coordinates match
        # the rectangle's constraints.
        self.plot_widget.setXRange(PLOT_BOUNDS[0], PLOT_BOUNDS[0] + PLOT_BOUNDS[2])
        self.plot_widget.setYRange(PLOT_BOUNDS[1], PLOT_BOUNDS[1] + PLOT_BOUNDS[3])
        self.plot_widget.setAspectLocked(True)
        parent_layout.addWidget(self.plot_widget, 1)

    def setup_line_management(self, parent_layout):
        """Setup UI for managing line sets"""
        self.line_list = QtWidgets.QListWidget()
        self.line_list.itemSelectionChanged.connect(self.on_line_selected)
        parent_layout.addWidget(self.line_list)

        # Line controls
        self.line_controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QGridLayout(self.line_controls)
        parent_layout.addWidget(self.line_controls)

        self.line_visible = QtWidgets.QCheckBox(self.tr('line_visible'))
        self.line_visible.stateChanged.connect(self.update_selected_line_set)
        controls_layout.addWidget(self.line_visible, 0, 0)

        self.line_color = QtWidgets.QPushButton(self.tr('line_color'))
        self.line_color.clicked.connect(self.change_line_color)
        controls_layout.addWidget(self.line_color, 0, 1)

        self.rename_button = QtWidgets.QPushButton(self.tr('line_rename'))
        self.rename_button.clicked.connect(self.rename_selected_line_set)
        controls_layout.addWidget(self.rename_button, 1, 0)

        self.line_delete = QtWidgets.QPushButton(self.tr('line_delete'))
        self.line_delete.clicked.connect(self.delete_selected_line_set)
        controls_layout.addWidget(self.line_delete, 1, 1)

        self.theta_label = QtWidgets.QLabel(self.tr('theta_label'))
        controls_layout.addWidget(self.theta_label, 2, 0)
        self.theta_spin = QtWidgets.QDoubleSpinBox()
        self.theta_spin.setRange(0, 180)
        self.theta_spin.valueChanged.connect(self.update_selected_line_set)
        controls_layout.addWidget(self.theta_spin, 2, 1)

        self.phi_label = QtWidgets.QLabel(self.tr('phi_label'))
        controls_layout.addWidget(self.phi_label, 3, 0)
        self.phi_spin = QtWidgets.QDoubleSpinBox()
        self.phi_spin.setRange(0, 360)
        self.phi_spin.valueChanged.connect(self.update_selected_line_set)
        controls_layout.addWidget(self.phi_spin, 3, 1)

        self.divisions_label = QtWidgets.QLabel(self.tr('divisions_label'))
        controls_layout.addWidget(self.divisions_label, 4, 0)
        self.divisions_spin = QtWidgets.QSpinBox()
        self.divisions_spin.setRange(1, 128)
        self.divisions_spin.valueChanged.connect(self.update_selected_line_set)
        controls_layout.addWidget(self.divisions_spin, 4, 1)

        self.add_line_button = QtWidgets.QPushButton(self.tr('add_line_set'))
        self.add_line_button.clicked.connect(self.show_add_line_dialog)
        controls_layout.addWidget(self.add_line_button, 5, 0, 1, 2)

        self.line_controls.setVisible(False)

    def setup_rotation_controls(self, parent_layout):
        """Setup rotation sliders"""
        self.tilt_slider = self.create_slider(self.tr('tilt'), 0, np.pi/2, np.pi/180)
        parent_layout.addWidget(self.tilt_slider['label'])
        parent_layout.addWidget(self.tilt_slider['slider'])
        self.tilt_slider['slider'].valueChanged.connect(self.update_3d)

        self.roll_slider = self.create_slider(self.tr('roll'), 0, np.pi/2, np.pi/180)
        parent_layout.addWidget(self.roll_slider['label'])
        parent_layout.addWidget(self.roll_slider['slider'])
        self.roll_slider['slider'].valueChanged.connect(self.update_3d)

        self.pan_slider = self.create_slider(self.tr('pan'), 0, np.pi/2, np.pi/180)
        parent_layout.addWidget(self.pan_slider['label'])
        parent_layout.addWidget(self.pan_slider['slider'])
        self.pan_slider['slider'].valueChanged.connect(self.update_3d)

    def setup_menu(self):
        """Setup application menu"""
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu(self.tr('file_menu'))
        self.help_menu = menubar.addMenu(self.tr('help_menu'))
        self.language_menu = menubar.addMenu(self.tr('language_menu'))

        self.exit_action = QtWidgets.QAction(self.tr('exit_action'), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.about_action = QtWidgets.QAction(self.tr('about_action'), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

        self.lang_en_action = QtWidgets.QAction(self.tr('language_english'), self, checkable=True)
        self.lang_en_action.setChecked(True)
        self.lang_en_action.triggered.connect(lambda: self.set_language('en'))
        self.lang_zh_action = QtWidgets.QAction(self.tr('language_chinese'), self, checkable=True)
        self.lang_zh_action.triggered.connect(lambda: self.set_language('zh_CN'))

        self.language_menu.addAction(self.lang_en_action)
        self.language_menu.addAction(self.lang_zh_action)

    def show_about(self):
        """Display about dialog"""
        QtWidgets.QMessageBox.information(
            self, self.tr('about_window_title'), self.tr('about_html')
        )

    def setup_styles(self):
        """Setup application styling"""
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QLabel { font-size: 12px; }
            QPushButton { font-size: 12px; }
            QGroupBox { font-size: 14px; font-weight: bold; }
        """)

    def create_slider(self, name, min_val, max_val, step):
        """Helper to create a labeled slider"""
        label = QtWidgets.QLabel(f"{name}: 0°")
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(int((max_val - min_val) / step))

        data = {
            'label': label,
            'slider': slider,
            'min': min_val,
            'max': max_val,
            'step': step,
            'name': name,
        }

        def on_val_change(val):
            real_val = data['min'] + val * data['step']
            deg_val = np.degrees(real_val)
            data['label'].setText(f"{data['name']}: {deg_val:.1f}°")

        slider.valueChanged.connect(on_val_change)
        data['on_val_change'] = on_val_change
        return data

    def toggle_3d_view(self):
        """Toggle visibility of the 3D view"""
        if self.view.isVisible():
            self.view.hide()
            self.toggle_3d_button.setText(self.tr('show_3d_view'))
        else:
            self.view.show()
            self.toggle_3d_button.setText(self.tr('hide_3d_view'))
