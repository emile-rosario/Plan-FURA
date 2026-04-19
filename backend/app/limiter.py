"""
Rate limiter compartido — Funeraria Rancier
Instancia única de slowapi para usar en todos los routers.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
