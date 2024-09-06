import pandas as pd
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
from django.conf import settings
from products.models import Product


class Command(BaseCommand):
    help = 'Uploads product data from a CSV file into the database'

    def handle(self, *args, **kwargs):
       
        df = pd.read_csv('path/to/your/products.csv')
        df['price'].fillna(df['price'].median(), inplace=True)
        df['quantity_sold'].fillna(df['quantity_sold'].median(), inplace=True)
        df['rating'].fillna(df.groupby('category')['rating'].transform('mean'), inplace=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    
        engine = create_engine('postgresql://ecommerce_user:ecommerce@localhost:5432/ecommerce_db')
        df.to_sql(Product._meta.db_table, con=engine, if_exists='replace', index=False)
        self.stdout.write(self.style.SUCCESS('Data uploaded successfully'))