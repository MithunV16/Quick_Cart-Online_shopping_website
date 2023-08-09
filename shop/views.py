from django.db.models.fields import CommaSeparatedIntegerField
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http.response import HttpResponse
from django.contrib import messages
from math import ceil
import io
import json


from E_Commerce.settings import MEDIA_ROOT
from shop.models import Product
from shop.models import Contact
from shop.models import Checkout, Tracker,productComments,Cartrecord
# from shop.templatetags import extra


def loadAllProducts(): 
    allProds = []
    catprods = Product.objects.values('category')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1, nSlides), nSlides])
    return {'allProds': allProds}


def load_cart(request,params):
    if request.user.is_authenticated:
        try:
            # fetching the cart details of the user
            param_cart=Cartrecord.objects.get(cart_user=request.user)
        except:
            object_cart=Cartrecord(cart_user=request.user)
            object_cart.save()
            param_cart=object_cart
        # passing the object containing the details of cart along with its its length 
        params['cart']=param_cart
        params['cart_length']=len(param_cart.json_data)
    return params


def keymatch(item,key):
    if key in item.product_name.lower() or key in item.category.lower() or key in item.subcategory.lower() or key in item.desc.lower():
        return True
    else:
        return False


def index(request):
    params=loadAllProducts()
    params=load_cart(request,params)
    #getting the data about user's device type
    user_agent=request.META['HTTP_USER_AGENT']
    if('Mobile' in user_agent):
        params['Mobile']=True
    else:
        params['Mobile']=False
    return render(request, "shop/index.html", params)


def tracker(request):
    params={}
    if request.user.is_authenticated:
        orders_list=[]
        checkout=Checkout.objects.filter(user=request.user)
        for order in checkout:
            track=Tracker.objects.filter(user=request.user,order_id=order.order_id).order_by('date')
            orders_list.append([order,track])
        params['orders_list']=orders_list
    params=load_cart(request,params)
    return render(request, "shop/tracker.html",params)


def checkout(request):
    params={}
    if(request.method == "POST"):
        name = request.POST.get('name') #instead can use request.POST['name'] 
        email = request.POST.get('email')
        address = request.POST.get('address1')+" "+request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phoneNumber = request.POST.get('phone')
        productJson = request.POST.get('itemsJson')
        if(len(productJson)>3):
            #saving the details of shipping
            checkout = Checkout(user=request.user,name=name, email=email, address=address, city=city, state=state,zip_code=zip_code, 
                                                                                    phoneNumber=phoneNumber, productJson=productJson)
            checkout.save()
            
            # initiating the processof order tracking
            orderTracker = Tracker(order_id=checkout.order_id,user=request.user,desc="Order has been placed")
            orderTracker.save()

            #erasing the cart data after sucessfully placing the order 
            cart_record=Cartrecord.objects.get(cart_user=request.user)
            cart_record.json_data="0"
            cart_record.save()

            messages.success(request, 'Order has been placed successfully.Please track your orders in the tracker section')
        else:
            messages.error(request, 'Your cart is Empty!')
    params=load_cart(request,params)
    return render(request, "shop/checkout.html", params)


def contact(request):
    if(request.method == "POST"):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phoneNumber = request.POST.get('phoneNumber')
        desc = request.POST.get('desc')
        contact = Contact(name=name, email=email,
                          phoneNumber=phoneNumber, desc=desc)
        contact.save()
    params={}
    params=load_cart(request,params)
    return render(request, "shop/contact.html",params)


