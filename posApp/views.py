from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from posApp.models import Purchase
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import json
from django.template.loader import get_template
from django.http import HttpResponse
from pos import settings
import os
#receipt
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from decimal import Decimal

# Create your views here.


# login view
class CustomLoginView(LoginView):
    template_name = 'posApp/logintest.html'
    redirect_authenticated_user = True


def login(request):

    return render(request, 'posApp/login.html')


# def calculate_purchase_totals(request):
#     thirty_days_ago = timezone.now() - timedelta(days=30)
#     purchases = Purchase.objects.filter(date__gte=thirty_days_ago)
#     total_purchase_value = purchases.aggregate(Sum('quantity_price'))['quantity_price__sum'] or 0
#     store_currency = request.user.store.currency.symbol_left
#     context = {
#         'total_purchase_value': f"{store_currency}{total_purchase_value:.2f}"
#     }
#     return render(request, 'posApp/index.html', context)


#index


@login_required
def index(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    print(store_id)
    print("nothing")
    if store_id:
        # If store ID is in session, use it to get the store, products, and suppliers
        try:
            store = Store.objects.get(id=store_id)
            products = Product.objects.filter(store=store)
            suppliers= Supplier.objects.filter(store=store)
            supplier_count = suppliers.count()
            brands = Brand.objects.filter(store=store)
            brand_count = brands.count()
            category =  Category.objects.filter(store=store)
            category_count = category.count()
            customers= Customer.objects.filter(store=store)
            customer_count= customers.count()
            ranked_products = sorted(products, key=lambda p: p.stock - p.alert_quantity)[:5]
            # Calculate the total sales for the last 30 days
            today = timezone.now()
            thirty_days_ago = today - timedelta(days=30)
            sales = Sale.objects.filter(store=store, date_added__gte=thirty_days_ago)
            total_sales = sum(Decimal(sale.grand_total-sale.tax_amount) for sale in sales)


             # Calculate the total purchase for the last 30 
             
            today = timezone.now()
            thirty_days_ago = today - timedelta(days=30)
            purchases = Purchase.objects.filter(store=store, date__gte=thirty_days_ago)
            total_purchases = sum(purchase.price*purchase.quantity for purchase in purchases)

             # Calculate the total purchase for the last 30 
             
            current_month_profits = total_sales-total_purchases
            



            


        except Store.DoesNotExist:
            messages.warning(request, 'Invalid store ID in session. Please select a store.')
            return redirect('select_store')
    else:
        # If store ID is not in session, use the store ID associated with the current user
        if request.user.is_superuser:
            messages.warning(request, 'Please select a store.')
            return redirect('select_store')
        else:
            store = request.user.store
            if store:
                products = Product.objects.filter(store=store)
                suppliers = Supplier.objects.filter(store=store)
                
            else:
                messages.warning(request, 'You have not been assigned a store. Please contact an administrator.')
                return redirect('login_view')

    # Render the index page with the store, products, and suppliers
    context = {'store': store, 'products': products, 'suppliers':suppliers,'sales':sales, 'total_sales': total_sales , 'total_purchases': total_purchases, 'current_month_profits': current_month_profits, 'customer_count': customer_count, 'supplier_count': supplier_count, 'brand_count':brand_count, 'category_count':category_count, "ranked_products": ranked_products}
    return render(request, 'posApp/index.html', context)

def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            # Save the new product to the database
            form.save()
            # Redirect the user to a success page
            return render(request, 'posApp/product_list.html')
        else:
            errors = form.errors.as_data() if form.errors else None
            return render(request, 'posApp/add_product.html', {'form': form, 'errors': errors})
    else:
        form = AddProductForm()
    return render(request, 'posApp/add_product.html', {'form': form})


def select_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    request.session['selected_category'] = category.id

def display_products(request):
    selected_category_id = request.session.get('selected_category')
    if selected_category_id:
        selected_category = get_object_or_404(Category, id=selected_category_id)
        products = selected_category.products.all()

# def pos(request):
#     categories=Category.objects.all()
#     # select_category(request, category_id)
#     selected_category_id = request.session.get('selected_category')
#     if selected_category_id:
#         selected_category, products = display_products(request)
#         # Use the selected_category and products variables in your POS logic
#     else:
#         # Handle the case when no category is selected
#         pass


  
#     context = {
#         'categories': categories,
#         # 'products': products,
#         'categories':categories,
#     }
 
    # return render(request, 'posApp/pos.html', context)

#get products
def get_products_with_stock(request):
    store_id = request.session.get('store_id')
    if store_id:
        store = get_object_or_404(Store, pk=store_id)
        products_with_stock = Product.objects.filter(stock__gt=0, store=store)
    else:
        # Get all products with stock
        products_with_stock = Product.objects.filter(stock__gt=0)
        
        # Get all stores that have products with stock and their corresponding products
        stores_with_products = {}
        for product in products_with_stock:
            if product.store not in stores_with_products:
                stores_with_products[product.store] = []
            stores_with_products[product.store].append(product)

        # If there are no available products in the current store, return all products from other stores
        if not stores_with_products:
            stores_with_products = {}
            for store in Store.objects.all():
                if store != current_store:
                    products = Product.objects.filter(stock__gt=0, store=store)
                    if products.exists():
                        stores_with_products[store] = products
            warning = "There are not any available products in our store today. However, here is a list from our other stores"
            return stores_with_products, warning

    return products_with_stock




#search product

def search_product(request, query):
    store_id = request.session.get('store_id')
    if store_id:
        store = get_object_or_404(Store, pk=store_id)
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query),
            stock__gt=0,
            store=store
        )
    else:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query),
            stock__gt=0
        )
    return 






