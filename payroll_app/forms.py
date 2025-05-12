from django import forms
from .models import Employee
from django.contrib.auth.hashers import make_password

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    is_active = forms.BooleanField(initial=True, required=False)
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'hourly_rate', 'standard_hours', 'contact']
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError("Password must contain at least one special character.")
        return password
        
class loginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    