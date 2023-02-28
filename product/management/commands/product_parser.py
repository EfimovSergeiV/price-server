from django.core.management.base import BaseCommand, CommandError

# from catalog.documents import ProductDocument   #, ProductKeywordDocument

from pathlib import Path
import xlsxwriter, json
import pandas as pd
from time import sleep

from elasticsearch_dsl import Q
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch

from product.models import ProductModel


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def clean_word(text):
    """ Чистим название """
    return text.replace('*', '').replace('_', '').replace('NEW', '').lstrip().rstrip()

def beautiful_price(price):
    """ Делаем красивую стоимость, повышая до ближайшего краного 10 """
    while price % 10 != 0:
        price += 1    
    return price

def word_list(text):
    """ Чистит текст запроса и возвращает список слов из запроса """
    return text.replace('(', '').replace(')', '').replace('+', '').replace('-', '').replace('.', '').replace('_', '').replace('*', '').split()


class Command(BaseCommand):
    args = ''
    help = '--brand fubag/svarog/telwin'

    path_prices = {
        'fubag' : f'{ BASE_DIR }/prices/PriceFubag.xlsx',
        'svarog': f'{ BASE_DIR }/prices/PriceSvarog.xlsx',
        'telwin': f'{ BASE_DIR }/prices/PriceTelwin.xlsx',
    }

    fields_prices = {
        'fubag' : { "vcode": 1,       "name": 2, "old_name": 4,    "price": 10, "if": 0, "of": 1 },
        'svarog': { "vcode": 'index', "name": 1, "old_name": None, "price": 6,  "if": 1, "of": 2 },
        'telwin': { "vcode": 'index', "name": 1, "old_name": None, "price": 4,  "if": 0, "of": 1 },
    }


    def add_arguments(self , parser):
        parser.add_argument('--brand', action='append', type=str)

    def handle(self, *args, **options):
        brand = options['brand'][0]
        file_path = self.path_prices[brand]
        qs_products = ProductModel.objects.all()
        
        # Counters
        counter = 0

        xl = pd.ExcelFile(file_path)    # read_only=True if openpyxl > 3.1.0 
        sheet_list = xl.sheet_names     # print(sheet_list)        

        for sheet_name in sheet_list[ self.fields_prices[brand]["if"] : self.fields_prices[brand]["of"] ]:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, index_col=0)

            # Бежим по строкам, обрабатываем колонки
            for index, row in df.iterrows():
                if self.fields_prices[brand]["vcode"] == "index":
                    vcode = f'{index}'
                else:
                    vcode = f'{row[self.fields_prices[brand]["vcode"]]}'

                name = clean_word(f'{row[self.fields_prices[brand]["name"]]}')


                # Поле old_name не у всех
                old_name_val = self.fields_prices[brand]["old_name"]
                if old_name_val:
                    old_name = clean_word(f'{row[old_name_val]}') if len(f'{row[old_name_val]}') > 1 else None
                else:
                    old_name = None
                

                price = row[self.fields_prices[brand]["price"]]


                if type(price) == int:
                    price = beautiful_price(price)
                    counter += 1
                    print(f' { counter }.\t{ vcode }\t\t{ name }\t\t{ old_name }\t\t{price}')


                    if len(qs_products.filter(name = name)) == 0:   # Блок водяного охлаждения GRA 90 <= BUG
                        ProductModel.objects.create(
                            vcode = vcode,
                            brand = brand,
                            name = name,
                            old_name =old_name,
                            price = f'{ price }'
                        )
                        print(f'Created\t{name}')
                    else:
                        print(f'Skiped\t{name}')




    # def clean_word(text):
    #     """ Чистим название """
    #     return text.replace('*', '').replace('_', '')

    # def word_list(text):
    #     """ Чистит текст запроса и возвращает список слов из запроса """
    #     return text.replace('(', '').replace(')', '').replace('+', '').replace('-', '').replace('.', '').replace('_', '').replace('*', '')  #.split()





# # Получаем список разделов xls файла
# file_path = f'{BASE_DIR}/prices/PriceFubag.xlsx'

# # Counters
# counter = 0

# xl = pd.ExcelFile(file_path)
# sheet_list = xl.sheet_names


# qs_products = ProductModel.objects.all()


# for sheet_name in sheet_list[ 0 : 1 ]:
#     df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, index_col=0)


#     # Бежим по строкам, обрабатываем колонки
#     for index, row in df.iterrows():

#         counter += 1

#         vcode = f'{row[1]}'
#         name = clean_word(f'{row[2]}')
#         old_name = clean_word(f'{row[4]}') if len(f'{row[4]}') > 0 else None
#         price = row[10]


#         if type(price) == int:
#             # print(f' {counter}. {vcode} {name} {old_name} {price}')


#             if len(qs_products.filter(name = name)) == 0:
#                 ProductModel.objects.create(
#                     vcode = vcode,
#                     brand = 'fubag',
#                     name = name,
#                     old_name =old_name,
#                     price = f'{ price }'
#                 )
#                 print(f'Created\t{name}')
#             else:
#                 print(f'Skiped\t{name}')
            
