__title__ = 'yup'
__author__ = 'Nathan Ostgard'
__license__ = 'MIT'

from ._version import __version__
from .document import (Document, Request, RequestExample, RequestParam,
                       iter_all, load_all)
from .render import render_all

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
