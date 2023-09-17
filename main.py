import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
try:
    os.mkdir("datas")
except:
    print("ko")



# TO DO : comment passer à la page suivante (pagination)
def list_all_pages_of_category():
    list_url_category = []
    page_next = 1 
    while True:
        url = f"http://books.toscrape.com/catalogue/category/books/mystery_3/page-{page_next}.html"
        reponse = requests.get(url)
        page = reponse.status_code
        print(page)
        if page == 200:
            list_url_category.append(url)
            print(url)
            page_next +=1
        else:
            break
    return list_url_category
# CSV of one book
def to_csv(datas, category):
   
    column_names=["product_page_url", "universal_ product_code (upc)", "title",  "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"]
    df = pd.DataFrame(datas, columns=column_names)
    df.to_csv("datas/"+category+".csv", index=False)

# Scrap one page of one book   
def scrapp_page_one_book(url_book_of_one_book):
    reponse = requests.get(url_book_of_one_book)
    page = reponse.content
    soup = BeautifulSoup(page, 'html.parser')
    table_livre=[]
    # url
    product_page_url = url_book_of_one_book
    

    # UPC
    for td in soup.find_all('td'):
        table_livre.append(td)
    upc= table_livre[0].text.strip()
    

    # title
    title = soup.find('h1').string
    

    # price avec tax
    price_including_tax= table_livre[2].text.strip()
   

    # price sans tax
    price_excluding_tax = table_livre[3].text.strip()
    

    #number_available
    number_available = table_livre[5].text.strip()
    

    # product_description
    div_product_description = soup.find("article", class_="product_page")
    p_product_description = div_product_description.find_all('p')

    if p_product_description:
        prodcut_description = p_product_description[3].get_text()
        
    else:
        print("aucune desciption trouvée")

    # category
    list_a = []
    for a_href in soup.find_all("a"):
        list_a.append(a_href.string)
    category = list_a[3]
    


    # review_rating
    review_rating = table_livre[6].text.strip()
    


    # img_rul
    img = soup.find_all('img')
    for image in img:
        image_url = image['src']
        image_url.replace("../../", "http://books.toscrape.com/" )
    
    
    datas_of_one_book = [product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available,  prodcut_description, category, review_rating, image_url]
    return datas_of_one_book, category 
    

url_book_of_one_book = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
# scrapp_page_one_book(url_book_of_one_book)



# scrapp all URL of books in mystery categorie 
def links_books_of_category_mistery(list_url_category):
    datas = []
    for url_page_category in list_url_category:
        print(url_page_category)
        reponse = requests.get(url_page_category)
        page = reponse.content
        soup = BeautifulSoup(page, 'html.parser')            
        for values in soup.find_all("h3"):
            a = values.find("a")
            href = a['href']
            a_href_remplaced = href.replace("../../..", "http://books.toscrape.com/catalogue")
            datas_of_one_book, category = scrapp_page_one_book(a_href_remplaced)
            datas.append(datas_of_one_book) 
    to_csv(datas, category)

list_url_category = list_all_pages_of_category()
links_books_of_category_mistery(list_url_category)





# Scrap all URL of category in home page
def links_categories_home_page(url):
    reponse = requests.get(url)
    page = reponse.content
    soup = BeautifulSoup(page, 'html.parser')
    list_of_category = []
    category_books = soup.find("ul", class_="nav nav-list").find_all("a")
    for a in category_books:
        a = urljoin(url, a['href'])
        list_of_category.append(a)
    for category_url in list_of_category:
        print(category_url)
    
url = "http://books.toscrape.com/index.html"
links_categories_home_page(url)

print("*****")