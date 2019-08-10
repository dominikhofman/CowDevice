# CowDevice

Command line tool with autogenerated arguments based on config file

# Installation guide

## 1. Prepare SD card

### Download brand-new raspbian image and unpack it

```bash
wget https://downloads.raspberrypi.org/raspbian_lite_latest -O raspbian.zip
unzip raspbian.zip
```

### Write image to sdcard

```bash
dd if=./xxx.img of=/dev/sdX status=progress
```

### Configure ssh and wifi connection

```bash
# enable ssh
touch /boot/ssh

# configure wifi
# create file /boot/wpa_supplicant.conf and put following content in it

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
     ssid="ssid"
     psk="password"
     key_mgmt=WPA-PSK
}

```

## 2. Setup raspbian

### Increase swap file
If running on Raspberry pi zero its recommended to increase swap size due to not
enough RAM on machine requied for building gattlib.

```bash
sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1000/g' /etc/dphys-swapfile
reboot
```

### Update system and install required tools

```bash
apt-get update && apt-get upgrade -y
apt-get install -y python3-pip git vim
```

### Install bluez dependencies

```bash
apt-get install -y pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev
```

### After reboot clone repo

```bash
git clone https://github.com/dominikhofman/CowDevice.git
```

### Install required python modules

```bash
cd ./CowDevice
# minimal module set for dynamictool.py and masstool.py
pip3 install -r requirements.txt
# additional dependencies required for remote.py
pip3 install -r requirements_remote.txt
# additional dependencies required for running tests
pip3 install -r requirements_test.txt
```

If installing module `pybluez[ble]` fails on building gattlib 
create symbolic link:

```bash
# fix for building gattlib
ln -s /usr/lib/arm-linux-gnueabihf/libboost_python-py35.so /usr/lib/arm-linux-gnueabihf/libboost_python-py34.so
# or
ln -s /usr/lib/arm-linux-gnueabihf/libboost_python3-py37.so /usr/lib/arm-linux-gnueabihf/libboost_python-py34.so
# if libboost_python-py35.so does not exists
```
and try again
## 3. Test if tool works

```bash
# enable bluetooth
echo 'power on' | sudo bluetoothctl

# edit 'MAC' variable in makefile
vim makefile

# write characteristics
make write

# read characteristics
make read
```

in case of not working, try following steps:

```bash
sudo vim /etc/systemd/system/bluetooth.target.wants/bluetooth.service
# replace
ExecStart=/usr/lib/bluetooth/bluetoothd
# with
ExecStart=/usr/lib/bluetooth/bluetoothd -d --compat --noplugin=sap -E


sudo systemctl daemon-reload
sudo service bluetooth restart

run masstool

sudo bluetoothctl
scan on
```

# Usage guide

## Dynamictool usage
For usage documentation please refer to chapter 6 in
[my graduation work](docs/inz.pdf)

## Masstool usage
`Masstool` requires properly configurated `dynamictool`, for usage documentation of `dynamictool` please check point above.

`Masstool` na wejściu otrzymuje
- plik wejściowy z adresami MAC interesujących nas urządzeń
- plik wyjściowy z adresami MAC które zostały już przetworzone
- komenda do uruchomienia dla każdego z urządzeń

plik wejściowy oraz wyjściowy adresy MAC zapisujemy w formacie hexadecymalnym
gdzie poszczególne bajty oddzielone są znakiem "`:`"
przykład:
```
f0:9e:03:36:54:cf
c9:8b:0c:34:0d:56
d1:3d:34:0b:89:5f
```

Podana komenda można użyć znacznika `{mac}` - zostanie on podmieniony na aktualny adres MAC przetwarzanego urządzenia.

Skrypt rozpoczyna działanie od załadowania pliku wejściowego i wyjściowego. Jeżeli
plik wyjściowy nie istnieje to zostanie utworzony nowy pusty plik, jeżeli istnieje to 
zostaną załadowane z niego adresy MAC i te urządzenia będą pomijane w dalszym ciągu programu. Do pliku wyjściowego będą na bierząco dopisywane wpisy z przetworzonymi urządzeniami.

