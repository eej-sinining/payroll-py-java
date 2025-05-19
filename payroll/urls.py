from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from payroll_app import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', views.home_page, name='home-redirect'),
    path('home/', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Dashboards
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Employee management
    path('employee-records/', views.employee_records, name='employee_records'),
    path('create-employee/', views.create_employee, name='create_employee'),
    path('employees/<int:employee_id>/', views.get_employee_data, name='get_employee_data'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    # Salary structure
    path('add-salary-structure/', views.add_salary_structure, name='add_salary_structure'),
    
    # Java service
    path('run-java-payroll/', views.run_service_java, name='run_java_payroll'),

    # Attendance
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('time-in/', views.time_in, name='time_in'),
    path('time-out/', views.time_out, name='time_out'),

    # Payroll
    path('get-payroll-details/<int:payroll_id>/', views.get_payroll_details, name='get_payroll_details'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)