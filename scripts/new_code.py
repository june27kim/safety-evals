#!/usr/bin/env python3
"""Вывести криптографически случайный ID (192 бита). Только стандартная библиотека."""
import secrets
print(secrets.token_urlsafe(24))
