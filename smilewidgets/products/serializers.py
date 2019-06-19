from rest_framework import serializers
from products.models import Product, ProductPrice, GiftCard

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'code', 'price')

class ProductPriceSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    product = ProductSerializer()
    
    class Meta:
        model = ProductPrice
        fields = ('id', 'date_start', 'date_end', 'price', 'product_id','product')
