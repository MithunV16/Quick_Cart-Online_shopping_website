from django.contrib import admin
from .models import Contact, Product,Checkout,Tracker,productComments,Cartrecord



class ProductAdmin(admin.ModelAdmin):
    list_display=['id','product_name','price','pub_date']

class CartdataAdmin(admin.ModelAdmin):
    list_display=['cart_user']

class CheckoutAdmin(admin.ModelAdmin):
    list_display=['order_id','name']

class TrackerAdmin(admin.ModelAdmin):
    list_display=['tracker_id','order_id','desc','date']

admin.site.register(Product,ProductAdmin)
admin.site.register(Contact)
admin.site.register(Checkout,CheckoutAdmin)
admin.site.register(Tracker,TrackerAdmin)
admin.site.register(productComments)
admin.site.register(Cartrecord,CartdataAdmin)