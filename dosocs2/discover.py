import importlib
import os
import pkgutil
from . import scanners

def discover():
    path = os.path.dirname(scanners.__file__)
    scanner_names = [name for _, name, _ in pkgutil.iter_modules([path])]
    modules = (
        importlib.import_module('.' + name, __package__ + '.' + 'scanners')
        for name in scanner_names
        )
    return {
        mod.scanner.name: mod.scanner
        for mod in modules
        }
