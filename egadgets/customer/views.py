from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import TemplateView,ListView,DetailView
from accounts.models import Products,Cart,Orders
from django.contrib import messages
from django.core.mail import send_mail
# Create your views here.


def signin_required(fn):
    def inner(request,*args,**kw):
        if request.user.is_authenticated:
            return fn(request,*args,**kw)
        else:
            messages.error(request,'Please login First!!')
            return redirect('login')
    return inner


class CustomerHomeView(TemplateView):
    template_name='home.html'

class ProductListView(ListView):
    template_name='productlist.html'
    queryset=Products.objects.all()
    context_object_name='products'  # key name
    def get_queryset(self):
        cat=self.kwargs.get('cat')
        return self.queryset.filter(category=cat)
    
class ProductDetailView(DetailView):
    template_name='productdetail.html'
    queryset=Products.objects.all()
    context_object_name='product'
    pk_url_kwarg='id' 

def addToCart(request,*args,**kwargs):
    try:
        pid=kwargs.get('id')
        product=Products.objects.get(id=pid)
        user=request.user
        cartcheck=Cart.objects.filter(product=product,user=user).exists()
        if cartcheck:
            cartitem=Cart.objects.get(product=product,user=user)
            cartitem.quantity+=1
            cartitem.save()
            messages.success(request,'Cart Item Quantity Increased!!')
            return redirect('customerhome')
        else:
            Cart.objects.create(product=product,user=user)
            messages.success(request,f'{product.title} Added To Cart!!')
            return redirect('customerhome')
    except Exception as e:
        messages.warning(request,'Something went wrong!!!')
        return redirect('customerhome')
    
class CartListView(ListView):
    template_name='cartlist.html'
    queryset=Cart.objects.all()
    context_object_name='carts'
    def get_queryset(self):
        qs=self.queryset.filter(user=self.request.user)
        return qs
    
def IncreaseQuantity(request,*args,**kwargs):
    try:
        cid=kwargs.get('id')
        cart=Cart.objects.get(id=cid)
        cart.quantity+=1
        cart.save()
        return redirect('cartlist')
    except:
        messages.warning(request,'Something went wrong!!')
        return redirect('cartlist')
    
def decreaseQuantity(request,*args,**kwargs):
    try:
        cid=kwargs.get('id')
        cart=Cart.objects.get(id=cid)
        if cart.quantity==1:
            cart.delete()
        else:   
            cart.quantity-=1
            cart.save()
        return redirect('cartlist')
    except:
        messages.warning(request,'Something went wrong!!')
        return redirect('cartlist')
    
def deleteCartItem(request,**kwargs):
    try:
        cid=kwargs.get('id')
        cart=Cart.objects.get(id=cid)
        cart.delete()
        messages.success(request,'Item removed from cart!!')
        return redirect('cartitem')
    except:
        messages.warning(request,'Something went wrong!!')
        return redirect('cartlist')
    
def placeorder(request,**kw):
    try:
        cid=kw.get('id')
        cart=Cart.objects.get(id=cid)
        Orders.objects.create(product=cart.product,user=request.user,quantity=cart.quantity)
        cart.delete()

       # email sending
        subject='Egadgets Order Notification'
        msg=f'Order for {cart.product.title} is placed!!'
        f_rom='tcsahla@gmail.com'
        to_id=request.user.email
        send_mail(subject,msg,f_rom,{to_id},fail_silently=True)

        messages.success(request,f'{cart.product.title}\'s Order Placed!!')
        return redirect('cartitem')
    except Exception as e:
        print(e)
        messages.warning(request, 'Something went wrong!!')
        return redirect('cartlist')

class OrderListView(ListView):
    template_name='orderlist.html'
    queryset=Orders.objects.all()
    context_object_name='orders'
    def get_queryset(self):
        qs=self.queryset.filter(user=self.request.user)
        return qs
    
def CancelOrder(request,**kwargs):
    try:
        oid=kwargs.get('id')
        order=Orders.objects.get(id=oid)
        order.status='cancelled'
        order.save()
        messages.success(request,'Order cancelled!!')
        return redirect('orderlist')
    except:
        messages.warning(request,'Something went wrong!!')
        return redirect('orderlist')