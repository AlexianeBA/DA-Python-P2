
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
    """ Récupération des données d'un livre, création d'une liste avec toutes ces données
    Args: 
        url_book_of_one_book: l'url de la page du livre
    Retruns:
        datas_of_one_book: liste des données d'un livre
        category: nom de la catégorie
    """
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
    price_including_tax = price_including_tax.replace("£", "")
   
    # price sans tax
    price_excluding_tax = table_livre[3].text.strip()
    price_excluding_tax = price_excluding_tax.replace("£", "")
    
    #number_available
    number_available = table_livre[5].text.strip()
    number_available = re.sub(r'[^\d]', "", number_available)
    
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
    review_rating = soup_livre.find_all("p", class_="star-rating")[0]
    class_text = review_rating["class"][1]
    match = re.search(r'\b(One|Two|Three|Four|Five)\b', class_text)
    
    if match:
        star_rating_text = match.group(0)
        star_rating = {
            'One' : 1,
            'Two' : 2,
            'Three' : 3,
            'Four' : 4,
            'Five' : 5
        }[star_rating_text]
        

    # img
    images = soup_livre.find_all('div', class_="item active")
    for image in images:
        image_url = image.find('img')['src']
        image_url = image_url.replace("../../", "http://books.toscrape.com/")
        download_image = requests.get(image_url).content
    
      
    datas_of_one_book = [product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available,  prodcut_description, category, star_rating, image_url]
    
    name_image = re.sub(r'[^\w\s.-]', '', title)
    if not os.path.exists("images"):
        os.makedirs("images")
    with open("images/" + name_image + ".jpg", "wb") as handler:
        handler.write(download_image) 
        
    return datas_of_one_book, category 

# list of all urls of books from category by browsing each page of the category
def list_all_pages_of_category(url_page_category):
    """ Création d'une liste de tous les url des livres à partir d'une catégorie.
    Args: 
        url_page_category: url de la catégorie du livre concerné
    
    Retruns: 
        list_url_category: listes des url de chaque categories
    """
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

# create CSV
def to_csv(datas, category):
    """ Convertie toutes les données récupérées dans un fichier csv pour une catégorie spécifique.
    Args: 
        datas: Liste des donnée d'un livre
        category: Liste du nom des catégories.
    
    Retruns: None
    """
    column_names=["product_page_url", "universal_ product_code (upc)", "title",  "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "star_rating", "image_url"]
    df = pd.DataFrame(datas, columns=column_names)
    df.to_csv("datas/"+category+".csv", index=False)



# scrapp all URL of books in mystery categorie 
def from_list_url_to_categories_csv(list_url_category):
    """ Extrait les données depuis la liste des urls des catégories et les stockent dans un fichier csv.
    Args: list_url_to_categorie: Liste des urls qui représentent les diférentes catégories
    Retruns: None
    """
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
 



# Scrap all URL of category in home page
def extract_all_links_categories_from_home_page(url):
    """ Extrait tous les liens de chaque catégorie qui sont présent sur la page d'accueil
    
    Args: url: url de la page d'accueil
    
    Retruns: list_of_category: liste des url des catégories
    """
    reponse = requests.get(url)
    print(reponse)
    page = reponse.content
    soup = BeautifulSoup(page, 'html.parser')
    list_of_category = []
    category_books = soup.find("ul", class_="nav nav-list").find_all("a")
    for a in category_books:
        a = urljoin(url, a['href'])
        list_of_category.append(a)
    
    del list_of_category[0]
    return list_of_category


# Fonction to scrap all categories for all books
def scrap_all_categories(url):
    """ Extrait toutes les données de chaque catégories de livres présent dans le site et sauvgadre des éléments dans un fichier csv
    
    Args: url: url de la page d'accueil du site
    Return: none.
    """
    categories = extract_all_links_categories_from_home_page(url)
    from_list_url_to_categories_csv(categories)
    
HOME_URL = "http://books.toscrape.com/index.html"
scrap_all_categories(url=HOME_URL)

