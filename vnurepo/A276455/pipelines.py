# -*- coding: utf-8 -*-

import scrapy
from scrapy.pipelines.files import FilesPipeline
import bpdb
import requests
import re
import mysql.connector
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class MyFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        return 'full/' + request.url.split('/')[-1]

class A276455Pipeline(object):
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(user='root', password='hahaha', host='127.0.0.1', database='vnurepo')

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def insert_book(self, item):
        query = ("INSERT INTO `books` (`title`, `authors`, `collection`, `date`, `keywords`, `publisher`, `uri`, `view_url`) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        values = (item.get('title'), item.get('authors'), item.get('collection'), item.get('date'), item.get('keywords'), item.get('publisher'), item.get("uri"), item.get("view_url"))
        self.conn.cursor().execute(query, values)
        self.conn.commit()

    def insert_file(self, item):
        query = ("INSERT INTO `files` (`article_url`, `file_url`) VALUES (%s, %s)")
        values = (item.get('article_url'), ",".join(item.get('file_urls')))
        self.conn.cursor().execute(query, values)
        self.conn.commit()

    def process_item(self, item, spider):
        if item.get('title'):
            self.insert_book(item)
        elif item.get('article_url'):
            self.insert_file(item)
        else:
            pass # WHAAAT

        return item
