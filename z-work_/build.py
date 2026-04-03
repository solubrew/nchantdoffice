




# Ubuntu/Debian
sudo apt-get install build-essential cmake ninja-build python3-dev
sudo apt-get install libfontconfig1-dev libfreetype6-dev libx11-dev
sudo apt-get install libxext-dev libxfixes-dev libxi-dev libxrender-dev
sudo apt-get install libxcb1-dev libx11-xcb-dev libxcb-glx0-dev
sudo apt-get install libxkbcommon-x11-dev libxcb-keysyms1-dev
sudo apt-get install libxcb-image0-dev libxcb-shm0-dev libxcb-icccm4-dev
sudo apt-get install libxcb-sync-dev libxcb-xfixes0-dev libxcb-shape0-dev
sudo apt-get install libxcb-randr0-dev libxcb-render-util0-dev
sudo apt-get install libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev
sudo apt-get install libxkbcommon-dev libxkbcommon-x11-dev



# Clone Qt6 source
git clone --recursive https://code.qt.io/qt/qt5.git qt6-source
cd qt6-source
git checkout 6.7  # or latest stable version

# Clone PySide6 source separately
git clone --recursive https://code.qt.io/pyside/pyside-setup.git
cd pyside-setup
git checkout 6.7  # match Qt version





- `-webengine-proprietary-codecs`: Enables H.264/H.265 support
- `-webengine-ffmpeg`: Uses system FFmpeg
- `-webengine-pepper-plugins`: Enables Flash support
- `-webengine-printing-and-pdf`: PDF support
