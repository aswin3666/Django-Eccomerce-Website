from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import ListView,DetailView,View
from .models import Products,OrderProducts,OrderProcess,BillingAddress,Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User,auth
from django.contrib import messages
import random
import string
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm
from django.core.mail import send_mail
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
#homepage of website
def home(request):
    product = Products.objects.all()
    return render(request,'HOME.html',{'product':product})
#category of products
def categorymen(request):
    product = Products.objects.all().filter(category='Me')
    return render(request,'mencategorym.html',{'product':product})

def categorywomen(request):
    product = Products.objects.all().filter(category='Wo')
    return render(request,'womencategory.html',{'product':product})

#search function
def Searchproducts(request):
    search = request.GET.get('search')
    product = Products.objects.all().filter(title__icontains=search)
    return render(request,'searchresult.html',{'product':product,'search':search})

#Productpage
class ProductsDetailView(DetailView):
    model = Products
    template_name = "product_page.html"

#user signup, login ,logout processes
def Signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Already Exists')
                return render(request,'signup.html')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken by Another User')
                return render(request,'signup.html')
            else :
                user=User.objects.create_user(username=username,email=email,password=password1)
                user.save()
                subject = 'ACCOUNT CREATED SUCCESSFULLY'
                message = f'HELLO {user.username}, WELCOME TO E-CART, YOUR ACCOUNT IS CREATED IN E-CART'
                send_mail(subject,
                 message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                if user is not None:
                    auth.login(request,user)
                    return redirect('/')
        else:
            messages.info(request,'Password Not Matching')
            return render(request,'signup.html')
    else:
        return render(request,'signup.html')
    return render(request,'signup.html')  

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'User not Found')
            return render(request,'login.html')
    else:
        return render(request,'login.html')
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

#Cart page
class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = OrderProcess.objects.get(user=self.request.user)
            return render(self.request, 'cart.html',{'object': order})
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

#add to cart and remove products from cart
@login_required
def add_to_cart(request,slug):
    product = get_object_or_404(Products,slug=slug)
    order_product,created = OrderProducts.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = OrderProcess.objects.filter(user=request.user)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            order.products.add(order_product)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:cart")
    else:
        order = OrderProcess.objects.create( user=request.user)
        order.products.add(order_product)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:cart")

@login_required
def remove_from_cart(request,slug):
    product = get_object_or_404(Products,slug=slug)
    order_qs = OrderProcess.objects.filter(user=request.user)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProducts.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.products.remove(order_product)
            messages.info(request, "This item quantity was Updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product_page", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product_page", slug=slug)

 #billing process       
class CheckoutView(View):
    def get(self,*args,**kwargs):
        form = CheckoutForm()
        return render(self.request,'checkout.html',{'form':form})
    def post(self,*args,**kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = OrderProcess.objects.get(user=self.request.user)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                mobilenumber = form.cleaned_data.get('mobilenumber')
                #save_info=form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(user=self.request.user,shipping_address= shipping_address,country=country,zip=zip,mobilenumber=mobilenumber)
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_option =='C':
                    current = self.request.user
                    Email = current.email
                    subject = 'ORDER PLACED SUCESSFULLY'
                    message = "WELCOME TO CART, YOUR ORDER SUCESSFULLY PLACED ON CASH ON DELIVERY..FOR MORE DETAILS PLEASE VISIT E-CART"                  
                    send_mail(subject,message, settings.EMAIL_HOST_USER, [Email], fail_silently=False)
                    return redirect('core:payment_cod')
                elif payment_option == 'S':
                    return redirect('core:payment')
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

#placed addresss page
def payment_cod(request):
    order = OrderProcess.objects.get(user=request.user)
    order_details = BillingAddress.objects.filter(user=request.user)
    return render(request,'orderplaced.html',{'order_details':order_details,'object': order})

#Payment Gateway
class PaymentView(View):
    def get(self,*args,**kwargs):
        return render(self.request,'payment.html')
    def post(self,*args,**kwargs):
        order = OrderProcess.objects.get(user=self.request.user,order_placed=False)
        amount=int(order.get_total())
        try:
            charge=stripe.Charge.create(
                amount=amount,
                currency="usd",
                source="tok_visa"
        )
            payment=Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            order.order_placed = True
            order.payment = payment
            order.save()
            return redirect('core:payment_cod')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            messages.error(self.request,"RateLimitError")
            return redirect("/")
       
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request,"InvalidRequestError ")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            messages.error(self.request,"AuthenticationError")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            messages.error(self.request,"APIConnectionError ")
            return redirect("/")

        except stripe.error.StripeError as e:
            messages.error(self.request,"StripeError")
            return redirect("/")
            
        except Exception as e:
            messages.error(self.request,"Something went error try again")
            return redirect("/")



    
