from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.index, name="shopHome"),
    path('checkout/', views.checkout, name="shopCheckout"),
    path('tracker/', views.tracker, name="shopTracker"),
    path('contact/', views.contact, name="shopContact"),
    path('productView/<int:myid>', views.productView, name="shopContact"),
    path('search/', views.search, name="shopSeach"),
    path('signup/', views.signup, name="shopSignup"),
    path('login/', views.userLogin, name="shopLogin"),
    path('logout/', views.userLogout, name="shopLogout"),
    path('updateCart/', views.updateCart, name="updateCart"),
]