@login_required
def pos(request):
    store_id = request.session.get('store_id')
    if store_id:
        try:
            store = Store.objects.get(id=store_id)
            customers= Customer.objects.filter(store=store)
        except Store.DoesNotExist:
            messages.warning(request, 'Invalid store ID in session. Please select a store.')
            return redirect('select_store')
        
        


        context = {
        
        "customers": [c.to_select2() for c in Customer.objects.all()],
        "store":store,
   
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            # Save the POST arguements
            data = json.load(request)
            store_id = request.session.get('store_id')


            sale_attributes = {
                "customer": Customer.objects.get(id=int(data['customer'])),
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "tax_amount": float(data["tax_amount"]),
                "tax_percentage": float(data["tax_percentage"]),
                "amount_payed": float(data["amount_payed"]),
                "amount_change": float(data["amount_change"]),
                "store" : Store.objects.get(id=store_id)
            }
            try:
                # Create the sale
                new_sale = Sale.objects.create(**sale_attributes)
                new_sale.save()
                # Create the sale details
                products = data["products"]

                for product in products:
                    detail_attributes = {
                        "sale": Sale.objects.get(id=new_sale.id),
                        "product": Product.objects.get(id=int(product["id"])),
                        "price": product["price"],
                        "quantity": product["quantity"],
                        "total_detail": product["total_product"]
                    }
                    sale_detail_new = SaleDetail.objects.create(
                        **detail_attributes)
                    sale_detail_new.save()

                print("Sale saved")

                messages.success(
                    request, 'Sale created succesfully!', extra_tags="success")

            except Exception as e:
                messages.success(
                    request, 'There was an error during the creation!', extra_tags="danger")

        return redirect('sales_list')

    return render(request, "posApp/pos.html", context=context)
# def pos(request):
#     store_id = request.session.get('store_id')
#     if store_id:
#         try:
#             store = Store.objects.get(id=store_id)
#             customers= Customer.objects.filter(store=store)
#         except Store.DoesNotExist:
#             messages.warning(request, 'Invalid store ID in session. Please select a store.')
#             return redirect('select_store')
        
    #     current_store = get_object_or_404(Store, pk=store_id)
    #     products_with_stock, warning = get_products_with_stock(request)
    # else:
    #     current_store = None
    #     products_with_stock = get_products_with_stock(request)

    # if request.method == 'POST':
    #     search_query = request.POST.get('search_query')
    #     if search_query:
    #         products = search_product(request, search_query)
    #         return render(request, 'posApp/search_results.html', {'products': products})
    # context = {
    #       "customers": [c.to_select2() for c in Customer.objects.filter(store=store)]

    #     'products_with_stock': products_with_stock,
    #     'warning': warning,
    # }


    # return render (request, 'posApp/pos.html', context)

#select_store

# def select_store(request, store_id=None):
#     if request.user.is_superuser:
#         stores = Store.objects.all()
#         if store_id:
#             request.session['selected_store_id'] = store_id
#         selected_store_id = request.session.get('selected_store_id')
#         context= {'stores': stores, 'selected_store_id': selected_store_id}
#         return render(request, 'posApp/select_store.html', context)
#     else:
#         return redirect('index')

def select_store(request):
    if request.method == 'POST':
        store_id = request.POST.get('store_id')
        request.session['store_id'] = store_id
        print(store_id)
        return redirect('index')

    stores = Store.objects.all()
    context = {
        'stores': stores,
    }

    return render(request, 'posApp/select_store.html', context)


# def select_store(request):
#     stores = Store.objects.all()
#     context = {'stores': stores}
#     return render(request, 'posApp/select_store.html', context)

# get products 

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def GetProductsAJAXView(request):
    if request.method == 'POST':
        
        if is_ajax(request=request):
            store_id = request.session.get('store_id')
            store = Store.objects.get(id=store_id)
            data = []

            products = Product.objects.filter(
                name__icontains=request.POST['term'], store=store)
            for product in products[0:10]:
                item = product.to_json()
                data.append(item)

            return JsonResponse(data, safe=False)

def SalesListView(request):
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
    context = {
        # "active_icon": "sales",
        "sales": Sale.objects.filter(store=store),
        "salesdetails": SaleDetail.objects.filter(store=store)
        
    }
    return render(request, "posApp/sales.html", context=context)


def SalesDetailsView(request, sale_id):
    """
    Args:
        sale_id: ID of the sale to view
    """
    if sale_id:
        # Get tthe sale
        sale = Sale.objects.get(id=sale_id)
      

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            # "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "posApp/sales_details.html", context)
    else:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales_list')

# receipt
def ReceiptPDFView(request, sale_id):
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
    """
    Args:
        sale_id: ID of the sale to view the receipt
    """
    # Get the sale
    sale = Sale.objects.get(id=sale_id)
    

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    # Render the template with the sale and details
    template = get_template("posApp/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details,
        'store': store
    }
    html_template = template.render(context)

    # Generate the PDF using xhtml2pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=sales_receipt_{sale_id}.pdf"

    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html_template.encode("UTF-8")), pdf_file)

    response.write(pdf_file.getvalue())
    pdf_file.close()

    return response



