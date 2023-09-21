from book import Book
HOME_URL = "http://books.toscrape.com/index.html"
book_scraper = Book()
book_scraper.scrap_all_categories(url=HOME_URL)