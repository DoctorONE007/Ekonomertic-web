import re
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class TemplateTask(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.CharField(default="a", max_length=100)
    description = models.CharField(max_length=1000)

    # path to generator
    generatorPath = models.FilePathField(default='asd', editable=False)
    generatorText = models.CharField(blank=True, max_length=1000)
    # path to program, which calculates answer
    checkerPath = models.FilePathField(default='asd', editable=False)
    checkerText = models.CharField(blank=True, max_length=1000)
    difficulty = models.IntegerField(default=1)
    ansList = models.CharField(default='a', max_length=1000)
    tries_left = models.IntegerField(default=1)

    closedTime = models.DateTimeField(default=datetime.now())

    showAnswers = models.BooleanField(default=False)
    isVisibleToStud = models.BooleanField(default=False)

    class Meta:
        ordering = ["description"]

    def __str__(self):
        self.save()
        return self.description

    @property
    def argslen(self):
        return len(re.findall('{.}', self.description))

    def getAnswer(self, arglist):
        answer = ""
        s = 'java -jar ' + self.checkerPath + " " + ' '.join(str(x) for x in arglist)
        from subprocess import Popen, PIPE, STDOUT
        p = Popen(s, stdout=PIPE, stderr=STDOUT, shell=True)
        for line in p.stdout:
            if answer != "":
                answer += "###"
            answer += line.decode('utf-8').rstrip()
        return answer

    def getArgs(self):
        args = ""
        s = 'java -jar ' + self.generatorPath
        from subprocess import Popen, PIPE, STDOUT
        p = Popen(s, stdout=PIPE, stderr=STDOUT, shell=True)
        for line in p.stdout:
            if args != "":
                args += "###"
            string = line.decode('utf-8').rstrip()
            args += string
        return args


class GeneratedTask(models.Model):
    id = models.AutoField(primary_key=True)

    # number of task in student's list
    numAtStud = models.IntegerField(default=0)
    # id of template task
    template = models.ForeignKey(TemplateTask, on_delete=models.CASCADE, )
    # args, inserted into description
    args = models.CharField(blank=True, max_length=1000)

    # right answers to task
    answer = models.CharField(default="a", max_length=1000)
    # stored answers to task
    storedanswer = models.CharField(blank=True, max_length=1000)

    tries_left = models.IntegerField(default=1)
    solved = models.BooleanField(default=False)
    closedTime = models.DateTimeField(blank=True, default=datetime.now())
    showAnswers = models.BooleanField(default=False)
    isGivenByTeacher = models.BooleanField(default=False)

    class Meta:
        ordering = ["-numAtStud"]

    def genArgs(self):
        arr = []
        self.args = self.template.getArgs()
        arglist = list(self.args.split('###'))
        for string in arglist:
            x = float(string)
            if x.is_integer():
                arr.append(int(x))
            else:
                arr.append(x)
        self.answer = self.template.getAnswer(arr)
        self.save()

    def arglessSetup(self, student, templateTask, given, show):
        self.numAtStud = student.jobs.count()
        while student.jobs.filter(numAtStud=self.numAtStud).exists():
            self.numAtStud += 1
        self.template = templateTask
        self.tries_left = templateTask.tries_left
        self.showAnswers = show
        self.isGivenByTeacher = given
        self.save()
        student.jobs.add(self)
        student.save()

    def setup(self, student, templateTask, given, show):
        self.arglessSetup(student, templateTask, given, show)
        self.genArgs()
        self.save()

    def specialsetup(self, student, templateTask, given, show, args):
        self.arglessSetup(student, templateTask, given, show)
        self.args = args
        self.answer = self.template.getAnswer(args.split('###'))
        self.save()

    def __str__(self):
        arglist = list(self.args.split('###'))
        temp = self.template.description
        for arg in arglist:
            temp = re.sub("{.}", arg, temp, 1)
        return temp


class TaskGroup(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(default="a", max_length=100)
    types = models.ManyToManyField(TemplateTask, blank=True)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    groupNumber = models.IntegerField(default=100)
    id = models.AutoField(primary_key=True)
    name = models.CharField(default="asd", max_length=20)
    family_name = models.CharField(default="asd", max_length=20)
    fathers_name = models.CharField(default="asd", max_length=20)
    jobs = models.ManyToManyField(GeneratedTask, blank=True)

    class Meta:
        ordering = ["-family_name", "-name", "-fathers_name"]

    def __str__(self):
        return '%s %s %s' % (self.name, self.family_name, self.fathers_name)


class StudentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField(default=id)
    members = models.ManyToManyField(Student, blank=True)

    class Meta:
        ordering = ["-number"]

    def __str__(self):
        return str(self.number)
