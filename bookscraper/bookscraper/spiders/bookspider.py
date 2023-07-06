import scrapy
from bookscraper.items import BookItem
import random


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    custom_settings = {
        "FEEDS": {
            "booksdata.json": {"format": "json", "overwrite": True},
        }
    }

    user_agent_list = [
        "Mozilla/5.0 (Android; Android 5.1; SM-G925L Build/LMY47X) AppleWebKit/536.18 (KHTML, like Gecko)  Chrome/48.0.1207.121 Mobile Safari/603.3",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_4_6) Gecko/20100101 Firefox/67.7",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_4; like Mac OS X) AppleWebKit/537.49 (KHTML, like Gecko)  Chrome/55.0.2252.168 Mobile Safari/602.3",
        "Mozilla/5.0 (Linux; Android 4.4.4; Nexus5 V7.1 Build/KOT49H) AppleWebKit/537.13 (KHTML, like Gecko)  Chrome/55.0.3722.149 Mobile Safari/537.6",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_0_6; like Mac OS X) AppleWebKit/602.45 (KHTML, like Gecko)  Chrome/49.0.1718.240 Mobile Safari/600.3"
    ]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()
            if "catalogue/" not in relative_url:
                relative_url = "catalogue/" + relative_url
            book_url = "http://books.toscrape.com/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page, headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            if "catalogue/" not in next_page:
                next_page = "catalogue/" + next_page
            next_page_url = "http://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback=self.parse, headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})

    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()

        book_item["url"] = response.url,
        book_item["title"] = response.css(".product_main h1::text").get(),
        book_item["upc"] = table_rows[0].css("td::text").get(),
        book_item["product_type"] = table_rows[1].css("td::text").get(),
        book_item["price_excl_tax"] = table_rows[2].css("td::text").get(),
        book_item["price_incl_tax"] = table_rows[3].css("td::text").get(),
        book_item["tax"] = table_rows[4].css("td::text").get(),
        book_item["availability"] = table_rows[5].css("td::text").get(),
        book_item["num_reviews"] = table_rows[6].css("td::text").get(),
        book_item["stars"] = response.css(".star-rating::attr(class)").get(),
        book_item["category"] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item["description"] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        book_item["price"] = response.css("p.price_color::text").get(),

        yield book_item
