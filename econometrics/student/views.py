from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect

from django.urls import reverse
from datetime import datetime

# Create your views here.
from .models import TaskGroup, Student, TemplateTask, GeneratedTask


def checkStud(request):
    if 'stud_id' not in request.session:
        raise Http404('You are not logged in as student')


def main(request):
    checkStud(request)

    return render(
        request,
        'main.html',
        context={'student': Student.objects.get(id=request.session['stud_id'])},
    )


def currenttasks(request):
    checkStud(request)

    if 'stud_id' not in request.session:
        stud_id = 1
    else:
        stud_id = request.session['stud_id']
    try:
        _stud = Student.objects.get(id=stud_id)
    except:
        raise Http404("Студент не найден!")

    _arr = _stud.jobs.filter(tries_left__gt=0)

    return render(
        request,
        'currenttasks.html',
        context={'tasklist': _arr, 'taskNum': len(_arr)},
    )


def generatetask(request):
    checkStud(request)

    templates = []
    if 'templates' in request.session:
        for temp_id in request.session['templates']:
            templates.append(TemplateTask.objects.get(id=temp_id))

        request.session.pop('templates')

    return render(
        request,
        'generatetask.html',
        context={'topics': TaskGroup.objects.all(), 'tempNum': len(templates), 'templates': templates},
    )


def history(request):
    checkStud(request)

    stud_id = request.session['stud_id']
    _stud = Student.objects.get(id=stud_id)
    _arr = _stud.jobs.filter(tries_left=0)

    return render(
        request,
        'history.html',
        context={'finished': _arr.order_by('-closedTime'), 'taskNum': len(_arr)},
    )


def profile(request):
    checkStud(request)

    stud_id = request.session['stud_id']
    std = Student.objects.get(id=stud_id)
    return render(
        request,
        'profile.html',
        context={
            'student': std}
    )


def statistics(request):
    checkStud(request)

    stud_id = request.session['stud_id']
    if not 'group_id' in request.session:
        group_id = None
    else:
        group_id = request.session.pop('group_id')
    _stud = Student.objects.get(id=stud_id)

    if group_id is None:
        allTasks = _stud.jobs.filter(tries_left=0)
        solved = allTasks.filter(solved=True)
    else:
        try:
            group = TaskGroup.objects.get(id=group_id)
        except:
            raise Http404("Тема не найдена!")
        allTasks = _stud.jobs.filter(template__topic=group.name, tries_left=0)
        solved = allTasks.filter(solved=True)
    return render(
        request,
        'statistics.html',
        context={'topics': TaskGroup.objects.all(),
                 'solved': len(solved),
                 'all': len(allTasks)},
    )


def support(request):
    checkStud(request)

    return render(
        request,
        'support.html',
        context={},
    )


def task(request, task_id):
    checkStud(request)

    stud_id = request.session['stud_id']
    std = Student.objects.get(id=stud_id)
    try:
        _task = std.jobs.get(numAtStud=task_id)
    except:
        raise Http404("Задача не найдена!")

    labels = list(_task.template.ansList.split(','))

    if not _task.storedanswer:
        _task.storedanswer = '###' * (len(labels) - 1)
        _task.save()

    stored = list(_task.storedanswer.split('###'))
    if len(stored) < len(labels):
        stored = [''] * len(labels)

    labelsandstored = [{'label': labels[i], 'stored': stored[i]} for i in range(len(labels))]

    return render(
        request,
        'taskpage.html',
        context={'task': _task, 'labelsandstored': labelsandstored},
    )


def checkAnswer(request, task_id):
    checkStud(request)
    stud_id = request.session['stud_id']
    std = Student.objects.get(id=stud_id)
    try:
        _task = std.jobs.get(numAtStud=task_id)
    except:
        raise Http404("Задача не найдена!")

    right_answers = list(_task.answer.split('###'))
    cur_answers = []

    for ans in list(_task.template.ansList.split(',')):
        cur_answers.append(request.POST[ans])
    _task.storedanswer = '###'.join(cur_answers)

    for i in range(len(right_answers)):
        if cur_answers[i] != right_answers[i]:
            _task.tries_left -= 1
            break
    else:
        _task.tries_left = 0
        _task.closedTime = datetime.now()
        _task.solved = True

    _task.save()

    return HttpResponseRedirect(reverse('stud:task', args=(_task.numAtStud,)))


def change_topic(request):
    checkStud(request)

    if request.method == 'POST':
        for topic in TaskGroup.objects.all():
            if topic.name in request.POST:
                request.session['group_id'] = topic.id
                return redirect('stud:statistics')

    return redirect('stud:statistics')


def find_templates(request):
    checkStud(request)

    if request.method == 'POST':
        templates = []
        for topic in TaskGroup.objects.all():
            if topic.name in request.POST:
                for temp in topic.types.all():
                    if str(temp.difficulty) == request.POST['difficulty']:
                        templates.append(temp.id)

        request.session['templates'] = templates
        return redirect('stud:generatetask')

    return redirect('stud:generatetask')


def generateJob(request, jobTemplate):
    checkStud(request)

    stud_id = request.session['stud_id']
    cur = Student.objects.get(id=stud_id)
    if request.method == "POST":
        job = GeneratedTask()
        job.setup(cur, jobTemplate, False, False)


def generateManyJobs(request):
    if request.method == 'POST':
        temps_to_gen = []
        for temp in TemplateTask.objects.all():
            if str(temp.id) in request.POST:
                temps_to_gen.append(temp)
        for templ in temps_to_gen:
            generateJob(request, templ)
        return redirect('stud:generatetask')

    return redirect('stud:generatetask')


def chp(request):
    checkStud(request)
    stud = Student.objects.get(id=request.session['stud_id'])
    user = stud.creator
    cur = request.POST['cur']
    if not user.check_password(cur):
        request.session['chperror'] = 'Old password mismatch'
        return redirect('stud:changepassword')
    newpass = request.POST['newpass']
    newpassrepeat = request.POST['newpassrepeat']
    if newpass != newpassrepeat:
        request.session['chperror'] = 'New passwords do not match'
        return redirect('stud:changepassword')
    if len(newpass) < 8:
        request.session['chperror'] = 'New password too short'
        return redirect('stud:changepassword')
    user.set_password(newpass)
    user.save()
    return redirect('stud:main')


def ChangePassword(request):
    checkStud(request)

    if 'chperror' in request.session:
        error = request.session.pop('chperror')
    else:
        error = ''
    return render(
        request,
        'changepassword.html',
        context={'error': error},
    )


def sendmail(request):
    checkStud(request)
    name = str(Student.objects.get(id=request.session['stud_id']))
    return redirect('stud:main')
    mail_admins(request.POST['subject'], "From" + name + '\n' + request.POST['message'])


def toLogin(request):
    checkStud(request)
    del request.session['stud_id']
    return redirect('login:authorise')
