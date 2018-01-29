# -*- coding: utf-8 -*-
from __future__ import absolute_import

import bpdb
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem
from ..items import PdfItem

import Cookie

import re

class RepositoryVnuEduVn(BasePortiaSpider):
    name = "repository.vnu.edu.vn"
    allowed_domains = [u'repository.vnu.edu.vn']
    # start_urls = ["http://repository.vnu.edu.vn/handle/VNU_123/17745?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17746?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17747?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17748?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17749?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17750?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17751?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17752?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17753?offset=0",
    #               "http://repository.vnu.edu.vn/handle/VNU_123/17754?offset=0"]
    start_urls = ["http://repository.vnu.edu.vn/handle/VNU_123/60487"]
    rules = [
        Rule(
            LinkExtractor(
                allow=('.*handle/VNU_123/[0-9]+\?offset=[0-9]+$'),
                deny=('http://repository.vnu.edu.vn/handle/VNU_123/17744',
                      'http://repository.vnu.edu.vn/handle/VNU_123/296'
                )
            ),
            callback='parse_page',
            follow=False
        ),
        Rule(
            LinkExtractor(
                allow=('^.*ViewOnline\?bitstid=.*$'),
                deny=()
            ),
            callback='parse_pdf',
            follow=False
        ),
        Rule(
            LinkExtractor(
                allow=('.*handle/VNU_123/[0-9]+$'),
                deny=('http://repository.vnu.edu.vn/handle/VNU_123/17744',
                      'http://repository.vnu.edu.vn/handle/VNU_123/296'
                )
            ),
            callback='parse_item',
            follow=False,
        )
    ]
    items = [
        [
            Item(
                PortiaItem,
                None,
                u'.container:nth-child(4)',
                [
                    Field(
                        u'title',
                        "//tr[contains(.,'Title:')]/td[@class='metadataFieldValue']/text()",
                        # '.table > tr:nth-child(1) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(1) > .metadataFieldValue *::text',
                        [],
                        True,
                        'xpath'),
                    Field(
                        u'authors',
                        "//tr[contains(.,'Authors:')]/td[@class='metadataFieldValue']/*/text()",
                        # '.table > tr:nth-child(2) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(2) > .metadataFieldValue *::text',
                        [],
                        type='xpath'),
                    Field(
                        u'keywords',
                        "//tr[contains(.,'Keywords:')]/td[@class='metadataFieldValue']/text()",
                        # '.table > tr:nth-child(3) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(3) > .metadataFieldValue *::text',
                        [],
                        type='xpath'),
                    Field(
                        u'date',
                        "//tr[contains(.,' Date:')]/td[@class='metadataFieldValue']/text()",
                        # '.table > tr:nth-child(4) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(4) > .metadataFieldValue *::text',
                        [],
                        type='xpath'),
                    Field(
                        u'publisher',
                        "//tr[contains(.,'Publisher:')]/td[@class='metadataFieldValue']/text()",
                        # '.table > tr:nth-child(5) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(5) > .metadataFieldValue *::text',
                        [],
                        type='xpath'),
                    Field(
                        u'desc',
                        "//tr[contains(.,'Description:')]/td[@class='metadataFieldValue']/text()",
                        # '.table > tr:nth-child(6) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(6) > .metadataFieldValue *::text',
                        [],
                        type='xpath'),
                    Field(
                        u'uri',
                        "//tr[contains(.,'URI:')]/td[@class='metadataFieldValue']/*/text()",
                        # '.table > tr:nth-child(7) > .metadataFieldValue > a::attr(href), .table > tbody > tr:nth-child(7) > .metadataFieldValue > a::attr(href)',
                        [],
                        type='xpath'),
                    Field(
                        u'collection',
                        "//tr[contains(.,'Collections:')]/td[@class='metadataFieldValue']/a/text()",
                        # '.table > tr:nth-child(8) > .metadataFieldValue *::text, .table > tbody > tr:nth-child(8) > .metadataFieldValue *::text',
                        [],
                        True,
                        type='xpath'),
                    Field(
                        u'view_url',
                        "//a[contains(@href,'/ViewOnline?bitstid')]/@href",
                        # '.panel > div:nth-child(5) > .standard > .btn-info::attr(href)',
                        [],
                        type='xpath')])]]

    def parse_page(self, response):
        if '(LIC)' not in response.body:
            return

        urls = response.css('.table a::attr(href)').extract()
        for each in urls:
            if re.match('.*handle/VNU_123/[0-9]+$', each):
                yield Request('http://repository.vnu.edu.vn' + each, self.parse_item)

    def parse_pdf(self, r):
        s = Cookie.SimpleCookie()
        bpdb.set_trace()
        s.load(r.headers['Set-Cookie'])

        cookie = {}
        for k, v in s.items():
            cookie[k] = v.value

        print('=====================================================================')
        cookie_header = {'Cookie': ",".join([k + "=" + v for k, v in cookie.items()])}
        print(cookie_header)
        print('=====================================================================')
        yield Request("http://repository.vnu.edu.vn/ViewOnline/pdfjs/web/viewer.jsp", cookies=cookie, callback=self.parse_real_pdf, meta={'view_url': r.url, 'dont_cache': True})

        # TODO change url article mapping to pdfs
    def parse_real_pdf(self, r):
        print('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
        print(r.body)
        item = PdfItem()

        m = re.search(r'/ViewOnline/pdf/([0-9]+)', r.body)
        if m:
            item.files_url =  m.group(0)
            item.article_id = r.meta['view_url']
            yield item

    # def filter_item(self, response):
    #     return response


    # def parse_item(self, response):
    #     if '(LIC)' not in response.body:
    #         print("=============================================================")
    #         print(response.url)
    #         print("=============================================================")
    #         return

    #     super(RepositoryVnuEduVn, self).parse_item(response)
