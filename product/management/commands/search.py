"""

"""

from django.core.management.base import BaseCommand
from elasticsearch_dsl import Q
from product.documents import ProductDocument
from product.models import ProductModel
from pathlib import Path
from time import sleep
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch

import xlsxwriter, openpyxl, json, requests
import pandas as pd
from colorama import init, Fore, Back, Style 

from django.db.models import Case, When


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
init(autoreset=True) # for COLORAMA


def clean_word(text):
    """ Чистим название от символов """
    return text.replace('*', '').replace('_', '').replace('NEW', '').replace('.', '').lstrip().rstrip()

def beautiful_price(price):
    """ Делаем красивую стоимость, повышая до ближайшего краного 10 """
    while price % 10 != 0:
        price += 1    
    return price

def to_word_list(text):
    """ Чистит текст запроса и возвращает список слов из запроса """
    return text.replace('(', '').replace(')', '').replace('*', '').replace('+', '').replace('-', ' ').replace('.', '').replace('_', '').replace('*', '').split()


class Command(BaseCommand):
    args = ''
    help = ''

    brand_ids = {
        'fubag' : 1,
        'svarog': 9,
        'telwin': 13,
    }

    count = 0

    def add_arguments(self , parser):
        parser.add_argument('--brand', action='append', type=str)

    def handle(self, *args, **options):
        brand_name = options['brand'][0]
        client = Elasticsearch()
        s = Search(using=client)
        document_class = ProductDocument
        product_queryset = ProductModel.objects.all()

        brand = self.brand_ids[brand_name]
        page = 1
        prods = []

        # запрос товаров бренда
        while page:
            response = requests.get(f'http://127.0.0.1:8000/c/prods/?brnd={ brand }&page={ page }')
            data = response.json()
            prods += [ { "id": product["id"] , "vcode": product["vcode"] ,"product": product["name"] ,"price": product["only_price"]} for product in data["results"]]
            page = None if data["next"] == None else page + 1

        """
        Make requests in ElasticSearch  P.S. MAKE OrderBy как у ElasticSearch
        
        colors: BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE RESET
        """ 
        for search_query in prods:

            search = clean_word(f'{search_query["vcode"]} {search_query["product"]}')

            query = Q('match', name=search)
            search = document_class.search().query(query)
            response = search.execute()

            self.count += 1
            b = to_word_list(search_query["product"])
            
            if self.count == 187:
                print(f'\nCNT{ self.count }\n{search_query["id"]}\tVC { search_query["vcode"] }\t{int(search_query["price"])} RUB\t{search_query["product"]}')

            ids_response = [ product.id for product in response]

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids_response)])
            products_qs = product_queryset.filter(brand = brand_name).filter(id__in = ids_response).order_by(preserved)

            for product_qs in products_qs:
                a = to_word_list(product_qs.name)

                # Проверка на полное совпадение
                similar_words = True
                for c in a:
                    if c not in b:
                        similar_words = False


                if self.count == 187:


                    if similar_words or product_qs.vcode == search_query["vcode"]:

                        if similar_words and product_qs.vcode == search_query["vcode"]:
                            print(Fore.WHITE  + f'{product_qs.id}\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')
                        
                        else:
                            print(Fore.CYAN + f'{product_qs.id}\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')
                    
                    else:
                        print(Fore.YELLOW + f'{product_qs.id}\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')




        """
        Return jsonFile with chenges

        [
            { 
                "id": INT, 
                "price": INT,
                "vcode": False, 
                "rename": False, 
                "dissable": False  
            },
        ]
        """