Po załadowaniu plików skrypt zrestartuje moduł bluetooth na urządzeniu i zacznie nasłuchiwanie urządzeń. Gdy skrypt usłyszy adres MAC który jest na liście wejściowej
oraz nie ma na liście wyjściowej to zostanie wykonana komenda podana przy uruchamianiu skryptu. Maksymalny czas na wykonanie komendy określany jest flagą `--timeout` domyślnie wynosi on 30s. Jeżeli wywołana komenda zwróci kod `0` to skrypt uznaje że urządzenie zostało przetworzone, adres MAC zostanie dodany do pliku wyjściowego. W każdym innym przypadku, czyli jeżeli nastąpi timeout lub komenda zwróci kod inny od `0` to skrypt uznaje że przetwarzanie się nie powiodło i wykonanie powtórzy się przy ponownyn pojawieniu się urządzenia w wynikach skanowania.

Skrypt zakończy działanie kiedy zostaną przetworzone wszyskie zadane urządzenia.

Przykład użycia:
```bash
python3 ./masstool.py --devices-to-process ./devices.txt --devices-processed ./devices_done.txt --timeout 30 --cmd "python3 home/pi/CowDeviceMenager/dynamictool.py {mac} --password xxx -s 2 -vvv"
```
Zawartość pliku `./devices.txt`
```
f0:9e:03:36:54:cf
c9:8b:0c:34:0d:56
d1:3d:34:0b:89:5f
```
Zawartość pliku `./devices_done.txt`
```
f0:9e:03:36:54:cf
```
## Remote usage

### 1. Setup host and port for MQTT broker in 'remote.yml' file

example config:

```yml
mqtt_config:
  host: 192.168.1.6 # mqtt broker host
  port: 1883 # mqtt broker port
  name: "" # leave empty ("") to use current hostname
  auto_reconnect: true
  reconnect_delay: 10 # in seconds
  keep_alive: 60 # in seconds
  debug_level: 10 # 10 - debug, 20 - info, 40 - error ### not implemended yet
```

### 2. Run script

```
sudo python3 remote.py
```

Script will subscribe the topic `/inbox/<name>/execute` where \<name> can be specified in remote.yml config file or if left empty will take the current hostname.
To schedule a task you have to publish on the topic above the following json:

```json
{
  // optional, if specified the response would contain this id
  "id": 1234,
  // mac addres of the desired device
  "mac": "ca:2c:83:fe:72:48",
  // arguments passed to dynamictool.py, for available arguments run python3 dynamictool.py --help
  "args": "-r",
  // optional password for granting write privilage on password prottected characteristics
  "password": "2"
}
```

After task completion the response would be published on the topic `/outbox/<name>/execute`. Example response:

```json
{
  // the id of corresponding request, would be generated if not specified in request
  "id": 1234,
  // the stderr generated by dynamictool.py
  "stderr": "",
  // the stdout generated by dynamictool.py
  "stdout": "tx_power: 4\ntime: 03:47:31\nled: 0\ndate: 14/10/20\nswitch: 2\nadv_interval: 250\nerror: ['SD']\n",
  // the return code of dynamictool.py
  "returncode": 0
}
```

### 3. Example

Lets say that we want to set `date`, `time`, `tx_power` and turn `led` on for device with mac `aa:bb:cc:dd:ee:ff` protected with password `pass123`. To acomplish that we would use the following command:

```
sudo dynamictool.py aa:bb:cc:dd:ee:ff --date 29/04/19 --time 04:20:00 --txpower 4 --led 1 --password pass123
```

The equivalent of above command would be publishing the following json on `/inbox/<name>/execute` topic

```json
{
  "id": 2137,
  "mac": "aa:bb:cc:dd:ee:ff",
  "args": "--date 29/04/19 --time 04:20:00 --txpower 4 --led 1",
  "password": "pass123"
}
```

If everything went good we should receive response on `/outbox/<name>/execute` topic

```json
{ "id": 2137, "stderr": "", "stdout": "", "returncode": 0 }
```

### 4. Returncodes

The `returncode` key in response describes the status of ended task

- returncode > 0 - error happend in dynamictool.py
- returncode == 0 - it ok my son
- returncode < 0 - error happend in remote.py
