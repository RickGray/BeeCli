#!/usr/bin/env python
# coding: utf-8

import re
import sys
from urlparse import urlparse, urljoin

import requests
from lxml import html

from lib.core.logger import logger
from lib.utils.common import init_proxy


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36',
}


class CaptcheProcessError(Exception):
    pass


class GoogleSearchInitError(Exception):
    pass


class GoogleSearchLimitError(Exception):
    pass


class Google(object):
    def __init__(self, host='https://www.google.com', headers=None, timeout=60, debug_mode=False):
        self.host = host
        self.headers = default_headers
        if isinstance(headers, dict):
            self.headers.update(headers)
        self.timeout = timeout
        self.request = requests.session()

        self.debug = debug_mode

        self._init()

    def _init(self):
        try:
            _ = self.request.get(self.host, headers=self.headers, allow_redirects=False, timeout=self.timeout)
        except Exception, e:
            raise GoogleSearchInitError('ConnectionError with "%s"' % self.host)

        if _.status_code == 302:
            self._redirect_process(_)

    def _redirect_process(self, response):
        location = response.headers['location']
        if 'sorry' not in location:
            host = urlparse(location).scheme + '://' + urlparse(location).netloc
            self.host = host

            if self.debug:
                logger.warning('Host redirect detected: "%s"' % self.host)
                logger.info('New host(%s) useed' % self.host)
        elif 'sorry' in location:
            if self.debug:
                logger.warning('Captche verify detected, cant load plugin to process...')
                logger.warning('Exit...')

            sys.exit()

    def search(self, word, page_num=100, start=0):
        if start > 1000:
            raise GoogleSearchLimitError('Google search only limit the reuslts no more than 1000')

        search_url = urljoin(self.host, '/search?gws_rd=ssl&q=%s&num=%s&start=%s&safe=off&filter=0'
                             % (str(word), str(page_num), str(start)))
        response = self.request.get(search_url, headers=self.headers, allow_redirects=False, timeout=self.timeout)
        if response.status_code == 302:
            self._redirect_process(response)
            return None

        return response.content

    def access(self, next_url):
        next_url = urljoin(self.host, next_url)
        response = self.request.get(next_url, headers=self.headers, allow_redirects=False, timeout=self.timeout)
        if response.status_code == 302:
            self._redirect_process(response)
            return None

        return response.content

    def fetch_results(self, query):
        url_collection = []
        #host_collection = []

        start = 0
        logger.info('Starting search with google: %s' % query)
        logger.warning('You can interrupt this process with [Ctrl+c]')

        next_url = None
        while True:
            try:
                if next_url:
                    content = self.access(next_url)
                else:
                    content = self.search(query, page_num=100, start=start)
            except GoogleSearchLimitError, e:
                logger.error('%s' % e)
                return url_collection
            except GoogleSearchInitError, e:
                logger.error('%s' % e)
                return url_collection
            except KeyboardInterrupt, e:
                return url_collection
            except Exception, e:
                continue

            if content:
                next_url = parse_next_url_from_content(content)

                temp_urls = parse_url_from_content(content)
                if len(temp_urls) > 0:
                    url_collection.extend(temp_urls)
                    logger.info('Catched %d results currently' % url_collection.__len__())

                    start += 100
                else:
                    logger.warning('No more results found, mo longer continue to search')
                    return url_collection

                if not next_url:
                    logger.warning('No more results found, no longer continue to search')
                    return url_collection


def fetch_work(args):
    if args.PROXY:
        init_proxy(args.PROXY)

    debug = False if args.QUIET else True
    outfile = args.OUTFILE
    query = args.query

    google = Google(debug_mode=debug)
    urls = google.fetch_results(query)

    quit_process(outfile, urls)


def parse_url_from_content(content):
    urls = []
    try:
        doc = html.document_fromstring(content)
    except Exception, e:
        return urls

    pre_urls = doc.xpath('//div[@id="ires"]/ol/div[@class="srg"]/li[@class="g"]/div[@class="rc"]/h3/a/@href')
    if pre_urls:
        for url in pre_urls:
            m = re.findall(r'http[s]?://([^&/?]*/??)', url)
            if m:
                urls.append(m[0])

    return urls


def parse_hosts_from_urls(urls):
    hosts = []

    urls = list(urls) if isinstance(urls, str) else urls
    for url in urls:
        m = re.findall(r'http[s]?://([^&/?]*)/??', url)
        if m:
            hosts.append(m[0])

    return hosts


def parse_next_url_from_content(content):
    next_url = None
    try:
        doc = html.document_fromstring(content)
    except Exception, e:
        return next_url

    pre_next_urls = doc.xpath('//a[@id="pnnext"]/@href')
    if pre_next_urls:
        next_url = pre_next_urls[0]

    return next_url


def quit_process(filename, results):
    logger.info('Processing results...')
    pre_num = results.__len__()
    results = {}.fromkeys(results).keys()
    num = results.__len__()

    if filename:
        save_results(filename, results)
        logger.info('Save results to "%s" finished' % filename)
    else:
        for r in results:
            print r

    logger.info('All: %d, Non-duplication: %d' % (pre_num, num))


def save_results(filename, results):
    with open(filename, 'w') as f:
        for r in results:
            f.write(r + '\n')
