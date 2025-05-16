"""
URL configuration for payroll project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from payroll_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.homepage, name='home'),
    path('home/', views.homepage, name='home'),
    path('super/', views.employee_records),
    path('create-employee/', views.create_employee, name='create_employee'),
    path('get_employee_data/<int:employee_id>/', views.get_employee_data, name='get_employee_data'),
    path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('add_salary_structure/', views.add_salary_structure, name='add_salary_structure'),
    path('get_position_data/<int:position_id>/', views.get_position_data, name='get_position_data'),
    path('update_salary_structure/<int:position_id>/', views.update_salary_structure, name='update_salary_structure'),
    path('delete_salary_structure/<int:position_id>/', views.delete_salary_structure, name='delete_salary_structure'),
    
] 

path('run-java-payroll/', views.run_service_java),



