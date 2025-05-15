from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Employee, CustomUser
import re

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        }),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password'
        }),
        required=True,
        help_text="Password must be at least 8 characters, include one number and one special character."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        required=True
    )
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'position',
            'hourly_rate', 'standard_hours', 'contact'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0'
            }),
            'standard_hours': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '168'
            }),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            raise ValidationError("Password is required.")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'\d', password):
            raise ValidationError("Password must include at least one number.")

        if not re.search(r'[^\w]', password):
            raise ValidationError("Password must include at least one special character.")

        validate_password(password)  # Optional: Django’s built-in validators

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data
    
    # def save(self, commit=True):
    #     """Create Employee and associated CustomUser atomically."""
    #     with transaction.atomic():
    #         employee = super().save(commit=False)
    #         if commit:
    #             employee.save()
    #             CustomUser.objects.create_user(
    #                 username=self.cleaned_data['username'],
    #                 password=self.cleaned_data['password'],
    #                 is_active=self.cleaned_data['is_active'],
    #                 role='employee',
    #                 employeeID=employee
    #             )
    #         return employee
    def save(self, commit=True):
        """Create Employee and associated CustomUser atomically."""
        with transaction.atomic():
            employee = super().save(commit=False)

        # Save employee if committing
        if commit:
            employee.save()
            CustomUser.objects.create_user(
                username=self.cleaned_data.get('username'),
                password=self.cleaned_data.get('password'),
                is_active=self.cleaned_data.get('is_active', True),
                role='employee',
                employeeID=employee
            )

        return employee


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            raise ValidationError("Both username and password are required.")

        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Invalid username or password.")

        cleaned_data['user'] = user
        return cleaned_data
