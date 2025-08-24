# VaCPA

*VaCPA's a Curvilinear Perspective Assistant.*

VaCPA is in a very early stage of development; expect few features and many changes.

## Anricipated features

- A bannar on this page
- Cross-platform builds
- More beautiful UI
- Ability to overlay image on guidelines
- Ability to export and restore past parameters
- And more...

## Build

After installing all Python dependencies:

```
pyinstaller src/main.py --name curvilinear --windowed --collect-all pyqtgraph --hidden-import pyqtgraph.opengl --icon icon.ico
```