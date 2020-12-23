from django.urls import path
from .views import(home,ProductsDetailView,Signup,Login,logout,add_to_cart,CartView, remove_from_cart,CheckoutView,payment_cod,PaymentView,categorymen,categorywomen,Searchproducts)
app_name='core'
urlpatterns=[
    path('',home,name="home"),
    path('product_page/<slug>/',ProductsDetailView.as_view(),name="product_page"),
    path('Signup',Signup,name="Signup"),
    path('Login',Login,name="Login"),
    path('logout',logout,name="logout"),
    path('cart', CartView.as_view(), name='cart'),
    path('add_to_cart/<slug>/',add_to_cart,name="add_to_cart"),
    path('remove_from_cart/<slug>/',remove_from_cart,name="remove_from_cart"),
    path('checkout',CheckoutView.as_view(),name='checkout'),
    path('payment_cod',payment_cod,name="payment_cod"),
    path('payment',PaymentView.as_view(),name="payment"),
    path('categorymen',categorymen,name="categorymen"),
    path('categorywomen',categorywomen,name="categorywomen"),
    path('Searchproducts',Searchproducts,name="Searchproducts"),
]