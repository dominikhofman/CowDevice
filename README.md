$pip wheel --wheel-dir=/tmp/wheelhouse SomePackage$ pip install --no-index --find-links=/tmp/wheelhouse SomePackage
https://pip.pypa.io/en/stable/reference/pip_wheel/

raspbian stretch xxx
apt-get update && apt-get upgrade -y
apt-get install -y python3-pip

# increase swap file

sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1000/g' /etc/dphys-swapfile
sudo reboot

#instal
