import socket

import pytest


@pytest.fixture(autouse=True)
def prohibit_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Unit tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
