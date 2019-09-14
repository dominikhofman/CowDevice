#!/bin/bash

# this scirpt should be run prior to dynamictool.py or masstool.py

btmgmt -i 0 power off
btmgmt -i 0 le on
btmgmt -i 0 connectable off
btmgmt -i 0 power on

echo 'Configured bluetooth successfully!'
