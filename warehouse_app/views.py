from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from .models import User,Inventory,Category,Store,Shipment
from django.http import JsonResponse
import json

import bcrypt

def index(request):
    return render(request,'login_reg.html')

def check_login(request):
    if not User.objects.filter(email = request.POST['email']):
        return JsonResponse({'email_login_msg1': "Account doesnt exist"})
    elif User.objects.filter(email = request.POST['email']):
        if len(request.POST['password']) < 9 :
            return JsonResponse({'email_login_msg2': "Account exists", 'password_login_msg1':"Password is too short"})
        else:
            return JsonResponse({'email_login_msg2': "Account exists", 'password_login_msg2':""})
    else:
        return redirect('/')



def login(request):
    if not User.objects.filter(email = request.POST['email']):
        messages.error(request, "Account doesnt exist")
        return redirect('/')
        
    else:
        if bcrypt.checkpw(request.POST['password'].encode(), User.objects.get(email = request.POST['email']).password.encode()):
            request.session['login_id'] = User.objects.get(email = request.POST['email']).id
            return redirect('/dashboard')

        else:
            messages.error(request, "password is not correct")
            return redirect('/')


def check_register(request):
    errors = User.objects.basic_validator(request.POST, {request.POST['target']})
    if len(errors) > 0 :
        for key, value in errors.items():
            messages.error(request, value)

        return JsonResponse({'message':errors})
    return JsonResponse({'message':'success'})



def register(request):
    errors = User.objects.basic_validator(request.POST, {"email", "first_name", "last_name", "password", "confrim_password"})
    if len(errors) > 0 :
        return redirect('/')
    else:
        hash_pass = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        User.objects.create(first_name = request.POST['first_name'],last_name = request.POST['last_name'],email = request.POST['email'],password = hash_pass)
        request.session['login_id'] = User.objects.last().id
        messages.success(request, "User created Successfully")
        return redirect('/dashboard')
    
# def dashboard(request):
#     if 'category_id' in request.session:
#         if None != Category.objects.filter(id = request.session['category_id']).first():
#             items = Category.objects.get(id = request.session['category_id']).items.all()
#         else:
#             items = Category.objects.first().items.all()

#         cat_id = int(request.session['category_id'])
        
#     else:
#         items = Inventory.objects.all()
#         cat_id = -1
#     current_user = User.objects.get(id  =request.session['login_id'])
#     categories = Category.objects.all()
#     content = {
#         'current_user': current_user,
#         'items' : items,
#         'categories':categories,
#         'cat_id': cat_id,
#     }

def dashboard(request):


    items = Inventory.objects.all()
    current_user = User.objects.get(id  =request.session['login_id'])
    categories = Category.objects.all()
    content = {
        'current_user': current_user,
        'items' : items,
        'categories':categories,
    }
    return render(request,'items.html',content)

def add_item_form(request):
    current_user = User.objects.get(id  =request.session['login_id'])
    content = {
        'current_user': current_user,

    }
    return render(request,'add_item.html',content)

def add_item(request):
    name = request.POST['name']
    count = float(request.POST['quantity'])
    price = request.POST['price']
    description = request.POST['description']
    new_item = Inventory.objects.create(name = name, count = count, price = price, description = description)
    new_item.save()
    return redirect('/dashboard')

# def filter(request):
#     request.session['category_id'] = int(request.POST['filter'])
#     return redirect('/dashboard')


def filter(request):
    request.session['category_id'] = int(request.POST['filter'])
    if None != Category.objects.filter(id = request.session['category_id']).first():
        items = Category.objects.get(id = request.session['category_id']).items.all().values()
    else:
        items = Inventory.objects.all().values()

    return JsonResponse({'items': list(items)})






