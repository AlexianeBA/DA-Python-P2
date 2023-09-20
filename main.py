
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
try:
    os.mkdir("datas")
except:
    print("Le dossier datas existe")

# Scrap one page of one book   

def scrap_page_one_book(url_book_of_one_book):
    html_livre = requests.get(url_book_of_one_book).content
    soup_livre = BeautifulSoup(html_livre, 'html.parser')
    table_livre=[]
    # url
    product_page_url = url_book_of_one_book
    
    # UPC
    for td in soup_livre.find_all('td'):
        table_livre.append(td)
    upc= table_livre[0].text.strip()

    # title
    title = soup_livre.find('h1').string
    
    # price avec tax
    price_including_tax= table_livre[2].text.strip()
   
    # price sans tax
    price_excluding_tax = table_livre[3].text.strip()
    
    #number_available
    number_available = table_livre[5].text.strip()
    
    # product_description
    div_product_description = soup_livre.find("article", class_="product_page")
    p_product_description = div_product_description.find_all('p')

    if p_product_description:
        prodcut_description = p_product_description[3].get_text()
        
    else:
        print("aucune desciption trouvée")

    # category
    list_a = []
    for a_href in soup_livre.find_all("a"):
        list_a.append(a_href.string)
    category = list_a[3]
    
    # review_rating
    review_rating = table_livre[6].text.strip()
    
    # img_url
    images = soup_livre.find_all('div', class_="item active")
    for image in images:
        image_url = image.find('img')['src']
        image_url = image_url.replace("../../", "http://books.toscrape.com/")
        download_image = requests.get(image_url).content
    
      
    datas_of_one_book = [product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available,  prodcut_description, category, review_rating, image_url]
    
    name_image = re.sub(r'[^\w\s.-]', '', title)
    if not os.path.exists("images"):
        os.makedirs("images")
    with open("images/" + name_image + ".jpg", "wb") as handler:
        handler.write(download_image) 
        
    return datas_of_one_book, category 

# pagination
def list_all_pages_of_category(url_page_category):
    print(url_page_category)
    list_url_category = [url_page_category]
    url_page_category=url_page_category.replace("/index.html", "")   
    page_next = 2
    while True:
        url = f"{url_page_category}/page-{page_next}.html"
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



# scrapp all URL of books in mystery categorie 
def from_list_url_to_categories_csv(list_url_category):
    for url_page_category in list_url_category:
        datas = []
        print(url_page_category)
        return_of_list_all_pages_of_catagory = list_all_pages_of_category(url_page_category)
        for page_url in return_of_list_all_pages_of_catagory:
            reponse = requests.get(page_url)
            page = reponse.content
            soup = BeautifulSoup(page, 'html.parser')
            category = soup.find("h1").text.strip()   
            for values in soup.find_all("h3"):
                a = values.find("a")
                href = a['href']
                a_href_remplaced = href.replace("../../..", "http://books.toscrape.com/catalogue")
                datas_of_one_book, category = scrap_page_one_book(a_href_remplaced)
                datas.append(datas_of_one_book) 
        to_csv(datas, category)
    # return datas   



# Scrap all URL of category in home page
def extract_all_links_categories_from_home_page(url):
    reponse = requests.get(url)
    print(reponse)
    page = reponse.content
    soup = BeautifulSoup(page, 'html.parser')
    list_of_category = []
    category_books = soup.find("ul", class_="nav nav-list").find_all("a")
    for a in category_books:
        a = urljoin(url, a['href'])
        list_of_category.append(a)
        # print(list_of_category)
    del list_of_category[0]
    return list_of_category

# links_categories_home_page("http://books.toscrape.com/index.html")

# Fonction to scrap all categories for all books
def scrap_all_categories(url):
    categories = extract_all_links_categories_from_home_page(url)
    from_list_url_to_categories_csv(categories)
    
HOME_URL = "http://books.toscrape.com/index.html"
scrap_all_categories(url=HOME_URL)

