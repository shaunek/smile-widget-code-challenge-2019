from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.parsers import JSONParser
from products.models import Product, ProductPrice, GiftCard
from products.serializers import ProductSerializer, ProductPriceSerializer
from datetime import datetime
from collections import namedtuple

def product_list(request):
    """
    List all products
    """
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)

def product_detail(request, id):
    """
    List product details
    """
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data)

@csrf_exempt
def fetch_price(request):
    """
    Gets product pricing, taking into account date and gift card data
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        product_code, date = ('', '')
        try:
            product_code = data['productCode']
            date = data['date']
            date = datetime.strptime(date, '%Y-%m-%d')
        except KeyError:
            return HttpResponse(status=400)
        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            return HttpResponse(status=404)

        gift_card_code = data['giftCardCode'] if 'giftCardCode' in data else None

        product_price = ProductPrice.objects.filter(
            Q(date_end__gte=date) | Q(date_end__isnull=True),
            date_start__lte=date,
            product__code=product_code
        ).order_by('-date_start').first()
        
        gift_code = GiftCard.objects.filter(
            Q(date_end__gte=date) | Q(date_end__isnull=True),
            date_start__lte=date,
            code=gift_card_code
        ).order_by('-date_start').first()
        
        price_output = {}
        price_output['discount'] = gift_code.amount if gift_code is not None else 0
        price_output['originalPrice'] = product_price.price \
                                          if product_price is not None \
                                          else product.price
        price_output['price'] = product_price.price - price_output['discount'] \
                                    if product_price is not None \
                                    else product.price - price_output['discount']

        return JsonResponse(price_output)
