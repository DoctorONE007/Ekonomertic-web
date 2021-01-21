from django.contrib import admin
from .models import Student, TemplateTask, TaskGroup, StudentGroup,GeneratedTask
# Register your models here.
admin.site.register(TemplateTask)
admin.site.register(GeneratedTask)
admin.site.register(Student)
admin.site.register(TaskGroup)
admin.site.register(StudentGroup)