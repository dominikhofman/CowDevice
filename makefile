MAC = ca:2c:83:fe:72:48
PASSWORD = 2
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
	sudo python3 dynamictool.py $(MAC) --password $(PASSWORD) -l 1 -t 04:23:55 -d 10/10/20 -p 4 -a 250 -s 2 $(VERBOSITY)

discover:
	sudo gattctl --discover

test:
	python3 -m pytest
