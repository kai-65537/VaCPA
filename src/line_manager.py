import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph.opengl as gl

from constants import r, LINE_WIDTH


class LineManagerMixin:
    """Mixin providing longitude line management."""

    line_sets: list

    def create_default_lines(self):
        """Create default longitude line sets"""
        self.add_line_set(self.tr('longitudes_x'), (90, 0), 16, (1, 0, 0, 1))
        self.add_line_set(self.tr('longitudes_y'), (90, 90), 16, (0, 1, 0, 1))
        self.add_line_set(self.tr('longitudes_z'), (0, 0), 16, (0, 0, 1, 1))

    def generate_longitude_lines(self, direction, divisions, color, visible=True):
        """Generate longitude lines for a given spherical direction"""
        lines = []
        t = np.linspace(0, np.pi, 100)
        theta = np.radians(direction[0])
        phi = np.radians(direction[1])
        d = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ])
        if np.allclose(d, [0, 0, 1]):
            e1 = np.array([1, 0, 0])
        else:
            e1 = np.cross(d, [0, 0, 1])
            e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(d, e1)
        for i in range(divisions):
            angle = 2 * np.pi * i / divisions
            v = np.cos(angle) * e1 + np.sin(angle) * e2
            x = r * (np.cos(t) * d[0] + np.sin(t) * v[0])
            y = r * (np.cos(t) * d[1] + np.sin(t) * v[1])
            z = r * (np.cos(t) * d[2] + np.sin(t) * v[2])
            pts = np.vstack([x, y, z]).T.astype(np.float32)
            line = gl.GLLinePlotItem(pos=pts, width=LINE_WIDTH, color=color)
            line.setVisible(visible)
            self.view.addItem(line)
            lines.append({'line': line, 'coords': (x, y, z)})
        return lines

    def add_line_set(self, name, direction, divisions, color):
        """Add a new set of longitude lines"""
        lines = self.generate_longitude_lines(direction, divisions, color, True)
        set_data = {
            'name': name,
            'direction': direction,
            'divisions': divisions,
            'color': color,
            'visible': True,
            'lines': lines,
        }
        self.line_sets.append(set_data)
        self.update_line_list()

    def update_line_list(self):
        """Update the list of line sets in the UI"""
        self.line_list.clear()
        for idx, set_data in enumerate(self.line_sets):
            item = QtWidgets.QListWidgetItem(set_data['name'])
            item.setData(QtCore.Qt.UserRole, idx)
            self.line_list.addItem(item)

    def on_line_selected(self):
        """Handle line set selection in the list"""
        selected = self.line_list.selectedItems()
        if not selected:
            self.line_controls.setVisible(False)
            return

        self.line_controls.setVisible(True)
        set_idx = selected[0].data(QtCore.Qt.UserRole)
        set_data = self.line_sets[set_idx]
        self.line_visible.blockSignals(True)
        self.theta_spin.blockSignals(True)
        self.phi_spin.blockSignals(True)
        self.divisions_spin.blockSignals(True)
        self.line_visible.setChecked(set_data['visible'])
        theta, phi = set_data['direction']
        self.theta_spin.setValue(theta)
        self.phi_spin.setValue(phi)
        self.divisions_spin.setValue(set_data['divisions'])
        self.line_visible.blockSignals(False)
        self.theta_spin.blockSignals(False)
        self.phi_spin.blockSignals(False)
        self.divisions_spin.blockSignals(False)

    def update_selected_line_set(self):
        """Update the selected line set based on UI controls"""
        selected = self.line_list.selectedItems()
        if not selected:
            return

        set_idx = selected[0].data(QtCore.Qt.UserRole)
        set_data = self.line_sets[set_idx]

        set_data['visible'] = self.line_visible.isChecked()
        for line_obj in set_data['lines']:
            line_obj['line'].setVisible(set_data['visible'])

        theta = self.theta_spin.value()
        phi = self.phi_spin.value()
        divisions = self.divisions_spin.value()
        if (theta, phi) != set_data['direction'] or divisions != set_data['divisions']:
            for line_obj in set_data['lines']:
                self.view.removeItem(line_obj['line'])
            set_data['direction'] = (theta, phi)
            set_data['divisions'] = divisions
            set_data['lines'] = self.generate_longitude_lines((theta, phi), divisions, set_data['color'], set_data['visible'])

        self.update_3d()
        self.schedule_projection_update()

    def change_line_color(self):
        """Change color of selected line set"""
        selected = self.line_list.selectedItems()
        if not selected:
            return

        set_idx = selected[0].data(QtCore.Qt.UserRole)
        set_data = self.line_sets[set_idx]

        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            r_val, g_val, b_val, a_val = color.getRgbF()
            set_data['color'] = (r_val, g_val, b_val, a_val)
            for line_obj in set_data['lines']:
                line_obj['line'].setData(color=set_data['color'])
            self.update_projection()

        self.schedule_projection_update()

    def rename_selected_line_set(self):
        """Rename the selected line set"""
        selected = self.line_list.selectedItems()
        if not selected:
            return

        set_idx = selected[0].data(QtCore.Qt.UserRole)
        set_data = self.line_sets[set_idx]

        new_name, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr('rename_line_set_title'),
            self.tr('rename_line_set_prompt'),
            text=set_data['name']
        )

        if ok and new_name:
            set_data['name'] = new_name
            self.update_line_list()
            for i in range(self.line_list.count()):
                if self.line_list.item(i).data(QtCore.Qt.UserRole) == set_idx:
                    self.line_list.setCurrentRow(i)
                    break

    def delete_selected_line_set(self):
        """Delete the selected line set"""
        selected = self.line_list.selectedItems()
        if not selected:
            return

        set_idx = selected[0].data(QtCore.Qt.UserRole)
        set_data = self.line_sets[set_idx]

        for line_obj in set_data['lines']:
            self.view.removeItem(line_obj['line'])
        del self.line_sets[set_idx]
        self.update_line_list()
        self.line_controls.setVisible(False)
        self.update_projection()
        self.schedule_projection_update()

    def show_add_line_dialog(self):
        """Show dialog to add new longitude line set"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.tr('add_longitude_set_title'))
        dialog.setMinimumWidth(250)

        layout = QtWidgets.QFormLayout(dialog)

        name_edit = QtWidgets.QLineEdit()
        theta_spin = QtWidgets.QDoubleSpinBox()
        theta_spin.setRange(0, 180)
        theta_spin.setDecimals(1)
        phi_spin = QtWidgets.QDoubleSpinBox()
        phi_spin.setRange(0, 360)
        phi_spin.setDecimals(1)
        divisions_spin = QtWidgets.QSpinBox()
        divisions_spin.setRange(1, 128)
        divisions_spin.setValue(16)

        layout.addRow(self.tr('dialog_name'), name_edit)
        layout.addRow(self.tr('dialog_theta'), theta_spin)
        layout.addRow(self.tr('dialog_phi'), phi_spin)
        layout.addRow(self.tr('dialog_divisions'), divisions_spin)

        color_button = QtWidgets.QPushButton(self.tr('dialog_select_color'))
        color_preview = QtWidgets.QFrame()
        color_preview.setFixedSize(24, 24)
        color_preview.setStyleSheet("background-color: red;")
        selected_color = [1, 0, 0, 1]

        def choose_color():
            color = QtWidgets.QColorDialog.getColor()
            if color.isValid():
                selected_color[:] = [color.redF(), color.greenF(), color.blueF(), 1.0]
                color_preview.setStyleSheet(
                    f"background-color: rgba({color.red()}, {color.green()}, {color.blue()}, 255);")

        color_button.clicked.connect(choose_color)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(color_button)
        color_layout.addWidget(color_preview)
        color_layout.addStretch()
        layout.addRow(self.tr('dialog_color'), color_layout)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_edit.text() or self.tr('unnamed')
            direction = (theta_spin.value(), phi_spin.value())
            divisions = divisions_spin.value()
            self.add_line_set(name, direction, divisions, selected_color)
            self.update_3d()
            self.schedule_projection_update()
