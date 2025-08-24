import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph
from visualizer import SphereProjectionVisualizer


def main():
    """Main application entry point."""
    if sys.platform.startswith("win"):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        if hasattr(QtWidgets.QApplication, "setHighDpiScaleFactorRoundingPolicy"):
            QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
                QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(250, 250, 250))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(52, 152, 219))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(palette)

    win = SphereProjectionVisualizer()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
