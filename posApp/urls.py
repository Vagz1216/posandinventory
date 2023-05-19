from .views import CustomLoginView
from django.urls import path, include
from . import views


#create views here


urlpatterns = [
    path('dashboard', views.index,  name='index' ),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('pos/', views.pos, name='pos'),
    path('select_store/', views.select_store, name='select_store'),
    path('', include('users.urls')),  # replace 'users' with the name of your app containing the login view
     # add a sale
    path("get/", views.GetProductsAJAXView, name="get_products"),
    #inventory 
    path("inventory/",views.inventory, name="inventory"),
    #sals list
    path('sales', views.SalesListView, name='sales_list'),
    # path('addsale/', views.addsale, name='addsale')
    path("details/<str:sale_id>",views.SalesDetailsView, name="sales_details"),
       # Sale receipt PDF
    path("pdf/<str:sale_id>",views.ReceiptPDFView, name="sales_receipt_pdf"),

      # Add product
    path('add', views.ProductsAddView, name='products_add'),
    
     # List products
    path('products', views.ProductsListView, name='products_list'),

    path('update/<str:product_id>',views.ProductsUpdateView, name='products_update'),

       # Delete product
    path('delete/<str:product_id>',views.ProductsDeleteView, name='products_delete'),


   # Add  purchases
    path('purchase', views.PurchasesAddView, name='add_purchases'),

       # List purchase
    path('purchases', views.PurchaseListView, name='purchase_list'),

    # Add  customer
    path('customer', views.CustomerAddView, name='add_customer'),

      #   customer list
    path('customers', views.CustomerListView, name='customer_list'),











]