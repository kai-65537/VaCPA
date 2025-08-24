import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from constants import r, LINE_WIDTH
from projection import (
    get_rotation_matrices,
    rotate_sphere_fast,
    get_projection,
)

from ui import UIMixin
from line_manager import LineManagerMixin


class SphereProjectionVisualizer(UIMixin, LineManagerMixin, QtWidgets.QMainWindow):
    """Main application window combining UI, line management and export logic."""

    def __init__(self):
        super().__init__()
        self.current_language = 'en'
        self.setWindowTitle('VaCPA')
        self.setGeometry(100, 100, 1400, 900)

        self.line_sets = []
        self.projection_needs_update = False

        # Timer for delayed projection updates
        self.update_timer = QtCore.QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_projection)

        # Setup UI components
        self.setup_ui()
        self.setup_menu()
        self.setup_styles()

        # Initialize visualization
        self.create_default_lines()
        self.update_3d()
        self.update_ui_texts()

    # ------------------------------------------------------------------
    def schedule_projection_update(self):
        """Schedule a projection update with delay"""
        self.projection_needs_update = True
        if not self.update_timer.isActive():
            self.update_timer.start(25)  # Update after 200ms delay

    def update_3d(self):
        """Update the 3D view based on current parameters"""
        tilt = self.tilt_slider['min'] + self.tilt_slider['slider'].value() * self.tilt_slider['step']
        roll = self.roll_slider['min'] + self.roll_slider['slider'].value() * self.roll_slider['step']
        pan = self.pan_slider['min'] + self.pan_slider['slider'].value() * self.pan_slider['step']

        # Precompute rotation matrix once per frame
        R = get_rotation_matrices(tilt, roll, pan)

        for set_data in self.line_sets:
            for obj in set_data['lines']:
                x, y, z = obj['coords']
                x_rot, y_rot, z_rot = rotate_sphere_fast(x, y, z, R)
                pts = np.vstack([x_rot.flatten(), y_rot.flatten(), z_rot.flatten()]).T.astype(np.float32)
                obj['line'].setData(pos=pts)
                obj['rotated'] = (x_rot, y_rot, z_rot)

        # Schedule projection update
        self.schedule_projection_update()

    def update_projection(self):
        """Update the 2D projection based on current 3D view"""
        if not self.projection_needs_update:
            return

        self.plot_widget.clear()
        projection_index = self.projection_combo.currentIndex()
        projection_types = ["Stereographic", "Azimuthal", "Orthographic"]
        projection_type = (
            projection_types[projection_index]
            if projection_index < len(projection_types)
            else "Orthographic"
        )

        # Draw sphere outline
        t = np.linspace(0, 2 * np.pi, 100)
        outline = pg.PlotDataItem(2 * np.cos(t), 2 * np.sin(t), pen=pg.mkPen('k', width=3 * LINE_WIDTH))
        self.plot_widget.addItem(outline)

        # Draw all visible lines
        for set_data in self.line_sets:
            if not set_data['visible']:
                continue
            for obj in set_data['lines']:
                if 'rotated' not in obj:
                    continue

                x_rot, y_rot, z_rot = obj['rotated']
                x_proj, y_proj = get_projection(x_rot, y_rot, z_rot, r, projection_type)

                if projection_index == 0:
                    mask = (1 - z_rot / r) < 0.01
                    if mask.ndim > 0:
                        x_proj = np.where(mask, np.nan, x_proj)
                        y_proj = np.where(mask, np.nan, y_proj)

                color = set_data['color']
                qcolor = QtGui.QColor(*[int(c * 255) for c in color[:3]])

                line_item = pg.PlotDataItem(
                    x_proj, y_proj,
                    pen=pg.mkPen(qcolor, width=LINE_WIDTH),
                    connect='finite'
                )
                self.plot_widget.addItem(line_item)

        self.projection_needs_update = False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SphereProjectionVisualizer()
    window.show()
    sys.exit(app.exec_())
