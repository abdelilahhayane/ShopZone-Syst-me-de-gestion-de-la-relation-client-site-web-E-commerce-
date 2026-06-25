# Configure PyMySQL as MySQLdb for Django with Python 3.13+
import pymysql
import sys

# Set the required version for Django 6.0
pymysql.version_info = (2, 2, 1)
pymysql.__version__ = '2.2.1'

pymysql.install_as_MySQLdb()

# Fix for Python 3.14 compatibility with Django 4.2
# https://code.djangoproject.com/ticket/35879
import copy
from django.template.context import RenderContext

# Monkeypatch for Python 3.14 compatibility
original_copy = copy.copy

def patched_copy(x):
    if isinstance(x, RenderContext):
        # Create a shallow copy without using __copy__
        new_context = RenderContext()
        new_context.dicts = x.dicts[:]
        return new_context
    return original_copy(x)

copy.copy = patched_copy