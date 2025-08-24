# VaCPA

*VaCPA's a Curvilinear Perspective Assistant.*

VaCPA is in a very early stage of development; expect few features and many changes.

## To Do List

- Bundle independent of a Python install
- A banner on this page
- Cross-platform builds
- More beautiful UI
- Image overlays on guidelines
- Exports and imports for parameters
- And more...

## Build

After installing all Python dependencies:

```
pyinstaller src/main.py --name curvilinear --windowed --collect-all pyqtgraph --hidden-import pyqtgraph.opengl --icon icon.ico
```