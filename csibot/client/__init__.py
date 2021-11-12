from .client import Client
import urllib3.util.connection as urllib3_cn
import socket


# Force to use IPv4
urllib3_cn.allowed_gai_family = lambda: socket.AF_INET


__all__ = ['Client']
