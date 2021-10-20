import scrapy
import w3lib.html

from ..items import ArgumentTopicsItem

#import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd


class CrawlDebateTopicSpider(scrapy.Spider):
    '''
    The goal of this crawler is to crawl top 5 topics with their pros and cons arguments
    from the website https://www.debate.org/opinions/?sort=popular and save them to a JSON file in the following
    format:
    [
        {"topic": "xxx",
         "category": "xxx",
         "pro_arguments": [
            {
                "title": "xxxx",
                "body": "xxxx"
            }
         ],
         "con_arguments": [
            {
                "title": "xxxx",
                "body": "xxxx"
            }
         ]
        }
    ]
    '''

    # Name of the crawler
    name = "debate_crawler"

    # Create an instance of ArgumentTopicsItem class for storing the scrapped data
    item = ArgumentTopicsItem()

    # Root url to the popular debate topics
    root_url = 'https://www.debate.org/opinions/?sort=popular'

    # Request more arguments from server
    argumentPage_url = 'https://www.debate.org/opinions/~services/opinions.asmx/GetDebateArgumentPage'

    def start_requests(self):
        """This function initiates a request to the base URL"""
        # Send initial request to the base URL
        request = scrapy.Request(url=self.root_url, callback=self.parse_topic_urls)
        yield request

    def parse_topic_urls(self, response):
        """This function parses the popular topics URL"""
        # Get the list of all popular topics present on the base URL
        topic_list = response.css('#opinions-list .image-frame .a-image-contain')

        # Keep first five only and extract relative slug
        for topic in topic_list[0:5]:
            slug = topic.css('a::attr(href)').extract_first()
            # Join the relative slug to make it a complete URL
            url = response.urljoin(slug)
            # Send a request to the server for the topic content
            request = scrapy.Request(url=url, callback=self.parse_topic_content)
            yield request

    def parse_topic_content(self, response):
        """This function parses the topic content and saves them as scrapy item"""
        # Scrap all the raw pro arguments
        pro_arguments_list = response.css('#debate #yes-arguments ul .hasData')
        # Scrap all the raw con arguments
        con_arguments_list = response.css('#debate #no-arguments ul .hasData')

        # Get the title of the topic
        argument_topic = response.css('.r-contain .qh-debate ::text').get()
        self.item['topic'] = argument_topic

        # Get the category of the topic
        argument_category = response.css('#breadcrumb a')
        category = argument_category[2].css('::text').get()
        self.item['category'] = category

        pro_arguments_list_data = []
        con_arguments_list_data = []

        # Go through all the raw pro arguments, extract title & body and remove HTML tags from the body
        for pro_argument in pro_arguments_list:
            pro_arguments_dict = dict()
            # Get the argument title text
            pro_arguments_dict['title'] = pro_argument.css('.hasData h2 ::text').get()

            # Get the argument body text
            pro_arguments_dict['body'] = w3lib.html.remove_tags(pro_argument.css('.hasData p').get())
            # Append the pro argument dict to the list
            pro_arguments_list_data.append(pro_arguments_dict)
        # Set pro_arguments for the topic
        self.item['pro_arguments'] = pro_arguments_list_data

        # Go through all the raw con arguments, extract title & body and remove HTML tags from the body
        for con_argument in con_arguments_list:
            con_arguments_dict = dict()
            # Get the argument title text
            con_arguments_dict['title'] = con_argument.css('.hasData h2 ::text').get()

            # Get the argument body text
            con_arguments_dict['body'] = w3lib.html.remove_tags(con_argument.css('.hasData p').get())
            # Append the con argument dict to the list
            con_arguments_list_data.append(con_arguments_dict)
        # Set con_arguments for the topic
        self.item['con_arguments'] = con_arguments_list_data

        yield self.item
