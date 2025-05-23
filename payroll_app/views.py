import re
import json
import os
import subprocess
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Sum
from datetime import time
from datetime import date
from .models import Employee, CustomUser, Position, Attendance, Payroll
from .forms import LoginForm, EmployeeForm

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.conf import settings

def homepage(request):
    """Render the home page with login form"""
    form = LoginForm()
    return render(request, 'payroll_app/home.html', {'form': form})

def login_view(request):
    """Handle user authentication"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('payroll_app:dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
        return render(request, 'payroll_app/home.html', {'form': form})
    return redirect('payroll_app:homepage')

def employee_records(request):
    today = timezone.now().date()
    employees = Employee.objects.all().order_by('id')
    positions = Position.objects.filter(is_active=True).order_by('id')  # Get active positions
    attendance_records = Attendance.objects.select_related('employee').all().order_by('id') 

    present_count = Attendance.objects.filter(status='present').count()
    absent_count = Attendance.objects.filter(status='absent').count()
    late_count = Attendance.objects.filter(status='late').count()

    pending_payrolls = Payroll.objects.filter(status__isnull=True).select_related('employee')
    done_payrolls = Payroll.objects.filter(status='done').select_related('employee')

    pending_count = pending_payrolls.count()
    total_payroll = Payroll.objects.aggregate(total=Sum('overall_pay'))['total'] or 0
    total_deductions = Payroll.objects.aggregate(total=Sum('deductions'))['total'] or 0

    form = EmployeeForm()

    return render(request, 'payroll_app/Admin.html', {
        'employees': employees,
        'employee_form': form,
        'positions': positions,  # Add positions to the context
        'attendance_records': attendance_records,

        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,

        'pending_payrolls': pending_payrolls,
        'done_payrolls': done_payrolls,

        'pending_count': pending_count,
        'total_payroll': total_payroll,
        'total_deductions': total_deductions,
    })

def attendance_summary(request):
    today = timezone.now().date()
    
    # Get all active employees
    all_employees = Employee.objects.filter(is_active=True)
    total_employees = all_employees.count()
    
    # Get today's attendance records
    today_attendance = Attendance.objects.filter(date=today)
    
    # Calculate counts
    present_count = today_attendance.filter(
        time_in__isnull=False,
        time_out__isnull=False,
        time_in__hour__lt=9  # Before 9 AM
    ).count()
    
    late_count = today_attendance.filter(
        time_in__hour__gte=9  # 9 AM or later
    ).count()
    
    # Absent = Total employees - (Present + Late)
    absent_count = total_employees - (present_count + late_count)
    
    context = {
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
    }
    
    return render(request, 'payroll_app/Admin.html', context)

def get_employee_data(request, employee_id):
    try:
        employee = Employee.objects.select_related('position').get(id=employee_id)
        user = CustomUser.objects.get(employeeID=employee)
        
        response_data = {
            'success': True,
            'employee': {
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'contact': employee.contact,
                'hourly_rate': str(employee.hourly_rate),
                'is_active': employee.is_active,
                'position': {
                    'id': employee.position.id if employee.position else None,
                    'name': employee.position.name if employee.position else None,
                    'standard_hours': employee.position.standard_hours if employee.position else None,
                    'base_salary': str(employee.position.base_salary) if employee.position else None,
                } if employee.position else None
            },
            'user': {
                'username': user.username,
                'is_active': user.is_active
            }
        }
        
        return JsonResponse(response_data)
        
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User account not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def update_employee(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=employee_id)
            user = CustomUser.objects.get(employeeID=employee)
            
            # Get new username from form
            new_username = request.POST.get('username')
            
            # Check if username is being changed and if it already exists
            if new_username and new_username != user.username:
                if CustomUser.objects.exclude(id=user.id).filter(username=new_username).exists():
                    return JsonResponse({
                        'success': False, 
                        'error': 'Username already exists'
                    })
            
            # Update basic employee info
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.contact = request.POST.get('contact')
            
            # Update position if changed
            position_id = request.POST.get('position')
            if position_id and position_id != 'none':
                position = Position.objects.get(id=position_id)
                employee.position = position
                employee.hourly_rate = position.base_salary
            elif position_id == 'none':
                employee.position = None
                employee.hourly_rate = None
            
            # Update active status
            employee.is_active = request.POST.get('is_active', 'off') == 'on'
            employee.save()
            
            # Update user account
            user.username = new_username
            user.is_active = employee.is_active
            password = request.POST.get('password')
            if password:  # Only update password if provided
                user.set_password(password)
            user.save()
            
            return JsonResponse({'success': True, 'refresh': True})
            
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid position selected'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Delete the associated CustomUser if it exists
        try:
            custom_user = CustomUser.objects.get(employeeID=employee)
            custom_user.delete()
        except CustomUser.DoesNotExist:
            pass  # No user associated, continue with employee deletion
            
        employee.delete()
        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_employee(request):
    if request.method == 'POST':
        try:
            # Get position instance
            position_id = request.POST.get('position')
            try:
                position = Position.objects.get(id=position_id, is_active=True)
            except Position.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid position selected'})
            
            # Create the Employee - standard_hours now comes from position
            employee = Employee(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                position=position,
                hourly_rate=position.base_salary,  # From position
                contact=request.POST.get('contact'),
                is_active=request.POST.get('is_active', 'off') == 'on'
            )
            employee.save()
            
            # Then create the CustomUser account
            user = CustomUser.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password'),
                role='employee',
                is_active=request.POST.get('is_active', 'off') == 'on',
                employeeID=employee
            )

            return JsonResponse({'success': True})
        except IntegrityError as e:
            if 'employee' in locals():
                employee.delete()
            return JsonResponse({'success': False, 'error': 'Username already exists'})
        except Exception as e:
            if 'employee' in locals():
                employee.delete()
            if 'user' in locals():
                user.delete()
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_attendance_report(request):
    # Validate Java environment first
    java_folder = os.path.join(os.path.dirname(__file__),  'calculation')
    java_file = os.path.join(java_folder, 'service.java')
    
    if not os.path.exists(java_file):
        return JsonResponse({
            'success': False,
            'error': 'Java service not configured. Missing service.java file.'
        }, status=500)

    try:
        # Verify Java is installed
        subprocess.run(['java', '-version'], 
                      check=True,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return JsonResponse({
            'success': False,
            'error': 'Java runtime not found or not working'
        }, status=500)

    try:
        # Compile Java service once at the beginning
        compile_result = subprocess.run(
            ['javac', 'service.java'],
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if compile_result.returncode != 0:
            return JsonResponse({
                'success': False,
                'error': f'Java compilation failed: {compile_result.stderr}'
            }, status=500)

        processed_employees = 0
        errors = []
        
        # Get all active employees with position info
        employees = Employee.objects.filter(is_active=True).select_related('position')
        total_employees = employees.count()

        for employee in employees:
            try:
                # Get attendance records for current month only (adjust as needed)
                attendances = Attendance.objects.filter(employee=employee)
                
                if not attendances.exists():
                    errors.append(f"No attendance records for employee {employee.id}")
                    continue

                # Prepare attendance data string for Java
                attendance_data = []
                for attendance in attendances:
                    time_in = attendance.time_in.strftime("%H:%M") if attendance.time_in else ""
                    time_out = attendance.time_out.strftime("%H:%M") if attendance.time_out else ""
                    attendance_data.append(f"{attendance.date},{time_in},{time_out}")
                
                attendance_str = ";".join(attendance_data)
                
                # Prepare Java arguments with proper validation
                args = [
                    str(employee.id),
                    str(employee.hourly_rate),
                    str(employee.position.bonus if employee.position else 0),
                    str(employee.position.deduction if employee.position else 0),
                    attendance_str
                ]

                # Run Java service with timeout
                run_result = subprocess.run(
                    ['java', 'service'] + args,
                    cwd=java_folder,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15
                )

                if run_result.returncode != 0:
                    errors.append(f"Java error for employee {employee.id}: {run_result.stderr}")
                    continue

                # Parse and validate Java output
                try:
                    result = {}
                    output = run_result.stdout.strip()
                    if not output:
                        raise ValueError("Empty response from Java service")

                    for part in output.split(','):
                        if ':' not in part:
                            continue
                        key, value = part.split(':', 1)
                        result[key.strip()] = value.strip()

                    required_fields = ['employeeId', 'totalHours', 'overallPay', 'deductions']
                    if not all(field in result for field in required_fields):
                        raise ValueError("Missing required fields in Java output")

                    # Create payroll record
                    Payroll.objects.create(
                        employee=employee,
                        total_hours_worked=float(result['totalHours']),
                        overall_pay=float(result['overallPay']),
                        deductions=float(result['deductions']),
                        payment_date=date.today()
                    )
                    processed_employees += 1

                except (ValueError, KeyError) as e:
                    errors.append(f"Data processing error for employee {employee.id}: {str(e)}")

            except Exception as e:
                errors.append(f"Error processing employee {employee.id}: {str(e)}")

        # Prepare response
        response = {
            'success': True,
            'message': f'Successfully processed {processed_employees} of {total_employees} employees',
            'processed': processed_employees,
            'total': total_employees,
        }

        if errors:
            response['warning'] = f'{len(errors)} errors occurred during processing'
            if len(errors) <= 5:  # Don't flood the response with too many errors
                response['errors'] = errors
            else:
                response['error_count'] = len(errors)
                response['sample_errors'] = errors[:3]

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'System error: {str(e)}'
        }, status=500)

def add_salary_structure(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            standard_hours = int(request.POST.get('standard_hours', 40))
            base_salary = Decimal(request.POST.get('base_salary'))
            bonus = Decimal(request.POST.get('bonus', 0))
            deduction = Decimal(request.POST.get('deduction', 0))
            
            # Create new position with salary structure
            Position.objects.create(
                name=name,
                standard_hours=standard_hours,
                base_salary=base_salary,
                bonus=bonus,
                deduction=deduction
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_position_data(request, position_id):
    try:
        position = Position.objects.get(id=position_id)
        
        response_data = {
            'success': True,
            'position': {
                'id': position.id,
                'name': position.name,
                'standard_hours': position.standard_hours,
                'base_salary': str(position.base_salary),
                'bonus': str(position.bonus),
                'deduction': str(position.deduction),
            }
        }
        
        return JsonResponse(response_data)
        
    except Position.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Position not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def update_salary_structure(request, position_id):
    if request.method == 'POST':
        try:
            position = Position.objects.get(id=position_id)
            
            # Update position data
            position.name = request.POST.get('name')
            position.standard_hours = int(request.POST.get('standard_hours', 40))
            position.base_salary = Decimal(request.POST.get('base_salary'))
            position.bonus = Decimal(request.POST.get('bonus', 0))
            position.deduction = Decimal(request.POST.get('deduction', 0))
            
            position.save()
            
            return JsonResponse({'success': True})
            
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Position not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_salary_structure(request, position_id):
    try:
        position = Position.objects.get(id=position_id)
        
        # Check if any employees are using this position
        if Employee.objects.filter(position=position).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Cannot delete this position because it is assigned to one or more employees.'
            })
            
        position.delete()
        return JsonResponse({'success': True})
        
    except Position.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Position not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def process_payroll(request):
    payroll_ids = request.POST.getlist('payroll_ids')
    
    try:
        # Update status of selected payrolls to 'done'
        Payroll.objects.filter(id__in=payroll_ids).update(status='done')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

        
def run_service_java(request):
    """Execute Java service with proper security checks"""
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    # Security: Validate inputs
    try:
        args = [
            request.GET.get('arg1', 'mayor'),
            request.GET.get('arg2', '160'),
            request.GET.get('arg3', '10'),
            request.GET.get('arg4', '2')
        ]
        
        # Validate arguments
        if not all(re.match(r'^[\w\.-]+$', arg) for arg in args):
            raise ValueError('Invalid arguments')

        java_folder = os.path.join(os.path.dirname(_file_), 'java_files')
        java_filename = 'service.java'
        classname = 'service'

        # Security: Restrict file operations to specific directory
        if not os.path.exists(os.path.join(java_folder, java_filename)):
            return HttpResponse('Service not found', status=404)

        # Compile Java
        compile_result = subprocess.run(
            ['javac', java_filename],
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if compile_result.returncode != 0:
            return HttpResponse(
                f"Compilation error:\n{compile_result.stderr}",
                status=500
            )

        # Execute Java
        run_result = subprocess.run(
            ['java', classname] + args,
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if run_result.returncode != 0:
            return HttpResponse(
                f"Runtime error:\n{run_result.stderr}",
                status=500
            )


        return HttpResponse(f"Java Output:\n\n{run_result.stdout}")

    except subprocess.TimeoutExpired:
        return HttpResponse('Process timed out', status=500)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)