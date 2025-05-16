from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Position(models.Model):
    name = models.CharField(max_length=30, unique=True)
    standard_hours = models.IntegerField() 
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional fields you might want
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.CharField(max_length=20)
    
    # You might want to add these fields for flexibility
    is_active = models.BooleanField(default=True)
    date_hired = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def position_name(self):
        return self.position.name if self.position else "No Position"

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    cutoff_start = models.DateField()
    cutoff_end = models.DateField()
    total_hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

class Adjustment(models.Model):
    ADJUSTMENT_CHOICES = [
        ('Overtime', 'Overtime'),
        ('Absence', 'Absence'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_CHOICES)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    cutoff_start = models.DateField()
    cutoff_end = models.DateField()

class Deduction(models.Model):
    DEDUCTION_CHOICES = [
        ('Tax', 'Tax'),
        ('SSS', 'SSS'),
        ('Pag-IBIG', 'Pag-IBIG'),
    ]
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    deduction_type = models.CharField(max_length=20, choices=DEDUCTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    userID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    employeeID = models.ForeignKey('Employee', null=True, on_delete=models.SET_NULL)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'