mac = ca:2c:83:fe:72:48
all:
	sudo python3 dynamictool.py $(mac) -r

help:
	python3 dynamictool.py --help

ledon:
	sudo python3 dynamictool.py $(mac) -l 1

ledoff:
	sudo python3 dynamictool.py $(mac) -l 0
	
read:
	sudo python3 dynamictool.py $(mac) -r

write:
	sudo python3 dynamictool.py $(mac) --password 2 -l 1 -t 04:23:55 -d 10/10/20 -p 4 -a 250 -s 2
test:
	python3 -m pytest
