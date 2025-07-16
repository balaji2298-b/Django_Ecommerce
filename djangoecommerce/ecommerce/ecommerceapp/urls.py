from django.urls import path
from ecommerceapp import views

urlpatterns = [
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.loginpage,name="login"),
    path('accounts/login/', views.loginpage),
    path('logout',views.logoutpage,name="logout"),
    path('cart',views.cartpage,name="cart"),
    path('addtocart',views.addtocart,name="addtocart"),
    path('fav',views.favpage,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('removefav/<str:fid>',views.removefav,name="removefav"),
    path('removecart/<str:cid>',views.removecart,name="removecart"),
    path('collections', views.collections,name='collections'),
    path('collections/<str:name>', views.collectionsview,name='collections'),
    path('collections/<str:name>/<str:pname>', views.productdetails,name='productdetails'),
    path('billingpage',views.billingpage,name='billingpage'),
    path('orderpage', views.orderpage, name='orderpage'),
    path('removeorder/<int:cid>',views.removeorder,name='removeorder'),
    path('addreview/<str:product_name>',views.addreview,name='addreview'),
    path('checkoutview/', views.checkoutview, name='checkoutview'),
    path('paymentsuccess/', views.paymentsuccess, name='paymentsuccess'),
]

