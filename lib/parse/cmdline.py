#!/usr/bin/env python
# coding: utf-8

import argparse


banner = r'''
 __ )             ___|                        |
 __ \   _ \  _ \ |      _ \  __ \   __|  _ \  |  _ \
 |   |  __/  __/ |     (   | |   |\__ \ (   | |  __/
____/ \___|\___|\____|\___/ _|  _|____/\___/ _|\___|

    Author: rickchen.vip@gmail.com   |
      Date: 2015-04-23               |
   Version: v0.0.1                   |
_____________________________________|
'''


def parse_argv():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='sub-command help', dest='mode')

    # Download Arguments
    download_parser = subparsers.add_parser('download', help='download poc from beebeeto.com')
    download_parser.add_argument('--cookie', dest='COOKIE', type=str,
                                 help='use a login cookie to download some sepecial poc')
    download_parser.add_argument('--proxy', dest='PROXY', type=str,
                              help='use a proxy to connect target (support: http,socks4,socks5)')
    download_parser.add_argument('poc', type=str, help='poc id (e.g. poc-2015-0086) or you can type all to fetch all')

    # Search Arguments
    search_parser = subparsers.add_parser('search', help='search poc you want with some keyword')
    search_parser.add_argument('keyword', type=str, help='keyword (e.g. Discuz, MacCMS, ...)')

    # Fetch Arguments
    fetch_parser = subparsers.add_parser('fetch', help='fetch targets from google or other search engine')
    fetch_parser.add_argument('-q', dest='QUIET', action='store_true', default=False,
                              help='be quiet when search processing')
    fetch_parser.add_argument('-o', dest='OUTFILE', type=str,
                              help='outfile results to given filename')
    fetch_parser.add_argument('--proxy', dest='PROXY', type=str,
                              help='use a proxy to connect target (support: http,socks4,socks5)')
    fetch_parser.add_argument('query', type=str, help='the dork or something you want to search')

    # Batch Arguments
    batch_parser = subparsers.add_parser('batch', help='batch scan with file include targets')
    batch_parser.add_argument('-m', '--mode', dest='METHOD', type=str, choices=['verify', 'exploit'],
                              help='verify or exploit mode to use (default: "verify")')
    batch_parser.add_argument('--threads', dest='THREADS', type=int, default=50,
                              help='max number of threads to batch (default 50)')
    batch_parser.add_argument('--proxy', dest='PROXY', type=str,
                              help='use a proxy to connect target (support: http,socks4,socks5)')
    batch_parser.add_argument('poc', type=str, help='poc file to batch')
    batch_parser.add_argument('targets', type=str, help='file within targets')

    return parser.parse_args()
