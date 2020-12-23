from django.db import models
from django.shortcuts import reverse
from django.conf import settings
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.utils import timezone

CATEGORY_CHOICES = (
    ('Me', 'Men'),
    ('Wo', 'Women')
)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


# Create your models here.
class Products(models.Model):
    title = models.CharField(max_length=250)
    price = models.FloatField(max_length=16)
    discount_price = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=2000)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1,null=True)
    stock = models.IntegerField()
    image = models.CharField(max_length=5000)
    slug = models.SlugField()
    
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("core:product_page", kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={
        'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={
        'slug':self.slug
        })
   
class OrderProducts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} of {self.product.title}"
    def get_total_price(self):
        return self.quantity*self.product.price

    def get_total_discount_product_price(self):
        return self.quantity *(self.product.price - self.product.discount_price) 

    def get_amount_saved(self):
        return self.get_total_price() - self.get_total_discount_product_price()
    

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_product_price()
        return self.get_total_price()

class OrderProcess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProducts)
    order_booked_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True,blank=True)
    order_placed = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,blank=False,null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price() 
        return total 
        
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=100)
    products = models.ManyToManyField(OrderProducts)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=50)
    mobilenumber = models.CharField(max_length=10)
    OrderProcesses = models.ForeignKey(OrderProcess,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price() 
        return total 
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
