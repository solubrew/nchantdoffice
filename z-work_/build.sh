cd qt6-source
mkdir build
cd build

# Configure Qt6 with WebEngine and proprietary codecs
../configure -prefix /opt/qt6-custom \
             -release \
             -shared \
             -webengine-proprietary-codecs \
             -webengine-pepper-plugins \
             -webengine-printing-and-pdf \
             -webengine-spellchecker \
             -nomake examples \
             -nomake tests