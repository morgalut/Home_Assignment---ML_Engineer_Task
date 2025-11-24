import pytest
from app.utils.ip_validator import validate_ip

def test_valid_public_ip():
    assert validate_ip("8.8.8.8") is True

def test_private_ip():
    assert validate_ip("192.168.0.1") is False

def test_loopback_ip():
    assert validate_ip("127.0.0.1") is False

def test_invalid_ip_format():
    assert validate_ip("999.999.999.999") is False

def test_reserved_ip():
    assert validate_ip("240.0.0.1") is False
