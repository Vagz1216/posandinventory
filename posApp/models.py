import base64
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import UserManager
from django.forms import model_to_dict

# Create your models here.
#1 Currency
class Currency(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    symbol_left = models.CharField(max_length=10, null=True, blank=True)
    symbol_right = models.CharField(max_length=10, null=True, blank=True)
    decimal_place = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
   
   

    def __str__(self):
        return self.title

#2 Store
class Store(models.Model):
    name = models.CharField(max_length=200)
    mobile =models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    store_logo = models.ImageField(upload_to='store') 
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='store')

    def __str__(self):
        return self.name


# Basic Users
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


#3 User model

class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ,
        related_name='customuser_groups'  # specify a custom related name
    )   
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_permissions'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # remove 'email' from the list

    objects = CustomUserManager()
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            # If the user is a superuser, set the store to None so they can choose their own store
            self.store = None
        else:
            # If the user is not a superuser, assign them to a default store
            if not self.pk:  # if this is a new user
                if not self.store:  # if store not assigned, assign default store
                    default_store = Store.objects.first()
                    self.store = default_store

        super().save(*args, **kwargs)
  
#4 ExpenseCategory
class ExpenseCategory(models.Model):
    category_name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    category_details = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.category_name


#5 Expense
class Expense(models.Model):
    ref_no = models.CharField(max_length=100)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    what_for = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    returnables = models.CharField(max_length=100)
    notes = models.TextField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.ref_no

#5 Stocktransfer
class StockTransfer(models.Model):
    ref_no = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    from_store = models.ForeignKey(Store, related_name='stock_transfer_from', on_delete=models.CASCADE)
    to_store = models.ForeignKey(Store, related_name='stock_transfer_to', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.ref_no


#6 Brand
class Brand(models.Model):
    name = models.CharField(max_length=200)
    brand_details = models.TextField(max_length=300)
    brand_image = models.ImageField(upload_to='brand') 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    store = models.ForeignKey(Store, on_delete=models.CASCADE,null=True, blank=True )

    def __str__(self):
        return self.name



#7 Category
class Category(models.Model):
    name = models.CharField(max_length=200)
    parent_id = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField(max_length=300)
    brand_image = models.ImageField(upload_to='category') 
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
 

    def __str__(self):
        return self.name

#8 Supplier
class Supplier(models.Model):
    sup_name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)
    sup_mobile = models.CharField(max_length=20)
    sup_email = models.EmailField()
    gtin = models.CharField(max_length=14, null=True, blank=True)
    sup_address = models.TextField()
    sup_city = models.CharField(max_length=200)
    sup_state = models.CharField(max_length=200)
    sup_country = models.CharField(max_length=200)
    sup_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # If the instance doesn't have a primary key, it's being created for the first time
           
            self.code_name = self.sup_name[:3].upper() + str(Supplier.objects.count() + 1).zfill(4)
        super().save(*args, **kwargs)


    


    def __str__(self):
        return self.sup_name

