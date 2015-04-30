#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import socks
import socket

from urlparse import urlparse

from lib.core.logger import logger


_FILTER_MODULES = ['__init__.py', 'baseframe.py']


def normalize_url(url, https=False):
    if not url:
        return
    elif url.startswith(('http://', 'https://')):
        return url
    if not https:
        url = 'http://' + url
    else:
        url = 'https://' + url
    return url


def init_proxy(proxy):
    res = urlparse(proxy)

    use_proxy = True
    if res.scheme == 'socks4':
        mode = socks.SOCKS4
    elif res.scheme == 'socks5':
        mode = socks.SOCKS5
    elif res.scheme == 'http':
        mode = socks.HTTP
    else:
        use_proxy = False
        logger.warning('Unknown proxy "%s", starting without proxy...' % proxy)

    if use_proxy:
        socks.set_default_proxy(mode, res.netloc.split(':')[0], int(res.netloc.split(':')[1]))
        socket.socket = socks.socksocket
        logger.info('Proxy "%s" using' % proxy)


def import_module_with_path(path):
    abspath = os.path.abspath(os.path.expanduser(path))
    dirpath, filename = os.path.split(abspath)

    if dirpath not in sys.path:
        sys.path.insert(0, dirpath)

    module_name, ext = os.path.splitext(filename)
    try:
        return __import__(module_name, fromlist=['*'])
    except ImportError:
        raise ImportError('Error on import "%s"' % abspath)
    except Exception, e:
        raise Exception('Error on import "%s" [%s]' % (abspath, e))


def import_all_modules_with_dirname(dirpath, pattern=r'(?P<filename>^.+\.py$)'):
    absdirpath = os.path.abspath(os.path.expanduser(dirpath))
    filenames = os.listdir(absdirpath)
    matchs = []

    for filename in filenames:
        match = re.search(pattern, filename)
        if match:
            if match.group('filename') not in _FILTER_MODULES:
                module_path = os.path.join(absdirpath, match.group('filename'))
                matchs.append(module_path)

    return [import_module_with_path(path) for path in matchs]
