from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, ProductType
from .forms import ProductForm, CategoryForm, ProductTypeForm
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def add_product(request):
    # Her form için bağımsız işleme
    category_form = CategoryForm(request.POST or None)
    product_type_form = ProductTypeForm(request.POST or None)
    product_form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        # Kategori formu işleme
        if 'category_submit' in request.POST and category_form.is_valid():
            category_form.save()
            return redirect('add_product')

        # Ürün tipi formu işleme
        if 'product_type_submit' in request.POST and product_type_form.is_valid():
            product_type_form.save()
            return redirect('add_product')

        # Ürün formu işleme
        if 'product_submit' in request.POST and product_form.is_valid():
            # Formdan seçilen kategori ve ürün tipini al
            category = product_form.cleaned_data['category']
            product_type = product_form.cleaned_data['product_type']
            
            # Ürünü kaydet
            product = product_form.save(commit=False)
            product.category = category
            product.product_type = product_type
            product.save()
            return redirect('add_product')

    return render(request, 'add_product.html', {
        'category_form': category_form,
        'product_type_form': product_type_form,
        'product_form': product_form
    })

def product_list_api(request):
    query = request.GET.get('q')
    page = int(request.GET.get('page', 1))

    product_list = Product.objects.all()
    if query:
        product_list = product_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(product_list, 12)  # Her sayfada 12 ürün

    products = paginator.get_page(page)

    product_data = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'image': product.image.url if product.image else '',
        }
        for product in products
    ]

    return JsonResponse({
        'products': product_data,
        'has_next': products.has_next()
    })

def products(request):
    query = request.GET.get('q')
    product_list = Product.objects.all()

    # Arama sorgusu varsa, filtreleme yap
    if query:
        product_list = product_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Sayfalama yapısı
    paginator = Paginator(product_list, 9)  # Her sayfada 9 ürün
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products.html', {
        'page_obj': page_obj,
        'query': query
    })

def product_detail(request, product_id):
    # Mevcut ürünü al
    product = get_object_or_404(Product, id=product_id)

    # Benzer ürünleri al: Aynı kategori ve ürün tipi üzerinden filtrele
    related_products = Product.objects.filter(
        category=product.category,
        product_type=product.product_type
    ).exclude(id=product.id)[:5]

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

# ---------------------------------

def product_type_products(request, product_type_id):
    product_type = get_object_or_404(ProductType, id=product_type_id)
    products = Product.objects.filter(product_type=product_type)
    return render(request, 'product_type_products.html', {
        'product_type': product_type,
        'products': products
    })

# -------------------------------------

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Your account has been created. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'register.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')