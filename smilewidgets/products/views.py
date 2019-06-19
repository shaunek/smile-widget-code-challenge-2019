from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from products.models import Product, ProductPrice, GiftCard
from datetime import datetime
from collections import namedtuple

@csrf_exempt
@api_view(['POST'])
def fetch_price(request):
    """
    Gets product pricing, taking into account date and gift card data
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            # Product cod and date are required
            product_code = data['productCode']
            date = data['date']
            date = datetime.strptime(date, '%Y-%m-%d')
        except KeyError:
            return HttpResponse(status=400)
        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            return HttpResponse(status=404)
        # Gift card code field is optional
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
        
        discount = gift_code.amount if gift_code is not None else 0
        original_price = product_price.price \
                            if product_price is not None \
                            else product.price
        price = original_price - discount \
                    if original_price >= discount \
                    else original_price

        # Use a simple dictionary for output instead of a more typical object output with serializer
        price_output = {'price':price, 'originalPrice': original_price, 'discount': discount}
        
        return Response(price_output)
