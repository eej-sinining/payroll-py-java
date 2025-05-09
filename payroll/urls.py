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
<<<<<<< HEAD
    path('run-java-payroll/', views.run_service_java),
]
=======
<<<<<<< HEAD
    path('super', views.employee_records),
] 
=======
<<<<<<< HEAD
    path('run-java-payroll/', views.run_service_java),
]
=======
] 
>>>>>>> 7ad9fd606fffea0821edbc7d37ba895fc20046c0
>>>>>>> eb0581bbd4fe90531293b1902b95f12d088c4b40
>>>>>>> 7168faf95103ce4a44cfc924559b66a29b1ed9b0
