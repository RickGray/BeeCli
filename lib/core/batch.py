#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import threadpool

try:
    import simplejson as json
except ImportError:
    import json


from gevent import monkey
monkey.patch_socket()

from copy import deepcopy

from lib.core.logger import logger
from lib.utils.common import init_proxy, normalize_url
from lib.utils.common import import_module_with_path, import_all_modules_with_dirname


_default_module_path = os.path.join(os.path.split(__file__)[0], '../../modules/')


class BatchTest(object):
    default_options = {
        'target': None,
        'verify': True,
        'verbose': False,
    }

    def __init__(self, funcs2run, seed_file, options=None,
                 result_file='result.txt', thread_num=50, verbose=True):
        self.funcs2run = funcs2run if isinstance(funcs2run, list) else [funcs2run]
        self.options = options if options else self.default_options
        self.seed_targets = open(seed_file, 'rb').readlines()

        self.total_num = 0
        self.success_num = 0

        self.tp = threadpool.ThreadPool(num_workers=thread_num)

        self.result_fobj = open(result_file, 'wb')

    def handle_result(self, request, result):
        result = deepcopy(request.args[0])
        if result['success']:
            self.success_num += 1
            logger.critical('Target: %s [Success] (%s)'
                            % (request.args[0]['options']['target'], result['poc_name']))
        else:
            logger.error('Target: %s [Failed] (%s)'
                         % (request.args[0]['options']['target'], result['poc_name']))
        self.result_fobj.write(json.dumps(result) + '\n')

    def start(self, norm_target_func=None, *args, **kwargs):

        def args_generator(poc_name):
            func_args = {
                'poc_name': poc_name,
                'options': self.options,
                'success': None,
                'poc_ret': {},
            }
            for target in self.seed_targets:
                if norm_target_func:
                    func_args['options']['target'] = norm_target_func(target.strip(), *args, **kwargs)
                else:
                    func_args['options']['target'] = target.strip()
                yield deepcopy(func_args)

        for name, func2run in self.funcs2run:
            requests = threadpool.makeRequests(callable_=func2run,
                                               args_list=args_generator(name),
                                               callback=self.handle_result,
                                               exc_callback=self.handle_result)

            [self.tp.putRequest(req) for req in requests]
            self.total_num += requests.__len__()

        self.tp.wait()
        self.tp.dismissWorkers(100, do_join=True)
        return self.total_num, self.success_num


def batch_work(args):
    if args.METHOD not in ['verify', 'exploit']:
        logger.error('Error method, please check out...')
        sys.exit()

    if args.PROXY:
        init_proxy(args.PROXY)

    if args.poc != 'all':
        poc = import_module_with_path(args.poc)
        funcs = (poc.__name__, (poc.MyPoc.verify if args.METHOD == 'verify' else poc.MyPoc.exploit))
        outfile = 'batch_%s_result_' % args.METHOD + os.path.splitext(os.path.basename(args.poc))[0] + '.txt'

        logger.info('Batch startting with "%s"' % ('verify' if args.METHOD == 'verify' else 'exploit'))
        start_time = time.time()
        bt = BatchTest(seed_file=args.targets,
                       funcs2run=funcs,
                       result_file=outfile,
                       thread_num=args.THREADS,
                       verbose=False)

        bt.start(norm_target_func=normalize_url)
        logger.info('total number: %d, success number: %d, failed number: %d'
                    % (bt.total_num, bt.success_num, (bt.total_num - bt.success_num)))
        logger.info('cost %f seconds.' % (time.time() - start_time))
    else:
        # Add
        path = args.MODULE_DIR
        module_path = _default_module_path if not path else os.path.expanduser(path)
        pocs = import_all_modules_with_dirname(module_path)
        funcs = [(poc.__name__, poc.MyPoc.verify if args.METHOD == 'verify' else poc.MyPoc.exploit) for poc in pocs]
        outfile = 'batch_%s_result_all' % args.METHOD + '.txt'

        logger.info('Batch all startting with "%s"' % ('verify' if args.METHOD == 'verify' else 'exploit'))

        start_time = time.time()
        bt = BatchTest(seed_file=args.targets,
                       funcs2run=funcs,
                       result_file=outfile,
                       thread_num=args.THREADS,
                       verbose=False)

        bt.start(norm_target_func=normalize_url)
        logger.info('total number: %d, success number: %d, failed number: %d'
                    % (bt.total_num, bt.success_num, (bt.total_num - bt.success_num)))
        logger.info('cost %f seconds.' % (time.time() - start_time))
