import os
import subprocess
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import Employee, CustomUser, Position, Admin
from .forms import LoginForm, EmployeeForm

# Constants
JAVA_DIR = os.path.join(os.path.dirname(__file__), 'java_files')
JAVA_FILE = 'service.java'
JAVA_CLASS = 'service'
PROCESS_TIMEOUT = 10

@require_http_methods(["GET"])
def link(request):
    """Route users based on their authentication status and role."""
    if not request.session.get('is_logged_in'):
        print("DEBUG: User is not logged in.")
        return redirect('home')

    username = request.session.get('username')
    print("DEBUG: Username from session:", username)

    try:
        # Print all admin usernames from the DB
        print("DEBUG: All admin usernames in DB:")
        for admin in Admin.objects.all():
            print(f"- {admin.username}")

        # Check if this session username is an admin
        if Admin.objects.filter(username=username).exists():
            print("DEBUG: Matched admin, redirecting to admin_dashboard")
            return redirect('admin_dashboard')
        else:
            print("DEBUG: Not an admin, redirecting to employee_dashboard")
            return redirect('employee_dashboard')

    except Exception as e:
        print("DEBUG: Exception occurred in link():", str(e))
        return redirect('home')

@require_http_methods(["GET"])
def home_page(request):
    """Render home/landing page."""
    return render(request, 'payroll_app/home.html')

@login_required
def employee_dashboard(request):
    """Render employee dashboard."""
    return render(request, 'payroll_app/employee.html')

@login_required
def admin_dashboard(request):
    """Render admin dashboard."""
    return render(request, 'payroll_app/admin.html')

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if CustomUser.objects.get(username=username).role == 'Admin':
                return redirect('admin_dashboard')
            else:
                return redirect('employee_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return redirect('home')
    
@login_required
@require_http_methods(["GET"])
def employee_records(request):
    """Display all employee records with form for new employees."""
    return render(request, 'payroll_app/Admin.html', {
        'employees': Employee.objects.all().order_by('id'),
        'employee_form': EmployeeForm(),
        'positions': Position.objects.filter(is_active=True).order_by('id')
    })

@login_required
@require_http_methods(["POST"])
def create_employee(request):
    """Create new employee and associated user account."""
    try:
        position = Position.objects.get(
            id=request.POST.get('position'),
            is_active=True
        )
        
        employee = Employee.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            position=position,
            hourly_rate=position.base_salary,
            contact=request.POST.get('contact'),
            is_active=request.POST.get('is_active', 'off') == 'on'
        )
        
        CustomUser.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password'),
            role='employee',
            is_active=request.POST.get('is_active', 'off') == 'on',
            employeeID=employee
        )
        
        return JsonResponse({'success': True})
    
    except Position.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid position'})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'Username exists'})
    except Exception as e:
        Employee.objects.filter(id=getattr(employee, 'id', None)).delete()
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def add_salary_structure(request):
    """Create new salary position structure."""
    try:
        Position.objects.create(
            name=request.POST.get('name'),
            standard_hours=int(request.POST.get('standard_hours', 40)),
            base_salary=Decimal(request.POST.get('base_salary')),
            bonus=Decimal(request.POST.get('bonus', 0)),
            deduction=Decimal(request.POST.get('deduction', 0))
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def run_service_java(request):
    """Compile and execute Java service with security checks."""
    try:
        java_path = os.path.join(JAVA_DIR, JAVA_FILE)
        if not os.path.exists(java_path):
            return HttpResponse('Service not found', status=404)

        # Compile Java
        compile_result = subprocess.run(
            ['javac', JAVA_FILE],
            cwd=JAVA_DIR,
            capture_output=True,
            text=True,
            timeout=PROCESS_TIMEOUT
        )
        if compile_result.returncode != 0:
            return HttpResponse(
                f"Compilation error:\n{compile_result.stderr}",
                status=500
            )

        # Execute Java
        run_result = subprocess.run(
            ['java', JAVA_CLASS] + request.GET.getlist('args', []),
            cwd=JAVA_DIR,
            capture_output=True,
            text=True,
            timeout=PROCESS_TIMEOUT
        )
        return HttpResponse(
            run_result.stdout if run_result.returncode == 0 
            else f"Runtime error:\n{run_result.stderr}",
            status=200 if run_result.returncode == 0 else 500
        )
    except subprocess.TimeoutExpired:
        return HttpResponse('Process timed out', status=500)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@login_required
@require_http_methods(["POST"])
def delete_employee(request, employee_id):
    """Delete employee and associated user account."""
    try:
        employee = Employee.objects.get(id=employee_id)
        CustomUser.objects.filter(employeeID=employee).delete()
        employee.delete()
        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["GET"])
def logout(request):
    """Log out user and clear session."""
    request.session.flush()
    return redirect('home')