def productView(request, myid):
    displayproducts = Product.objects.filter(id=myid)#gets the list of products as query sets 
    params = {'product': displayproducts[0]}


    #post request is for adding the comments to database
    if request.method=="POST" :
        comment=request.POST['comment']#here comment is used to catch both comments and replays and its differentiated with the help of parentId
        productid=request.POST['productid']
        parentid=request.POST['parentId']
        user=request.user
        product=Product.objects.get(id=productid)#gets the item directly

        if(len(comment.strip())!=0):
            if parentid=="":
                pcomments=productComments(comment=comment,product=product,user=user)
            else:
                parent=productComments.objects.get(comment_id=parentid)
                pcomments=productComments(comment=comment,product=product,user=user,parent=parent)
            pcomments.save()
        else:
            messages.warning('Please enter valid comment')
    #extracting the comment and replies from the database and differentiating it
    comments=productComments.objects.filter(product=displayproducts[0],parent=None)
    replies=productComments.objects.filter().exclude(parent=None)
    repliesDict={}
    #arranges the replay with their parent comment in a dictionary
    for reply in replies:
        if(reply.parent.comment_id not in repliesDict):
            repliesDict[reply.parent.comment_id]=[reply]
        else:
            repliesDict[reply.parent.comment_id].append(reply)

    params['comments']=comments
    params['repliesDict']=repliesDict
    params=load_cart(request,params)
    return render(request, "shop/productView.html", params)


def search(request):
    key=request.POST.get('search')
    if(key==None or key.split()==[]):
        params=loadAllProducts()
        messages.error(request,'Please enter valid keywords')
    else:
        allProds = []
        catprods = Product.objects.values('category')
        # aggregating the category of the products
        cats = {item['category'] for item in catprods}
        for cat in cats:
            prodtemp = Product.objects.filter(category=cat)
            prod=[item for item in prodtemp if keymatch(item,key.lower())]
            n = len(prod)
            if(n!=0):
                nSlides = n//4 + ceil((n/4)-(n//4))
                allProds.append([prod, range(1, nSlides), nSlides])

        if(len(allProds)==0):
            messages.error(request,'No match found, Please try different keyword')
            params=loadAllProducts()
            params=load_cart(request,params)
            #getting the data about user's device type
            user_agent=request.META['HTTP_USER_AGENT']
            if('Mobile' in user_agent):
                params['Mobile']=True
            else:
                params['Mobile']=False
            return render(request, "shop/index.html", params)
        params = {'allProds': allProds}
    params=load_cart(request,params)
    #getting the data about user's device type
    user_agent=request.META['HTTP_USER_AGENT']
    if('Mobile' in user_agent):
        params['Mobile']=True
    else:
        params['Mobile']=False
    return render(request, "shop/index.html", params)


def signup(request):
    flag=0
    if(request.method=='POST'):
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        currentPath=request.POST['currentPathsignIn']

        if len(username)<3 or len(username)>20:
            messages.warning(request, 'Username is either too long or too short')
            flag=1

        if not username.isalnum():
            messages.warning(request, 'Username should contain either alphabets or numerics')
            flag=1
        if pass1!=pass2:
            messages.warning(request, 'Password is not matching')
            flag=1
        
        if flag==1:
            return redirect(currentPath)
        else:
            newUser=User.objects.create_user(username,email,pass1)
            newUser.first_name=fname
            newUser.last_name=lname
            newUser.save()
            messages.success(request, 'Successfully created account')
            login(request,newUser)
            return redirect(currentPath)
    else:
        return HttpResponse('Not Found')


def userLogin(request):
    if (request.method=="POST"):
        username=request.POST['loginusername']
        userpass=request.POST['loginpass']
        currentPathlogIn=request.POST['currentPathlogIn']
        user=authenticate(request,username=username,password=userpass)
        if user is None:
            messages.error(request, 'Invalid credentials, Please try again')
            return redirect(currentPathlogIn)
        else:
            login(request,user)
            messages.success(request, 'Successfully Logged in')
            return redirect(currentPathlogIn)
    return HttpResponse('404 - Not found')


def userLogout(request):
    if request.method=="POST":
        currentPath=request.POST['currentPath']
    logout(request)
    messages.info(request, 'Successfully Logged out')
    return redirect(currentPath)


#updates the cart asynchronously
@csrf_exempt
def updateCart(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            json_cart_data=request.body
            stream=io.BytesIO(json_cart_data)
            json_cart_object=JSONParser().parse(stream)
            json_cart_string=json.dumps(json_cart_object)
            try:
                cart_object=Cartrecord.objects.get(cart_user=request.user)
                cart_object.json_data=json_cart_string
                cart_object.save()
            except:
                cart_object=Cartrecord(cart_user=request.user)
                cart_object.save()
    return HttpResponse("successfully updated")
