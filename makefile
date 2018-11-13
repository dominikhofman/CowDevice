MAC = ca:2c:83:fe:72:48

all:
	sudo python3 dynamictool.py $(MAC) -r

help:
	python3 dynamictool.py --help

ledon:
	sudo python3 dynamictool.py $(MAC) -l 1

ledoff:
	sudo python3 dynamictool.py $(MAC) -l 0
	
read:
	sudo python3 dynamictool.py $(MAC) -r -vvv

write:
	sudo python3 dynamictool.py $(MAC) --password 2 -l 1 -t 04:23:55 -d 10/10/20 -p 4 -a 500 -s 2 -vvv

test:
	python3 -m pytest
