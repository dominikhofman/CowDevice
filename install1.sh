
apt-get update && apt-get upgrade -y && \
apt-get install -y python3-pip git vim && \
apt-get install -y pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev && \
ln -s /usr/lib/arm-linux-gnueabihf/libboost_python-py35.so /usr/lib/arm-linux-gnueabihf/libboost_python-py34.so && \
sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1000/g' /etc/dphys-swapfile