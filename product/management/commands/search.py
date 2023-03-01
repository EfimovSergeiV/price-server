"""

"""
import os
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


    data = []
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


            tmp_data = {
                "product": { "id": search_query["id"], "vcode": search_query["vcode"], "name": search_query["product"] },
                "options": []
            }

            writed_be = {
                "id": tmp_data["product"]["id"],
                "price": False,
                "vcode": False,
                "rename": False,
                "dissable": False
            }
            
            os.system('clear')
            if len(self.data) > 0:
                print(f'Latest: { self.data[-1] }\n')
            
            if True:
                print(f'\nCNT:{ self.count }\n{search_query["id"]}\tVC { search_query["vcode"] }\t{int(search_query["price"])} RUB\t{search_query["product"][0:180]}')

            ids_response = [ product.id for product in response]

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids_response)])
            products_qs = product_queryset.filter(brand = brand_name).filter(id__in = ids_response).order_by(preserved)


            variant_counter = 0
            for product_qs in products_qs:
                variant_counter += 1
                a = to_word_list(product_qs.name)

                tmp_data['options'].append(
                    { "vcode": product_qs.vcode, "price": product_qs.price, "name": product_qs.name }
                )

                # Проверка на полное и совпадение по venodor code
                similar_words = True
                for c in a:
                    if c not in b:
                        similar_words = False
                if True:
                    if similar_words or product_qs.vcode == search_query["vcode"]:
                        if similar_words and product_qs.vcode == search_query["vcode"]:
                            print(Fore.WHITE  + f'{variant_counter}.\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')
                        else:
                            print(Fore.CYAN + f'{variant_counter}.\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')
                    else:
                        print(Fore.YELLOW + f'{variant_counter}.\tVC {product_qs.vcode}\t{product_qs.price} RUB\t{product_qs.name[0:180]}')
            
            print(
                # RED GREEN YELLOW BLUE MAGENTA CYAN WHITE
                Fore.CYAN + f'\n======================================',
                Fore.CYAN + f'\n Number product - select number option',
                Fore.CYAN + f'\n Space - skip',
                Fore.CYAN + f'\n Enter - select first option',
                Fore.CYAN + f'\n v - rewrite vcode\tn - rewrite name',
                Fore.CYAN + f'\n d - dissable product\tq - save and exit',
                Fore.CYAN + f'\n======================================'
            )
            
            # print(f'WRITED DATA: { self.data }')
            action = input("\nEnter action:\t")

            if action == '':
                current_id_option = 1
                writed_be["price"] = tmp_data['options'][int(current_id_option) - 1]["price"]
                self.data.append(writed_be)
            
            elif len(action) > 1 or action.lower() in ('v', 'n', 'd',) or action in [ str(i) for i in range( 1, len(tmp_data['options']) + 1 ) ]:
                for key in list(action):
                    if key in [ str(i) for i in range( 1, len(tmp_data['options']) + 1 ) ]:
                        current_id_option = int(key)
                        writed_be["price"] = tmp_data['options'][int(current_id_option) - 1]["price"]
                    if key.lower() in ('v',):
                        writed_be["vcode"] = tmp_data['options'][int(current_id_option) - 1]["vcode"]
                    if key.lower() in ('n',):
                        writed_be["name"] = tmp_data['options'][int(current_id_option) - 1]["name"]
                    if key.lower() in ('d',):
                        writed_be["dissable"] = True
                    if key.lower() in ('q',):
                        break
                    else:
                        pass

                self.data.append(writed_be)
                

            elif action == ' ':
                pass

            else:
                break


        with open(f'{ BASE_DIR }/output.json', 'w') as file:
            json.dump(self.data, file)
    