def item_view(request, id):
    current_user = User.objects.get(id  =request.session['login_id'])
    item = Inventory.objects.get(id = id)
    categories = Category.objects.exclude(items = item)
    shipments = Shipment.objects.filter(item = item)
    print(type(Shipment.objects.get(id =1).quantity))

    content = {
        'current_user': current_user,
        'item' : item,
        'categories':categories,
        'shipments':shipments
    }
    return render(request,'view_items.html',content)

def delete_category_item(request, category_id, item_id):
    item = Inventory.objects.get(id = item_id)
    category = Category.objects.get(id = category_id)
    item.categories.remove(category)
    if request.POST['which_cat_delete'] == 'edit':
        return redirect(f'/item_view/edit_form/{item_id}')
    elif request.POST['which_cat_delete'] == 'view':
        return redirect(f'/item_view/{item_id}')


def add_item_category(request):
    print(request.POST['category_id'])
    category = Category.objects.get(id = request.POST['category_id'])
    item = Inventory.objects.get(id = request.POST['item_id'])
    category.items.add(item)
    return redirect('/dashboard/categories')

def create_category(request):
    new_category = Category.objects.create(name = request.POST['name'])
    new_category.save()
    return redirect('/dashboard/categories')

def delete_category(request,id):
    category = Category.objects.get(id = id)
    category.delete()
    return redirect('/dashboard/categories')

def store_delete(request,id):
    store = Store.objects.get(id = id)
    store.delete()
    return redirect('/dashboard/stores')



def add_category(request,id):
    item = Inventory.objects.get(id = id)
    category = Category.objects.get(id = request.POST['category'])
    item.categories.add(category)
    print(category.id)
    if request.POST['which_form'] == 'view': 
        return redirect(f'/item_view/{id}')
    elif request.POST['which_form'] == 'edit':
        return redirect(f'/item_view/edit_form/{id}')

def item_edit_form(request, id):
    current_user = User.objects.get(id  =request.session['login_id'])
    item = Inventory.objects.get(id = id)
    
    content = {
        'current_user': current_user,
        'item':item,
    }
    return render(request,'edit_item.html',content)
def edit_item(request,id):
    item = Inventory.objects.get(id = id)
    item.name = request.POST['name']
    item.count = float(request.POST['quantity'])
    item.price = request.POST['price']
    item.description = request.POST['description']
    item.save()
    return redirect(f'/item_view/{id}')

def categories(request):
    categories = Category.objects.all()
    dictionary = {}
    for category in Category.objects.all() :
        items = Inventory.objects.exclude(categories = category)
        dictionary[category] = items
    current_user = User.objects.get(id  =request.session['login_id'])
    items = Inventory.objects.all()
    content = {
        'current_user': current_user,
        'categories':categories,
        'dictionary':dictionary,
    }
    return render(request, 'category.html',content)

def create_shipment_form(request):
    items = Inventory.objects.all()
    stores = Store.objects.all()
    user = User.objects.get(id = request.session['login_id'])
    shipments = Shipment.objects.all()
    content = {
        'items':items,
        'current_user':user,
        'stores':stores,
        'shipments':shipments,
    }
    return render(request,'create_shipment.html',content)

def create_shipment(request):
    user = User.objects.get(id = request.session['login_id'])
    item = Inventory.objects.get(id = request.POST['item'])
    store = Store.objects.get(id = request.POST['store'])
    quantity = int(request.POST['qty'])
    shipment = Shipment.objects.create(user = user, item = item, store = store, quantity = quantity )
    shipment.save()
    item.count = item.count - quantity
    item.save()
    return redirect('/create_shipment_form')

def stores(request):
    user = User.objects.get(id = request.session['login_id'])
    stores = Store.objects.all()
    content = {
        'stores':stores,
        'current_user':user
    }
    return render(request,'stores.html',content)

def add_store(request):
    name = request.POST['name']
    location = request.POST['location']
    new_store = Store.objects.create(name = name, location = location)
    new_store.save()
    return redirect('/dashboard/stores')
def logout(request):
    request.session.flush()
    return redirect('/')
def about_us(request):
    return render(request,'about_us.html')