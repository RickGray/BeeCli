#!/usr/bin/env python
# coding: utf-8

import os
import re

from lib.core.logger import logger
from lib.utils.common import import_all_modules_with_dirname


_default_module_path = os.path.join(os.path.split(__file__)[0], '../../modules/')


class SearchPoC(object):
    def __init__(self, keyword, path=None):
        self.keyword = keyword

        self._modules = None
        self._module_path = _default_module_path if not path else os.path.expanduser(path)

        self._load_all_modules()

    def _load_all_modules(self):
        pocs = import_all_modules_with_dirname(self._module_path)

        self._modules = [(poc.__name__, poc) for poc in pocs]

    def search(self):
        results = {}
        if self._modules:
            for name, module in self._modules:
                try:
                    poc_info = module.MyPoc.poc_info
                except Exception:
                    logger.debug('Get "%s" poc_info failed' % name)
                    continue

                poc_desc = poc_info['poc']
                if re.search(self.keyword, poc_desc['name'], re.I):
                    results[name] = poc_desc['name']

        return results


def search_work(args):
    repi = SearchPoC(args.keyword, path=args.PATH)
    res = repi.search()

    for key, value in res.items():
        logger.info('%s    %s' % (key, value))
