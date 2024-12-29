from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('api/products/', views.product_list_api, name='product_list_api'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('add-product/', views.add_product, name='add_product'),

    path('product-type/<int:product_type_id>/', views.product_type_products, name='product_type_products'),

    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
]
