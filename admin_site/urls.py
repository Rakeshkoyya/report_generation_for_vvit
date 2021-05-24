from . import views
from django.urls import path

urlpatterns = [
    path('', views.home,name='home'),
    path('admin_entry',views.admin_entry, name='admin_entry'),
    path('report', views.report,name='report'),
    path('download', views.download,name='download'),
    path('admin/admin_entry', views.admin_entry,name='admin_entry'),
    path('admin/logout', views.logout,name='logout'),
    path('admin/',views.admin,name='admin'),
    path('help',views.help,name='help'),

]
