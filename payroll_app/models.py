from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Employee(models.Model):
    POSITION_CHOICES = [
        ('Admin', 'Admin'),
        ('Mayor', 'Mayor'),
        ('Vice Mayor', 'Vice Mayor'),
        ('Councilor', 'Councilor'),
        ('Mayor\'s Assistant', 'Mayor\'s Assistant'),
        ('Vice Mayor\'s Assistant', 'Vice Mayor\'s Assistant'),
        ('Councilor\'s Assistant', 'Councilor\'s Assistant'),
        ('Security Guard', 'Security Guard'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)  # Increased max_length
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    standard_hours = models.IntegerField()
    contact = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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