from django.urls import path
from . import views

app_name = 'student'
urlpatterns = [
    path('', views.main, name='main'),
    path('currenttasks', views.currenttasks, name='currenttasks'),
    path('generatetask', views.generatetask, name='generatetask'),
    path('generatetask/find_templates', views.find_templates, name='find_templates'),
    path('generatetask/gen_templates', views.generateManyJobs, name='gen_templates'),
    path('history', views.history, name='history'),
    path('statistics', views.statistics, name='statistics'),
    path('statistics/change_topic', views.change_topic, name='change_topic'),
    path('profile', views.profile, name='profile'),
    path('support', views.support, name='support'),
    path('toLogin', views.toLogin, name='toLogin'),
    path('changepassword', views.ChangePassword, name='changepassword'),
    path('sendmail', views.sendmail, name='sendmail'),
    path('chp', views.chp, name='chp'),
    path('task/<int:task_id>', views.task, name='task'),
    path('task/<int:task_id>/answer_check', views.checkAnswer, name='answer_check'),
]
