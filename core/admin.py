from django.contrib import admin
from .models import Products,OrderProcess,BillingAddress,OrderProducts,Payment
# Register your models here.
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'title','description','price','stock','image','category'
    )
admin.site.register(Products,ProductsAdmin)
class OrderProcessAdmin(admin.ModelAdmin):
    list_display = (
        'user','order_booked_date','ordered_date','order_placed','billing_address','get_total','id','being_delivered','received','payment')
admin.site.register(OrderProcess,OrderProcessAdmin)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user','shipping_address','country','zip','mobilenumber','get_total')
admin.site.register(BillingAddress,BillingAddressAdmin)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user','stripe_charge_id','amount','timestamp')
admin.site.register(Payment,PaymentAdmin)


