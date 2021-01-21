from django.urls import path
from . import views

app_name = 'educator'

urlpatterns = [
    path('', views.edMain, name='edmain'),
    path('edtaskwatch', views.edTaskWatch, name='edtaskwatch'),
    path('edassigntask', views.edAssignTask, name='edassigntask'),
    path('edassigntask_grpsel', views.edAssignTask, name='edassigntask_grpsel'),
    path('edassigntask_taskgrpsel', views.edAssignTask, name='edassigntask_taskgrpsel'),
    path('edassigntask_studsel', views.edAssignTask, name='edassigntask_studsel'),
    path('topics', views.edTaskGroups, name='topics'),
    path('topics/new', views.edTaskNew, name='new_topic'),
    path('templates', views.edTaskTemplates, name='topic_templates'),
    path('eddefinetask', views.edDefineTask, name='eddefinetask'),
    path('edworkontask', views.editTemplate, name='edworkontask'),
    path('edgeneratetask', views.edGenerateTask, name='edgeneratetask'),
    path('edpregeneratedtask', views.edPreGeneratedTask, name='edpregeneratedtask'),
    path('edstatistics', views.edStatistics, name='edstatistics'),
    path('edstats/students', views.edStatsStudents, name='stats_students'),
    path('edstats/student', views.edStatsStudent, name='stats_student'),
    path('edstats/student/detailed', views.edStatsStudentDetailed, name='stats_student_detailed'),
    path('edprofile', views.edProfile, name='edprofile'),
    path('edsupport', views.edSupport, name='edsupport'),
    path('edchangepassword', views.edChangePassword, name='edchangepassword'),
    path('edchp', views.edchp, name='edchp'),
    path('edsendmail', views.edsendmail, name='edsendmail'),
    path('edcreategroup', views.edcreategroup, name='edcreategroup'),
    path('toLogin', views.toLogin, name='toLogin'),
]
