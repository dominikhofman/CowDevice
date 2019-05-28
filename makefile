#MAC = fd:e7:e0:f3:c9:f7
MAC = d2:67:fb:0c:fc:22 
PASSWORD = .Mafiozo\#102.
VERBOSITY = -vvv

all:
	sudo python3 dynamictool.py $(MAC) -r

help:
	python3 dynamictool.py --help

ledon:
	sudo python3 dynamictool.py $(MAC) -l 1

ledoff:
	sudo python3 dynamictool.py $(MAC) -l 0
	
read:
	sudo python3 dynamictool.py $(MAC) -r $(VERBOSITY)

write:
	sudo python3 dynamictool.py $(MAC) --password $(PASSWORD) -l 1 $(VERBOSITY)
#	sudo python3 dynamictool.py $(MAC) --password $(PASSWORD) -l 1 -t 04:23:55 -d 10/10/20 -p 4 -a 250 -s 2 $(VERBOSITY)

discover:
	sudo gattctl --discover

test:
	python3 -m pytest

mass:
	python3 ./masstool.py --devices-to-process ./devices.txt --devices-processed ./devices_done.txt --timeout 30 \
		--cmd "python3 /home/pi/gatt/dynamictool.py {mac} -r -vvv"
		# --cmd "python3 /home/pi/gatt/dynamictool.py {mac} --led 1 -vvv"
		# --cmd "python3 /home/pi/gatt/dynamictool.py {mac} -r -vvv"
#		--cmd "python3 /home/pi/gatt/dynamictool.py {mac} --password .Mafiozo#102. -s 1 -vvv"
	# --cmd "bash /home/pi/gatt/device_cmd.sh {mac}"