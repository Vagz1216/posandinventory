from .views import CustomLoginView
from django.urls import path
from . import views


#create views here


urlpatterns = [
    path('', views.index,  name='index' ),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('pos/', views.pos, name='pos'),
    path('select_store/', views.select_store, name='select_store'),
     # add a sale
    path("get/", views.GetProductsAJAXView, name="get_products"),
    #sals list
    path('sales', views.SalesListView, name='sales_list'),
    # path('addsale/', views.addsale, name='addsale')
    path("details/<str:sale_id>",views.SalesDetailsView, name="sales_details"),
       # Sale receipt PDF
    path("pdf/<str:sale_id>",views.ReceiptPDFView, name="sales_receipt_pdf"),








]