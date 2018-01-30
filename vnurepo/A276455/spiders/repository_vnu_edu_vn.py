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
import hashlib
import re

class RepositoryVnuEduVn(BasePortiaSpider):
    name = "vnu"
    allowed_domains = [u'repository.vnu.edu.vn']
    start_urls = ["http://repository.vnu.edu.vn/handle/VNU_123/17745?offset=0"
                  "http://repository.vnu.edu.vn/handle/VNU_123/17746?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17747?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17748?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17749?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17750?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17751?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17752?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17753?offset=0",
                  "http://repository.vnu.edu.vn/handle/VNU_123/17754?offset=0"]
    rules = [
        Rule(
            LinkExtractor(
                allow=('.*handle/VNU_123/[0-9]+\?offset=[0-9]+$'),
                deny=('http://repository.vnu.edu.vn/handle/VNU_123/17744',
                      'http://repository.vnu.edu.vn/handle/VNU_123/296'
                )
            ),
            callback='parse_page',
            follow=True
        ),
        # Rule(
        #     LinkExtractor(
        #         allow=('^.*ViewOnline\?bitstid=.*$'),
        #         deny=()
        #     ),
        #     callback='parse_pdf',
        #     follow=False
        # ),
        # Rule(
        #     LinkExtractor(
        #         allow=('.*handle/VNU_123/[0-9]+$'),
        #         deny=('http://repository.vnu.edu.vn/handle/VNU_123/17744',
        #               'http://repository.vnu.edu.vn/handle/VNU_123/296'
        #         )
        #     ),
        #     callback='parse_item',
        #     follow=False,
        # )
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
                        [],
                        True,
                        'xpath'),
                    Field(
                        u'authors',
                        "//tr[contains(.,'Authors:')]/td[@class='metadataFieldValue']/*/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'keywords',
                        "//tr[contains(.,'Keywords:')]/td[@class='metadataFieldValue']/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'date',
                        "//tr[contains(.,' Date:')]/td[@class='metadataFieldValue']/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'publisher',
                        "//tr[contains(.,'Publisher:')]/td[@class='metadataFieldValue']/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'desc',
                        "//tr[contains(.,'Description:')]/td[@class='metadataFieldValue']/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'uri',
                        "//tr[contains(.,'URI:')]/td[@class='metadataFieldValue']/*/text()",
                        [],
                        type='xpath'),
                    Field(
                        u'collection',
                        "//tr[contains(.,'Collections:')]/td[@class='metadataFieldValue']/a/text()",
                        [],
                        True,
                        type='xpath'),
                    Field(
                        u'view_url',
                        "//a[contains(@href,'/ViewOnline?bitstid')]/@href",
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
        s.load(r.headers['Set-Cookie'])
        # bpdb.set_trace()

        cookie = {}
        for k, v in s.items():
            cookie[k] = v.value

        cookie_header = {'Cookie': ",".join([k + "=" + v for k, v in cookie.items()])}
        yield Request("http://repository.vnu.edu.vn/ViewOnline/pdfjs/web/viewer.jsp", headers=cookie_header, callback=self.parse_real_pdf, meta={'article_url': r.meta['article_url'], 'dont_cache': True}, dont_filter=True)

    def parse_real_pdf(self, r):
        item = PdfItem()

        m = re.search(r'/ViewOnline/pdf/([0-9]+)', r.body)
        if m:
            item["file_urls"] = ["http://repository.vnu.edu.vn" + m.group(0)]
            item["article_url"] = r.meta['article_url']
            yield item
        else:
            print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOT FOUND")
            print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOT FOUND")
            print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOT FOUND")
            print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOT FOUND")
