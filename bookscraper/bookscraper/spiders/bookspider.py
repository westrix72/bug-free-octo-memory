import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()
            if "catalogue/" not in relative_url:
                relative_url = "catalogue/" + relative_url
            book_url = "http://books.toscrape.com/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            if "catalogue/" not in next_page:
                next_page = "catalogue/" + next_page
            next_page_url = "http://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        yield {
            "url": response.url,
            "title": response.css(".product_main h1::text").get(),
            "product_type": table_rows[1].css("td::text").get(),
            "price_excl_tax": table_rows[2].css("td::text").get(),
            "price_incl_tax": table_rows[3].css("td::text").get(),
            "tax": table_rows[4].css("td::text").get(),
            "availability": table_rows[5].css("td::text").get(),
            "num_reviews": table_rows[6].css("td::text").get(),
            "stars": response.css(".star-rating::attr(class)").get(),
            "category": response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            "price": response.css(".price_color::text").get()
        }
