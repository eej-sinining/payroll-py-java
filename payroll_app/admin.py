from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employee, Payroll, Adjustment, Deduction, Admin  # adjust based on your models

admin.site.register(Employee)
admin.site.register(Payroll)
admin.site.register(Adjustment)
admin.site.register(Deduction)
admin.site.register(Admin)
