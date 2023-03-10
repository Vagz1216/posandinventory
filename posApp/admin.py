from django.contrib import admin
from .models import*
from .forms import*
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.hashers import make_password

# Register your models here.
class PosAdminArea(admin.AdminSite):
    site_header = "Pos Admin Area"
    login_template = 'posApp/admin/login.html'

pos_site = PosAdminArea(name='PosAdmin')

class ProductAdmin(admin.ModelAdmin):
    form = AddProductForm


# pos_site.register(Product)
class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        """
        Hash the password before saving the user model.
        """
        password = form.cleaned_data.get('password')
        if password:
            obj.password = make_password(password)
        obj.save()


admin.site.register(CustomUser, UserAdmin)




admin.site.register(Product, ProductAdmin)
admin.site.register(Brand)
admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Customer)
admin.site.register(Supplier)
admin.site.register(Purchase)
admin.site.register(PurchaseReturn)
admin.site.register(Sale)
admin.site.register(SalesReturn)
admin.site.register(Currency)
admin.site.register(Receipt)
# admin.site.register(CustomUser)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(StockTransfer)
admin.site.register(TaxRate)
admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(OrderItem)





