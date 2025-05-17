from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from payroll_app import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),  # Added trailing slash for consistency
    
    # Authentication
    path('', views.home_page, name='home-redirect'),  # Main entry point
    path('home/', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),  # Added login URL
    path('logout/', views.logout, name='logout'),
    
    # Dashboards
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Fixed to use admin_dashboard view
    
    # Employee management
    path('employee-records/', views.employee_records, name='employee_records'),  # Better naming
    path('create-employee/', views.create_employee, name='create_employee'),
    path('employees/<int:employee_id>/', views.get_employee_data, name='get_employee_data'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    # Salary structure
    path('add-salary-structure/', views.add_salary_structure, name='add_salary_structure'),
    
    # Java service
    path('run-java-payroll/', views.run_service_java, name='run_java_payroll'),  # Added name parameter
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)