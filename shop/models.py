from typing import MutableSequence
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import AutoField, CharField
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=20, default="")
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default="")
    email = models.CharField(max_length=20, default="")
    phoneNumber = models.CharField(max_length=15, default="")
    desc = models.CharField(max_length=300, default="")

    def __str__(self):
        return self.name

#stores shipping details of the order
class Checkout(models.Model):
    order_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=30, default="")
    email = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=200, default="")
    city = models.CharField(max_length=20, default="")
    state = models.CharField(max_length=20, default="")
    zip_code = models.CharField(max_length=20, default="")
    phoneNumber = models.CharField(max_length=15, default="")
    productJson = models.CharField(max_length=2000, default="")

    def __str__(self):
        return self.name


class Tracker(models.Model):
    tracker_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    order_id=models.IntegerField(default="")
    desc = models.CharField(max_length=300, default="Order has been placed")
    date = models.DateTimeField(default=now)


class productComments(models.Model):
    comment_id=models.AutoField(primary_key=True)
    comment=models.TextField()
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    parent=models.ForeignKey('self',on_delete=models.CASCADE, null=True )
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return " \" "+ self.comment[:6] + "...\" by " + self.user.username


class Cartrecord(models.Model):
    cartid=models.AutoField(primary_key=True)
    cart_user=models.ForeignKey(User,on_delete=models.CASCADE)
    json_data=models.CharField(max_length=500,default="0")

    def __str__(self):
        return self.cart_user.username