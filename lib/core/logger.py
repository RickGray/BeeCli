#!/usr/bin/env python
# coding: utf-8

import logging

from logging.handlers import RotatingFileHandler

from termcolor import colored


class StreamFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: colored('[D] %(message)s', 'blue'),
        logging.INFO: colored('[*] %(message)s', 'white'),
        logging.WARNING: colored('[!] %(message)s', 'yellow'),
        logging.ERROR: colored('[-] %(message)s', 'red'),
        logging.CRITICAL: colored('[+] %(message)s', 'green'),
        'DEFAULT': '%(asctime)s %(message)s'
    }

    def __init__(self):
        logging.Formatter.__init__(self)

        self.datefmt = '%Y-%m-%d(%H:%M:%S)'

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


class FileFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: '%(asctime)s %(message)s',
        logging.INFO: '%(asctime)s %(message)s',
        logging.WARNING: '%(asctime)s %(message)s',
        logging.ERROR: '%(asctime)s %(message)s',
        logging.CRITICAL: '%(asctime)s %(message)s',
        'DEFAULT': '%(asctime)s %(message)s'
    }

    def __init__(self):
        logging.Formatter.__init__(self)

        self.datefmt = '%Y-%m-%d(%H:%M:%S)'

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


#base_path = '~/.bee/'

#log_path = 'bee.log'

#file_handler = RotatingFileHandler(log_path, mode='a', maxBytes=5*1024*1024)
#file_handler.setFormatter(FileFormatter())

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(StreamFormatter())

logger = logging.getLogger('log')
logger.addHandler(stream_handler)
#logger.addHandler(file_handler)

logger.setLevel(logging.INFO)
stream_handler.setLevel(logging.INFO)
#file_handler.setLevel(logging.DEBUG)
