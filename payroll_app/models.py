from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

class Position(models.Model):
    name = models.CharField(
        max_length=30, 
        unique=True,
        help_text="Official job title/position name"
    )
    standard_hours = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(1)],
        help_text="Standard weekly working hours for this position"
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Monthly base salary for this position"
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        # default=0,
        validators=[MinValueValidator(0)],
        help_text="Standard monthly bonus for this position"
    )
    deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        # default=0,
        validators=[MinValueValidator(0)],
        help_text="Standard monthly deductions for this position"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed job description and responsibilities"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this position is currently available"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'

    def __str__(self):
        return self.name

    def monthly_gross_salary(self):
        """Calculate total monthly gross salary (base + bonus)"""
        return self.base_salary + self.bonus


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.CharField(max_length=20)
    standard_hours = models.IntegerField(default=40) #temporary, wla ko ka gets ani?
    
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
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'payroll_app_admin'  # Ensures Django uses the correct table name

    def __str__(self):
        return self.username
    

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    userID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    employeeID = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.SET_NULL)

    objects: CustomUserManager = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.username

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"