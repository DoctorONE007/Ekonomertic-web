from django.urls import path
from . import views
app_name = 'login'

urlpatterns = [
    path('overlook', views.main, name='main'),
    path('educators', views.educators, name='educators'),
    path('studentgroups', views.studentgroups, name='studentgroups'),
    path('students', views.students, name='students'),
    path('', views.loginPage, name='authorise'),
    path('authorize', views.authorize, name='logcheck'),
]