#9 TaxRate
class TaxRate(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = 0
            # Create code name when the tax rate is created
            code_name = f"{self.name[:3]}{self.id:04}"
            self.code_name = code_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#10 Product
class Product(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product') 
    description =  models.TextField(max_length=300)
    price =  models.DecimalField(max_digits=9, decimal_places=2, default=0)
    taxrate = models.ForeignKey(TaxRate, on_delete=models.CASCADE, null=True, blank=True, default=0)
    # tax = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    alert_quantity = models.IntegerField(default=2)
    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=0)
    def save(self, *args, **kwargs):
        self = self.price * (self.taxrate / 100)
        super(Product, self).save(*args, **kwargs)

    
    store = models.ForeignKey(Store, on_delete=models.CASCADE,null=True, blank=True)

    def to_json(self):
        item = model_to_dict(self)
        item['id'] = self.id
        item['text'] = self.name
        item['category'] = self.category.name
        item['image']= base64.b64encode(self.image.read()).decode('utf-8') if self.image else None
        item['quantity'] = 1
        item['total_product'] = 0
        return item

        class Meta:
                # Table's name
                db_table = "Product"


    def price_with_currency(self):
        return f"{self.store.currency.symbol_left}{self.price}"





    # def price_with_currency(self):
    #     return f"{self.currency.symbol_left}{self.price}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # If the instance doesn't have a primary key, it's being created for the first time
            category_name = self.category.name
            self.code = category_name[:3].upper() + self.name[:3].upper() + str(Product.objects.count() + 1).zfill(4)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + '-'+ self.code

#11 Customer
class Customer(models.Model):
    customer_name = models.CharField(max_length=200)
    dob = models.DateField()
    customer_email = models.EmailField()
    # gtin = models.CharField(max_length=14)
    customer_mobile = models.CharField(max_length=20)
    customer_sex = models.CharField(max_length=10)
    customer_age = models.PositiveSmallIntegerField()
    customer_address = models.TextField()
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    def to_select2(self):
        item = {
            "label": self.customer_name,
            "value": self.id
        }
        return item

    def __str__(self):
        return self.customer_name 




#12 Purchase
class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    ref_no = models.UUIDField(default=uuid.uuid4, editable=False)
    purchase_returned = models.PositiveIntegerField(default=0)

    def price_with_currency(self):
        return f"{self.store.currency.symbol_left}{self.price}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase.product.stock += self.quantity
        self.purchase.product.save()

    def update_purchase_returned(self):
        total_returned = self.purchasereturn_set.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
        self.purchase_returned = total_returned
        self.save()

    def __str__(self):
        return self.product.name + " : " + self.supplier
       
#13 ReturnPurchase
class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    return_date = models.DateTimeField(default=timezone.now)
    return_quantity = models.PositiveIntegerField()
    return_reason = models.CharField(max_length=200)
    reference_no = models.UUIDField()


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.purchase.product.stock -= self.quantity
        self.purchase.product.save()




    def __str__(self):
        return str(self.reference_no)


#17 Order
class Order(models.Model):
    ON_HOLD = 'ON_HOLD'
    COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (ON_HOLD, 'On hold'),
        (COMPLETED, 'Completed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    @property
    def cartget__total(self):
        orderitems = self.orderitem_set.all()
        subtotal = sum([item.get_total for item in orderitems])
        total_tax = sum([item.product.price * (item.product.taxrate.rate / 100) * item.quantity for item in orderitems])
        return subtotal + total_tax

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 


#18 OrderItem

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.stock -= self.quantity
        self.product.save()

    def delete(self, *args, **kwargs):
        self.product.stock += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)


    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total 


#14 Sale
class Sale(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    tax_percentage = models.FloatField(default=0)
    amount_payed = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Sales'

    def __str__(self) -> str:
        return "Sale ID: " + str(self.id) + " | Grand Total: " + str(self.grand_total) + " | Datetime: " + str(self.date_added)

    def sum_items(self):
        details = SaleDetail.objects.filter(sale=self.id)
        return sum([d.quantity for d in details])
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     order_items = self.order.orderitem_set.filter(order__status=Order.COMPLETED)
    #     for item in order_items:
    #         item.product.stock -= item.quantity
    #         item.product.save()
    # def __str__(self):
    #     return self.order + " - " + self.customer

#15 SaleReturns

class SalesReturn(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    returned_items = models.ManyToManyField(Product, through='SalesReturnItem')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for item in self.salesreturnitem_set.all():
            item.product.stock += item.quantity
            item.product.save()


class SalesReturnItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    return_order = models.ForeignKey(SalesReturn, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)



#16 Payment methods
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    code_name = models.CharField(max_length=255)
    details = models.TextField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255)
    sort_order = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            # New payment method
            self.code_name = f"{self.name[:3].upper()}{self.pk}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#Inventory
#To edit
# class Inventory(models.Model):
#     product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
#     stock_alert_level = models.PositiveIntegerField()
#     purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     sell_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     store = models.ForeignKey(Store, on_delete=models.CASCADE)

#     def available_units(self):
#         purchased_units = Purchase.objects.filter(product_code=self.product_code) \
#             .aggregate(Sum('quantity'))['quantity__sum'] or 0
#         sold_units = Sale.objects.filter(product_code=self.product_code) \
#             .aggregate(Sum('quantity'))['quantity__sum'] or 0
#         return purchased_units - sold_units

#     def update_purchase_price(self):
#         purchase = Purchase.objects.filter(product_code=self.product_code).latest('id')
#         self.purchase_price = purchase.unit_price
#         self.save()

#     def update_sell_price(self):
#         sale = Sale.objects.filter(product_code=self.product_code).latest('id')
#         self.sell_price = sale.unit_price
#         self.save()
  
#     def __str__(self)
#         return f'{self.product_code} ({self.available_units()} units)'

#Taxrate model


#19 Receipt
class Receipt(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    products = models.ManyToManyField(Product)
    prices = models.TextField(default='')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=50)
    # Other fields...

    def save(self, *args, **kwargs):
        if not self.pk:
            # This is a new instance, so we can fetch the associated Order and Customer objects.
            order = self.order
            customer = order.customer

            # Add the customer to the receipt.
            self.customer = customer

            # Get all the products associated with the order.
            products = Product.objects.filter(orderitem__order=order)

            # Add the products to the receipt.
            self.products.set(products)

            # Get the prices of each product and store them as a string.
            prices = []
            for product in products:
                price = str(product.price)
                prices.append(f'{product.name}: {price}')
            self.prices = ', '.join(prices)

            # Calculate the total tax of the products.
            total_tax = sum([product.price * (product.taxrate.rate / 100) for product in products])

            # Add the total tax to the receipt.
            self.tax = total_tax

            # Get the category of the products.
            category = products[0].category.name if products else ''
            self.category = category

        super().save(*args, **kwargs)



class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, db_column='sale')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, db_column='product')
    price = models.FloatField()
    quantity = models.IntegerField()
    total_detail = models.FloatField()

    class Meta:
        db_table = 'SaleDetails'

    def __str__(self) -> str:
        return "Detail ID: " + str(self.id) + " Sale ID: " + str(self.sale.id) + " Quantity: " + str(self.quantity)



# User

# userProfile

