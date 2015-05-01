#!/usr/bin/env python
# coding: utf-8

from lib.parse.cmdline import parse_argv, banner

from lib.core.fetch import fetch_work
from lib.core.search import search_work
from lib.core.batch import batch_work
from lib.core.download import download_work


if __name__ == '__main__':
    print banner
    args = parse_argv()

    import signal, sys

    def signal_handler(sig, frame):
        print 'Detected ctrl+c, exit...'
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if args.mode == 'download':
        download_work(args)
    elif args.mode == 'search':
        search_work(args)
    elif args.mode == 'fetch':
        fetch_work(args)
    elif args.mode == 'batch':
        batch_work(args)
