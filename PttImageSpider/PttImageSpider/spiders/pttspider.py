#coding=utf8
from PttImageSpider.items import PttImage
from scrapy.http import FormRequest
import scrapy
import logging

domain = "https://www.ptt.cc"

#符合圖片格式的網址
def isImageFormat(link):
    if(link.find('.jpg') > -1 or link.find('.png') > -1 or link.find('.gif') > -1 or link.find('.jpeg') > -1):
       return True;
    return False;

#移除特殊字元（移除Linux上無法作為資料夾的字元）
def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value.rstrip();

class PttSpider(scrapy.Spider):
      name = "ptt_img_spider"
      allowed_domains = ['ptt.cc']
      #板名網址 (可自行修改板名)
      # ex.   start_urls = ["https://www.ptt.cc/bbs/AKB48/index.html"]
      start_urls = ["https://www.ptt.cc/bbs/Beauty/index.html"]

      _retries = 0
      MAX_RETRY = 1
      def parse(self, response):
          if len(response.xpath('//div[@class="over18-notice"]')) > 0:
              if self._retries < PttSpider.MAX_RETRY:
                  self._retries += 1
                  logging.warning('retry {} times...'.format(self._retries))
                  yield FormRequest.from_response(response, formdata={'yes': 'yes'}, callback=self.parse)
              else:
                  logging.warning('you cannot pass')

          else:
              #每篇文章的 標題 網址
              for href in response.xpath('//div[@class="title"]/a'):
                  href_url =  domain + href.xpath('@href')[0].extract()
                  title =  href.xpath('text()')[0].extract()
                  item = PttImage()
                  item['title'] = remove(title, "\/:*?'<>.;&!|`{}")
                  #將 item 的值傳過去因為再來要使用 標題 作為資料夾的名稱
                  yield scrapy.Request(href_url, callback = self.parse_images, meta={'item': item})
              #抓取上(下)一頁的 URL
              previouspage = response.xpath('//a[@class="btn wide"]/@href')[1]
              previouspage =  domain + previouspage.extract()
              yield scrapy.Request(previouspage, self.parse)

      def parse_images(self, response):
          item = response.meta['item']
          imgurls = []
          #取得每篇文章內的 圖片
          for img in response.xpath('//a/@href'):
              url = img.extract()
              if(isImageFormat(url)):
                 imgurls.append(url)

          item['image_urls'] = imgurls
          return  item


            # for href in response.xpath('//div[@class="r-ent"]'):
            #     if href.xpath('div[@class="nrec"]/span/text()') :
            #      #每篇文章的 標題 網址
            #         href_url =  domain + href.xpath('div[@class="title"]/a/@href')[0].extract()
            #         title =  href.xpath('div[@class="title"]/a/text()')[0].extract()
            #         item = PttImage()
            #         item['title'] = remove(title, "\/:*?'<>.;&!|`{}") + '_' + href.xpath('div[@class="nrec"]/span/text()')[0].extract()
            #         #將 item 的值傳過去因為再來要使用 標題 作為資料夾的名稱
            #         yield scrapy.Request(href_url, callback = self.parse_images, meta={'item': item})
            #   #抓取上(下)一頁的 URL
            #   previouspage = response.xpath('//a[@class="btn wide"]/@href')[1]
            #   previouspage =  domain + previouspage.extract()
            #   yield scrapy.Request(previouspage, self.parse)

              # for href in response.xpath('//div[@class="title"]/a'):
              #     href_url =  domain + href.xpath('@href')[0].extract()
              #     title =  href.xpath('text()')[0].extract()
              #     item = PttImage()
              #     item['title'] = remove(title, "\/:*?'<>.;&!|`{}")
              #     #將 item 的值傳過去因為再來要使用 標題 作為資料夾的名稱
              #     yield scrapy.Request(href_url, callback = self.parse_images, meta={'item': item})
              # #抓取上(下)一頁的 URL
              # previouspage = response.xpath('//a[@class="btn wide"]/@href')[1]
              # previouspage =  domain + previouspage.extract()
              # yield scrapy.Request(previouspage, self.parse)