#Inventory 

def inventory(request):
    store_id = request.session.get('store_id')
    if store_id:
        try:
            store = Store.objects.get(id=store_id)
            products= Product.objects.filter(store=store)
        except Store.DoesNotExist:
            messages.warning(request, 'Invalid store ID in session. Please select a store.')
            return redirect('select_store')

        context = {
        
        "products": products
     
    }
    return render (request, "posApp/inventory.html",context)




@login_required
def ProductsAddView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  

    


    context = {

        "product_status": Product.status.field.choices,
        "categories": Category.objects.all().filter(status="ACTIVE"),
        'products' : Product.objects.filter(store=store),
        'suppliers': Supplier.objects.filter(store=store), 
        'brands': Brand.objects.filter(store=store),
        'taxrates': TaxRate.objects.all()  


  
    }
    

    if request.method == 'POST':
        # Save the POST arguements
        data = request.POST
        image = request.FILES['product_image'] 

        attributes = {
            "name": data['name'],
            "code": data['code'],
            "category": Category.objects.get(id=data['category']),
            "supplier": Supplier.objects.get(id=data['supplier']),
            "brand" : Brand.objects.get(id=data['brand']),
            "image":image,
            "description": data['description'],
            "price": data['price'],
            "taxrate": TaxRate.objects.get(id=data['taxrate']),
            "alert_quantity": data['alert_quantity'],
            "status": data['state'],
            "store": Store.objects.get(id=store_id),



         
        }

        # Check if a product with the same attributes exists
        if Product.objects.filter(**attributes).exists():
            messages.error(request, 'Product already exists!',
                           extra_tags="warning")
            return redirect('products_add')

        try:
            # Create the product
            new_product = Product.objects.create(**attributes)

            # If it doesn't exists save it
            new_product.save()

            messages.success(request, 'Product: ' +
                             attributes["name"] + ' created succesfully!', extra_tags="success")
            return redirect('products_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('products_add')

    return render(request, "posApp/products_add.html", context=context)



def ProductsListView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  
    context = {

        "products": Product.objects.filter(store=store)
        }
    return render(request, "posApp/product_list.html", context=context)



def ProductsUpdateView(request, product_id):
     # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
    """
    parameter:
        product_id : The product's to be updated
    """

    # Get the product
    try:
        # Get the product to update
        product = Product.objects.get(id=product_id)
    except Exception as e:
        messages.success(
            request, 'There was an error trying to get the product!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')

    context = {
        # "active_icon": "products",
        "product_status": Product.status.field.choices,
        "categories": Category.objects.all().filter(status="ACTIVE"),
        'products' : Product.objects.filter(store=store),
        'suppliers': Supplier.objects.filter(store=store), 
        'brands': Brand.objects.filter(store=store),
        'taxrates': TaxRate.objects.all(),
        'product':product
    }

    if request.method == 'POST':
        try:
            # Save the POST arguements
            data = request.POST
            image = request.FILES['product_image'] 


            attributes = {
                "name": data['name'],
                "code": data['code'],
                "category": Category.objects.get(id=data['category']),
                "supplier": Supplier.objects.get(id=data['supplier']),
                "brand" : Brand.objects.get(id=data['brand']),
                "image":image,
                "description": data['description'],
                "price": data['price'],
                "taxrate": TaxRate.objects.get(id=data['taxrate']),
                "alert_quantity": data['alert_quantity'],
                "status": data['state'],
                "store": Store.objects.get(id=store_id),

            }

            # Check if a product with the same attributes exists
            if Product.objects.filter(**attributes).exists():
                messages.error(request, 'Product already exists!',
                               extra_tags="warning")
                return redirect('products_add')

            # Get the product to update
            product = Product.objects.filter(
                id=product_id).update(**attributes)

            product = Product.objects.get(id=product_id)

            messages.success(request, '¡Product: ' + product.name +
                             ' updated successfully!', extra_tags="success")
            return redirect('products_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the update!', extra_tags="danger")
            print(e)
            return redirect('products_list')

    return render(request, "posApp/product_update.html", context=context)



@login_required
def PurchasesAddView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  

    


    context = {

        # "product_status": Product.status.field.choices,
        
        'products' : Product.objects.filter(store=store),
        'suppliers': Supplier.objects.filter(store=store), 
       

  
    }
    

    if request.method == 'POST':
        # Save the POST arguements
        data = request.POST
      

        attributes = {
            "product": Product.objects.get(id=data['product']),
            "supplier": Supplier.objects.get(id=data['supplier']),
            'quantity':data['quantity'],
            "price": data['price'],
            "store": Store.objects.get(id=store_id),



         
        }

        # Check if a product with the same attributes exists
        # if Product.objects.filter(**attributes).exists():
        #     messages.error(request, 'Product already exists!',
        #                    extra_tags="warning")
        #     return redirect('products_add')

        try:
            # Create the product
            new_purchase = Purchase.objects.create(**attributes)

            # If it doesn't exists save it
            new_purchase.save()

            messages.success(request, 'Purchase created succesfully!', extra_tags="success")
            return redirect('purchase_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('add_purchases')

    return render(request, "posApp/add_purchase.html", context=context)


def PurchaseListView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  
    context = {

        "purchases": Purchase.objects.filter(store=store)
        }
    return render(request, "posApp/purchase_list.html", context=context)




@login_required
def CustomerAddView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  

    


    context = {

        # "product_status": Product.status.field.choices,
        # "categories": Category.objects.all().filter(status="ACTIVE"),
        # 'customers' : Customer.objects.filter(store=store),
        # 'suppliers': Supplier.objects.filter(store=store), 
        # 'brands': Brand.objects.filter(store=store),
        # 'taxrates': TaxRate.objects.all()  


  
    }
    

    if request.method == 'POST':
        # Save the POST arguements
        data = request.POST


        attributes = {
            "name": data['name'],
            "dob": data['dob'],
            "customer_email": data['customer_email'],
            "customer_mobile": data['customer_mobile'],
            "customer_sex": data['customer_sex'],
            "customer_address": data['customer_address'], 
            "store": Store.objects.get(id=store_id),
        }

        # Check if a customer with the same attributes exists
        if Customer.objects.filter(**attributes).exists():
            messages.error(request, 'Customer already exists!',
                           extra_tags="warning")
            return redirect('add_customer')

        try:
            # Create the product
            new_customer = Customer.objects.create(**attributes)

            # If it doesn't exists save it
            new_customer.save()

            messages.success(request, 'Customer: ' +
                             attributes["name"] + ' created succesfully!', extra_tags="success")
            return redirect('add_customer')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('add_customer')

    return render(request, "posApp/add_customer.html", context=context)



def CustomerListView(request):
    # Check if store ID is in session
    store_id = request.session.get('store_id')
    store = Store.objects.get(id=store_id)
  
    context = {

        "customers": Customer.objects.filter(store=store)
        }
    return render(request, "posApp/customer_list.html", context=context)


def ProductsDeleteView(request, product_id):
    """
    Args:
        product_id : The product's ID that will be deleted
    """
    try:
        # Get the product to delete
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, '¡Product: ' + product.name +
                         ' deleted!', extra_tags="success")
        return redirect('products:products_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('products_list')








