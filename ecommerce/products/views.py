from django.http import HttpResponse
import pandas as pd
import pandas as pd
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product  , User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password, check_password

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=400)
    user = User(username=username, password=make_password(password))
    user.save()
    return Response({'message': 'User created successfully'}, status=201)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = User.objects.filter(username=username).first()
    if user and check_password(password, user.password):
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)}, status=200)
    return Response({'error': 'Invalid credentials'}, status=401)



def generate_report(request):
    summary = []
    categories = Product.objects.values_list('category', flat=True).distinct()
    for category in categories:
        products = Product.objects.filter(category=category)
        if products:
            top_product = max(products, key=lambda p: p.quantity_sold)
            total_revenue = sum(p.price * p.quantity_sold for p in products)
            summary.append({
                'category': category,
                'total_revenue': total_revenue,
                'top_product': top_product.product_name,
                'top_product_quantity_sold': top_product.quantity_sold
            })
    
    summary_df = pd.DataFrame(summary)
    summary_csv = summary_df.to_csv(index=False)
    response = HttpResponse(summary_csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=summary_report.csv'
    return response


@csrf_exempt
def upload_data(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        df = pd.read_csv(csv_file)
        df = clean_data(df)
        for _, row in df.iterrows():
            Product.objects.update_or_create(
                product_id=row['product_id'],
                defaults={
                    'product_name': row['product_name'],
                    'category': row['category'],
                    'price': row['price'],
                    'quantity_sold': row['quantity_sold'],
                    'rating': row['rating'],
                    'review_count': row['review_count']
                }
            )
        return HttpResponse('Data uploaded successfully')


def clean_data(df):
    df['price'].fillna(df['price'].median(), inplace=True)
    df['quantity_sold'].fillna(df['quantity_sold'].median(), inplace=True)

    for category in df['category'].unique():
        avg_rating = df[df['category'] == category]['rating'].mean()
        df.loc[(df['category'] == category) & (df['rating'].isnull()), 'rating'] = avg_rating

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    return df