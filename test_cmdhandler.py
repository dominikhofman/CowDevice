import pytest
from argparse import ArgumentTypeError
from cmdhandler import *

def test_check_mac_valid_macs():
    macs = ['CE:51:A1:54:4D:36', '52:88:8c:4b:df:b2', 'F5-D7-A3-97-85-80', 'b6-05-13-90-4b-ac']
    for mac in macs:
        assert check_mac(mac) == mac
        
def test_check_mac_not_valid_macs():
    macs = ['Casdad', '5x:88:8c:4b:dp:b2', '88:8c:4b:d3:b2', '888c4bd3b2']
    for mac in macs:
        with pytest.raises(ArgumentTypeError):
            check_mac(mac) 

@pytest.fixture
def error_characteristic():
    from cmdhandler import ErrorCharacteristic
    config = {'uuid': '0000cd07-caa9-44b2-8b43-96ae3072fd36', 'errors': [{'bitmask': 0, 'message': 'BATT'}, {'bitmask': 1, 'message': 'TIMER'}, {'bitmask': 2, 'message': 'GATT'}, {'bitmask': 3, 'message': 'RADIO'}, {'bitmask': 4, 'message': 'MAG'}, {'bitmask': 5, 'message': 'ACC'}, {'bitmask': 6, 'message': 'RTC'}, {'bitmask': 7, 'message': 'SD'}]}
    return ErrorCharacteristic(config)

def test_error_characteristic_value_0(error_characteristic):
    error_characteristic.value = b'\x00'
    assert error_characteristic.value == []

    
def test_error_characteristic_value_25(error_characteristic):
    error_characteristic.value = b'\x25'
    assert error_characteristic.value == ['BATT', 'GATT', 'ACC']
    
def test_error_characteristic_value_ff(error_characteristic):
    error_characteristic.value = b'\xff'
    assert error_characteristic.value == ['BATT', 'TIMER', 'GATT', 'RADIO', 'MAG', 'ACC', 'RTC', 'SD']
