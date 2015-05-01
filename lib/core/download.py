#!/usr/bin/env python
# coding: utf-8

import os
import re
import requests

from lxml import html
from urlparse import urljoin
from random import choice

from lib.core.logger import logger
from lib.utils.common import init_proxy


download_link = 'http://beebeeto.com/download/pdb/%s/'
module_path = os.path.join(os.path.split(__file__)[0], '../../modules/')

_ID_REGEX = r'^poc-\d{4}-\d{4}$'
_KEYWORDS = 'class MyPoc'


def parse_page_from_content(content, crawl_dic):
    url = 'http://beebeeto.com/pdb/'
    new_crawl_dic = crawl_dic
    try:
        doc = html.document_fromstring(content)
    except Exception, e:
        return new_crawl_dic

    pre_page_urls = doc.xpath('//div[@style="text-align: right;"]/a/@href')
    if pre_page_urls:
        pre_page_urls = [urljoin(url, page_url) for page_url in pre_page_urls]

        for page_url in pre_page_urls:
            if not new_crawl_dic.has_key(page_url):
                new_crawl_dic[page_url] = False

        return new_crawl_dic


def parse_poc_id_from_content(content):
    ids = None
    try:
        doc = html.document_fromstring(content)
    except Exception, e:
        return ids

    ids = []
    pre_links = doc.xpath('//tbody//a/@href')
    if pre_links:
        for pre_link in pre_links:
            item = re.search(r'(?P<poc_id>poc-\d{4}-\d{4})', pre_link)
            if item:
                poc_id = item.group('poc_id')
                ids.append(poc_id)

        return ids


def download_poc(poc_id, cookie):
    link = download_link % poc_id
    try:
        poc_file = requests.get(link, headers={'Cookie': cookie} if cookie else None, timeout=10)
    except Exception:
        logger.error('Download "%s" [Failed] (Connection Error)' % poc_id)
        return

    if _KEYWORDS not in poc_file.content:
        logger.error('Download "%s" [Failed] (Permission denied or POC not exist)' % poc_id)
        return

    ext = '.py'
    restore_path = module_path + poc_id.replace('-', '_') + ext
    open(restore_path, 'wb').write(poc_file.content)
    logger.critical('Download "%s" [Success]' % poc_id)


def download_work(args):
    if args.PROXY:
        init_proxy(args.PROXY)

    cookie = args.COOKIE if args.COOKIE else None

    if args.poc != 'all':
        poc_id = args.poc
        if not re.search(_ID_REGEX, poc_id):
            logger.error('Error format on poc id, please reinput.')
        else:
            download_poc(poc_id, cookie)
    else:
        logger.info('Download all pocs from "beebeeto.com"')
        logger.warning('PoC existed will be overwrite, type [Enter] to continue.')
        raw_input()
        if True:
            crawl_dic = {'http://beebeeto.com/pdb/?page=1': False}

            while False in crawl_dic.values():
                crawl_url = choice([link for link, crawled in crawl_dic.items() if not crawled])

                try:
                    content = requests.get(crawl_url).content
                    crawl_dic[crawl_url] = True
                except Exception, e:
                    logger.error('Exception occured "%s" (%s)' % (Exception, e))
                    break

                if content:
                    crawl_dic = parse_page_from_content(content, crawl_dic)

                    ids = parse_poc_id_from_content(content)
                    for poc_id in ids:
                        download_poc(poc_id, cookie)
        else:
            logger.info('Download cancel.')
            return
