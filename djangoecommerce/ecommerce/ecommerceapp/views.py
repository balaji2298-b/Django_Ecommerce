from django.shortcuts import render,redirect,get_object_or_404
from ecommerceapp.models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from ecommerceapp.forms import CustomUserForm
import json
from django.http import  JsonResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.db import connection
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.http import HttpResponse 
from django.contrib.auth.models import User
from razorpay import Client
from ecommerceapp.utils import get_user_counts 
from .utils import get_user_counts
from django.contrib.auth import get_user_model
import re

def get_user_counts(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM ecommerceapp_cart WHERE user_id = %s", [user_id])
        cart_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ecommerceapp_favourite WHERE user_id = %s", [user_id])
        fav_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ecommerceapp_orderrs WHERE user_id = %s", [user_id])
        order_count = cursor.fetchone()[0]
    return {"cart_count": cart_count,"fav_count": fav_count,"order_count": order_count}

def index(request):
    products = Product.objects.filter(trending=1)
    if request.user.is_authenticated:
        counts = get_user_counts(request.user.id)
    else:
        counts = {"cart_count": 0, "fav_count": 0, "order_count": 0}
    return render(request, 'shop/index.html', {"products": products, **counts})

def loginpage(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"shop/login.html")

def logoutpage(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")

def register(request):
	form=CustomUserForm()
	if request.method=='POST':
		form=CustomUserForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,"Registration Success You can Login Now..!")
			return redirect('/login')
	return render(request,"shop/register.html",{'form':form})

def collections(request):
    category = Category.objects.filter(status=0)
    if request.user.is_authenticated:
        counts = get_user_counts(request.user.id)
    else:
        counts = {"cart_count": 0, "fav_count": 0, "order_count": 0}
    return render(request, 'shop/collections.html', {"category": category,**counts})

def collectionsview(request, name):
    if Category.objects.filter(name=name, status=0).exists():
        products = Product.objects.filter(category__name=name)
        if request.user.is_authenticated:
            counts = get_user_counts(request.user.id)
        else:
            counts = {"cart_count": 0, "fav_count": 0, "order_count": 0}
        return render(request, 'shop/products/index.html', {"products": products,"category__name": name,**counts})
    else:
        messages.warning(request, "No Such Category Found")
        return redirect('collections')

def productdetails(request, name, pname):
    if Category.objects.filter(name=name, status=0).exists():
        if Product.objects.filter(name=pname, status=0).exists():
            product = Product.objects.filter(name=pname, status=0).first()
            reviews = Reviews.objects.filter(product=product).order_by('date')
            review_count = reviews.count()

            if request.user.is_authenticated:
                counts = get_user_counts(request.user.id)
            else:
                counts = {"cart_count": 0, "fav_count": 0, "order_count": 0}

            return render(request,"shop/products/productdetail.html",{
                "product": product,
                "category__name": name,
                "reviews": reviews,
                "review_count": review_count,
                **counts
            })
        else:
            messages.error(request, "No Such Product Found")
            return redirect('collections')
    else:
        messages.error(request, "No Such Category Found")
        return redirect('collections')

@login_required
def cartpage(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    counts = get_user_counts(user.id)
    total_amount = sum(item.total_cost for item in cart)
    return render(request, "shop/cart.html", {"cart": cart,**counts, 'total_amount': total_amount})

def addtocart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

@login_required
def favviewpage(request):
    user = request.user
    fav = Favourite.objects.filter(user=user)
    counts = get_user_counts(user.id)
    return render(request, "shop/fav.html", {"fav": fav,**counts})

def removefav(request,fid):
  favitem=Favourite.objects.get(id=fid)
  favitem.delete()
  return redirect("/favviewpage")

def removecart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")

def favpage(request):
  if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
      else:
        return JsonResponse({'status':'Login to Add Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Invalid Access'}, status=200)
@login_required
def orderpage(request):
    user = request.user
    orders = Orderrs.objects.filter(user=user).order_by('created_at')
    counts = get_user_counts(user.id)
    return render(request, "shop/orderspage.html", {"orderrs": orders,**counts})

@login_required
def removeorder(request, cid):
    order = get_object_or_404(Orderrs, id=cid, user=request.user)

    if order.status in ['Order Placed', 'Order Shipped']:
        order.delete()  
    return redirect('orderpage')


def addreview(request, *args, **kwargs):
    product_name = kwargs.get('product_name')
    try:
        prod = Product.objects.get(name=product_name)
    except Product.DoesNotExist:
        return redirect('collections')
    if not request.user.is_authenticated:
        request.session['next'] = request.get_full_path()
        return redirect('collections')
    rev = request.POST.get('user-review')
    if not rev:
        return redirect('productdetails', name=prod.category.name, pname=prod.name)
    Reviews.objects.create(content=rev, user=request.user, product=prod)
    return redirect('productdetails', name=prod.category.name, pname=prod.name)

@login_required
def billingpage(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    counts = get_user_counts(user.id)
    total_amount = sum(item.total_cost for item in cart_items)

    #  Place POST logic here
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        if not all([name, email, mobile]):
            messages.error(request, "Name, Email, and Mobile are required.")
            return redirect('billingpage')

        # Save validated billing info to session
        request.session['billing_info'] = {
            'name': name,
            'email': email,
            'address': request.POST.get('address', ''),
            'country': request.POST.get('country', ''),
            'pincode': request.POST.get('pincode', ''),
            'mobile': mobile,
            'ordernotes': request.POST.get('ordernotes', ''),
        }

        request.session.modified = True  # optional but safe
        return redirect('checkoutview')

    # Render form for GET requests
    return render(request, 'shop/billingpage.html', {
        "cart_items": cart_items,
        "total_amount": total_amount,
        **counts
    })    

@login_required  
def checkoutview(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    counts = get_user_counts(user.id)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cartpage')

    billing = request.session.get('billing_info')
    if not billing:
        messages.error(request, "Billing information missing. Please fill out billing form.")
        return redirect('billingpage')
    
    total_amount = sum(item.total_cost for item in cart_items)
    amount_paise = total_amount * 100  # Razorpay expects amount in paise

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        existing_customers = client.customer.all({'email': billing['email']}).get('items', [])
        if existing_customers:
            razorpay_customer = existing_customers[0]
        else:
            razorpay_customer = client.customer.create({
                "name": billing['name'],
                "email": billing['email'],
                "contact": billing['mobile']
            })
    except Exception:
        razorpay_customer = None

    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
        "customer_id": razorpay_customer['id'] if razorpay_customer else None,
        "notes": {
            "user_id": str(user.id)
        }
    }

    razorpay_order = client.order.create(data=order_data)

    return render(request, 'shop/checkout.html', {
        'payment': razorpay_order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': total_amount,
        'customer': billing,
        'cart_items': cart_items,
        **counts
    })

@csrf_exempt
def paymentsuccess(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    # Razorpay POST data
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return HttpResponseBadRequest("Missing payment details.")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        return HttpResponseBadRequest("Signature verification failed.")

    # Fetch payment info
    payment_info = client.payment.fetch(razorpay_payment_id)
    amount = int(payment_info['amount']) // 100

    # Get user
    notes = payment_info.get('notes', {})
    user_id = notes.get('user_id')
    if not user_id:
        return HttpResponseBadRequest("User ID missing in payment notes.")

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found.")

    # Get billing info from session
    billing = request.session.get('billing_info')
    if not billing:
        return HttpResponseBadRequest("Billing info missing from session.")

    # Validate mobile
    raw_mobile = billing.get('mobile', '')
    mobile = re.sub(r'\D', '', str(raw_mobile))
    if not mobile or len(mobile) < 10:
        return HttpResponseBadRequest("Invalid or missing mobile number.")

    mobile = int(mobile)

    # Create orders from cart
    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        Orderrs.objects.create(
            user=user,
            product=item.product,
            name=billing.get('name',''),
            product_qty=item.product_qty,
            address=billing.get('address', ''),
            mobile=mobile,
            status='Order Placed',
            ordernotes=billing.get('ordernotes', '')
        )
    cart_items.delete()

    counts = get_user_counts(user.id)

    return render(request, 'shop/paymentsuccess.html', {
        'order_id': razorpay_order_id,
        'payment_id': razorpay_payment_id,
        'amount': amount,
        **counts
    })