import os
import re
import subprocess

from django.core.mail import mail_admins

from .models import Educator
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin

from student.models import StudentGroup, TemplateTask, TaskGroup, Student, GeneratedTask


def checkEdu(request):
    if 'edu_id' not in request.session:
        raise Http404('You are not logged in as educator')


def edMain(request):
    checkEdu(request)

    return render(
        request,
        'edmain.html',
        context={'educator': Educator.objects.get(id=request.session['edu_id'])},
    )


@xframe_options_sameorigin
def edAssignTask(request):
    checkEdu(request)

    step6 = False
    if 'step6' in request.POST:
        step6 = True
        values = []  # TODO
    elif 'step5' in request.POST:
        topicsid = request.POST.getlist('topicsid[]')
        topics = TaskGroup.objects.filter(id__in=topicsid)
        template = TemplateTask.objects.get(id=int(request.POST['tasktemplate']))
        studentsid = request.POST.getlist('students[]')
        students = Student.objects.filter(id__in=studentsid)
        valchoice = request.POST['valchoice']
        if valchoice == 'random':
            for stud in students:
                t = GeneratedTask()
                t.setup(stud, template, True, False)
        else:
            args = request.POST['args']
            lines = args.splitlines()
            if len(lines) < len(students):
                ctx = {
                    'args': args,
                    'template': template.id,
                    'topics': topics,
                    'students': students,
                    'message': "Not enough lines"
                }
                return render(
                    request,
                    'edassigntask_taskgrpsel.html',
                    context=ctx,
                )

            for line in lines:
                if len(line.split('###')) != template.argslen:
                    ctx = {
                        'args': args,
                        'template': template.id,
                        'topics': topics,
                        'students': students,
                        'message': "Wrong argument number somewhere"
                    }
                    return render(
                        request,
                        'edassigntask_taskgrpsel.html',
                        context=ctx,
                    )
            for stud, line in zip(students, lines):
                t = GeneratedTask()
                t.specialsetup(stud, template, True, False, line)
        return render(request, 'edmain.html')

    if 'step4' in request.POST:
        topicsid = request.POST.getlist('topicsid[]')
        topics = TaskGroup.objects.filter(id__in=topicsid)
        topic = TaskGroup.objects.get(name=request.POST['topic'])
        studentsid = request.POST.getlist('students[]')
        students = Student.objects.filter(id__in=studentsid)
        templates = topic.types.all()
        ctx = {
            'args': request.POST['args'],
            'templates': templates,
            'topics': topics,
            'students': students,
            'message': ""
        }
        return render(
            request,
            'edassigntask_taskgrpsel.html',
            context=ctx,
        )
        from django.http import HttpResponse
        return HttpResponse('TODO step 4')

    if 'step3' in request.POST:
        topics = TaskGroup.objects.all()
        studentsid = request.POST.getlist('students[]')
        students = Student.objects.filter(id__in=studentsid)
        ctx = {
            'args': '',
            'templates': [],
            'topics': topics,
            'students': students,
            'message': ""
        }
        return render(
            request,
            'edassigntask_taskgrpsel.html',
            context=ctx,
        )

    step2 = False
    if 'step2' in request.POST:
        step2 = True
        groups = request.POST.getlist('groups[]')
    elif 'group' in request.POST:
        step2 = True
        groups = [request.POST['group']]

    if step2 & ('groups' in locals()):
        if len(groups) > 0:
            ctx = {}
            students = set()
            for grp in StudentGroup.objects.filter(number__in=groups):
                students |= set(grp.members.all())
            ctx['students'] = [{'id': student.id, 'label': str(student)}
                               for student in students]
            ctx['check'] = ('step2' in request.POST)
            return render(
                request,
                'edassigntask_studsel.html',
                context=ctx,
            )

    ctx = {'groups': [{'number': grp.number, 'label': str(grp)}
                      for grp in StudentGroup.objects.all()]}
    return render(
        request,
        'edassigntask_grpsel.html',
        context=ctx,
    )


def edDefineTask(request):
    checkEdu(request)

    if 'src' in request.POST:
        ctx = {'generatorText': '', 'checkerText': '', 'description': '',
               'subject': TaskGroup.objects.get(id=int(request.POST.get('src'))).name, 'src': -1}

    else:
        for arg in TemplateTask.objects.all():
            if str(arg.id) in request.POST:
                task = arg
        if 'task' not in locals():
            for arg in TemplateTask.objects.all():
                if ('d' + str(arg.id)) in request.POST:
                    todel = arg
            if 'todel' not in locals():
                group = TaskGroup.objects.get(id=int(request.POST.get('group')))
                return render(
                    request,
                    'topic_templates.html',
                    context={'src': group.id, 'templates': group.types.all()},
                )
            group = TaskGroup.objects.get(name=todel.topic)
            group.types.remove(todel)
            import shutil
            shutil.rmtree('TasksSupport/' + str(todel.id))
            todel.delete()
            if todel in TemplateTask.objects.all():
                todel.delete()
            group.save()
            return render(
                request,
                'topic_templates.html',
                context={'src': group.id, 'templates': group.types.all()},
            )
        ctx = {'generatorText': task.generatorText, 'checkerText': task.checkerText,
               'description': task.description, 'subject': task.topic, 'src': task.id}
    return render(
        request,
        'eddefinetask.html',
        context=ctx,
    )


def edGenerateTask(request):
    checkEdu(request)

    if 'group_id' in request.POST:
        group_id = request.POST['group_id']
        group = TaskGroup.objects.get(id=group_id)
        templates = TemplateTask.objects.filter(topic=group.name, difficulty=request.POST['difficulty'])
    else:
        templates = []
    return render(
        request,
        'edgeneratetask.html',
        context={
            'topics': TaskGroup.objects.all(),
            'tempNum': len(templates),
            'templates': templates},
    )


def subArgsToDesc(description, args):
    arglist = list(args.split('###'))
    for arg in arglist:
        description = re.sub("{.}", arg, description, 1)
    return description


def edPreGeneratedTask(request):
    checkEdu(request)

    temp_id = request.POST['task_id']
    template = TemplateTask.objects.get(id=temp_id)
    labels = list(template.ansList.split(','))
    args = template.getArgs()
    description = subArgsToDesc(template.description, args)
    arr = []
    arglist = list(args.split('###'))
    for string in arglist:
        x = float(string)
        if x.is_integer():
            arr.append(int(x))
        else:
            arr.append(x)
    answer = template.getAnswer(arr)
    return render(
        request,
        'edpregeneratedtask.html',
        context={
            'topic': template.topic,
            'difficulty': template.difficulty,
            'description': description,
            'answer': answer,
            'labels': labels
        },
    )


def edProfile(request):
    checkEdu(request)
    return render(
        request,
        'edprofile.html',
        context={'educator': Educator.objects.get(id=request.session['edu_id'])},
    )


def edStatistics(request):
    checkEdu(request)

    return render(
        request,
        'edstatistics.html',
        context={'groups': StudentGroup.objects.all()},
    )


def edStatsStudents(request):
    checkEdu(request)

    if 'group' in request.POST:
        group_id = request.POST['group']
    else:
        group_id = 0

    students = StudentGroup.objects.get(number=group_id).members.all()

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'stats_students.html',
        context={'students': students},
    )


def edStatsStudent(request):
    checkEdu(request)

    if 'stud_id' not in request.POST:
        stud_id = 1
        group_id = None
    else:
        stud_id = request.POST['stud_id']
        if 'group_id' not in request.POST:
            group_id = None
        else:
            group_id = request.POST['group_id']
            if (group_id == '-1'):
                group_id = None
    try:
        _stud = Student.objects.get(id=stud_id)
    except:
        raise Http404("Студент не найден!")

    if group_id is None:
        group_id = -1
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
        'stats_student.html',
        context={
            'student': _stud,
            'group_id': group_id,
            'topics': TaskGroup.objects.all(),
            'solved': len(solved),
            'all': len(allTasks)},
    )


def edStatsStudentDetailed(request):
    checkEdu(request)

    if 'stud_id' not in request.POST:
        stud_id = 1
    else:
        stud_id = request.POST['stud_id']
    """
    Функция отображения страницы истории решенных задач.
    """

    try:
        _stud = Student.objects.get(id=stud_id)
    except:
        raise Http404("Студент не найден!")

    _arr = _stud.jobs.filter(tries_left=0)
    group_id = request.POST['group_id']
    if group_id != '-1':
        group = TaskGroup.objects.get(id=group_id)
        _arr = _arr.filter(template__topic=group.name)

    return render(
        request,
        'stats_student_detailed.html',
        context={
            'stud_id': stud_id,
            'group_id': group_id,
            'tasks': _arr,
            'taskNum': len(_arr)},
    )


def edSupport(request):
    checkEdu(request)

    return render(
        request,
        'edsupport.html',
        context={},
    )


def edTaskWatch(request):
    checkEdu(request)
    stud_id = request.POST['stud_id']
    student = Student.objects.get(id=stud_id)
    job_id = request.POST['job_id']
    job = student.jobs.get(numAtStud=job_id)

    labels = list(job.template.ansList.split(','))

    if not job.storedanswer:
        job.storedanswer = '###' * (len(labels) - 1)
        job.save()

    answers = list(job.answer.split('###'))

    stored = list(job.storedanswer.split('###'))
    if len(stored) < len(labels):
        stored = [''] * len(labels)

    labelsandstored = [{'label': labels[i], 'stored': stored[i], 'answer': answers[i]} for i in range(len(labels))]
    return render(
        request,
        'edtaskwatch.html',
        context={
            'task': job,
            'stud_id': stud_id,
            'group_id': request.POST['group_id'],
            'labelsandstored': labelsandstored,
        },
    )


def edTaskGroups(request):
    checkEdu(request)

    return render(
        request,
        'topics.html',
        context={'topics': TaskGroup.objects.all()},
    )


def edTaskTemplates(request):
    checkEdu(request)

    templates = []
    for topic in TaskGroup.objects.all():
        if topic.name in request.POST:
            src = topic.id
            for temp in topic.types.all():
                templates.append(temp)
            break
    if 'src' not in locals():
        for arg in TaskGroup.objects.all():
            if ('d' + str(arg.id)) in request.POST:
                todel = arg
                break
        if 'todel' not in locals():
            return render(
                request,
                'topics.html',
                context={'topics': TaskGroup.objects.all()},
            )
        for task in todel.types.all():
            todel.types.remove(task)
            import shutil
            shutil.rmtree('TasksSupport/' + str(task.id))
            task.delete()
            if task in TemplateTask.objects.all():
                task.delete()
        todel.delete()
        if todel in TaskGroup.objects.all():
            todel.delete()
        return render(
            request,
            'topics.html',
            context={'topics': TaskGroup.objects.all()},
        )
    return render(
        request,
        'topic_templates.html',
        context={'src': src, 'templates': templates},
    )


def edTaskNew(request):
    checkEdu(request)

    return render(
        request,
        'create_topic.html',
        context={},
    )


def edchp(request):
    checkEdu(request)
    edu = Educator.objects.get(id=request.session['edu_id'])
    user = edu.creator
    cur = request.POST['cur']
    if not user.check_password(cur):
        request.session['chperror'] = 'Old password mismatch'
        return redirect('edu:edchangepassword')
    newpass = request.POST['newpass']
    newpassrepeat = request.POST['newpassrepeat']
    if newpass != newpassrepeat:
        request.session['chperror'] = 'New passwords do not match'
        return redirect('edu:edchangepassword')
    if len(newpass) < 8:
        request.session['chperror'] = 'New password too short'
        return redirect('edu:edchangepassword')
    user.set_password(newpass)
    user.save()
    return redirect('edu:edmain')


def edChangePassword(request):
    checkEdu(request)

    if 'chperror' in request.session:
        error = request.session.pop('chperror')
    else:
        error = ''
    return render(
        request,
        'edchangepassword.html',
        context={'error': error},
    )


def edchangepassword(request):
    checkEdu(request)
    if 'chperror' in request.session:
        error = request.session.pop('chperror')
    else:
        error = ''
    return render(
        request,
        'edchangepassword.html',
        context={'error': error},
    )


def editTemplate(request):
    checkEdu(request)

    src = request.POST.get('src')
    if src == '-1':
        job = TemplateTask()
        job.topic = request.POST.get('subject')
        job.description = request.POST.get('description')
        job.generatorText = request.POST.get('generatorText')
        job.checkerText = request.POST.get('checkerText')
        job.difficulty = request.POST.get('difficulty')
        job.save()
        path = "TasksSupport/" + str(job.id)
        os.mkdir(path, 0o767)
        path += '/'
        createGenerator(path, 'generator', job.generatorText)
        createGenerator(path, 'answer', job.checkerText)
        job.generatorPath = path + "generator.jar"
        job.checkerPath = path + "answer.jar"
        job.save()
        group = TaskGroup.objects.get(name=job.topic)
        group.types.add(job)
        group.save()
        job.save()
    else:
        job = TemplateTask.objects.get(id=int(src))
        topic = request.POST.get('subject')
        if topic != '':
            if topic != job.topic:
                grfrom = TaskGroup.objects.get(name=job.topic)
                grfrom.types.remove(job)
                job.topic = topic
                grto = TaskGroup.objects.get(name=topic)
                grto.types.add(job)
                grto.save()
        description = request.POST.get('description')
        if description != '':
            job.description = description
        job.difficulty = request.POST.get('difficulty')
        path = "TasksSupport/" + str(job.id) + '/'
        generatorText = request.POST.get('generatorText')
        if job.generatorText != generatorText:
            job.generatorText = generatorText
            createGenerator(path, 'generator', generatorText)
        checkerText = request.POST.get('checkerText')
        if job.checkerText != checkerText:
            job.checkerText = checkerText
            createGenerator(path, 'answer', checkerText)
        job.save()
    return redirect('edu:edmain')


def createGenerator(path, name, string):
    owd = os.getcwd()
    os.chdir(path)
    f = open(name + '.java', "w")
    f.write(string)
    f.close()
    subprocess.call(['javac', name + '.java'])
    if os.path.exists(name + '.java'):
        os.remove(name + '.java')
    subprocess.call(['jar', 'cvfe', name + '.jar', name, name + '.class'])
    if os.path.exists(name + '.class'):
        os.remove(name + '.class')
    os.chdir(owd)


def edsendmail(request):
    checkEdu(request)
    name = str(Educator.objects.get(id=request.session['edu_id']))
    return redirect('edu:edmain')
    mail_admins(request.POST['subject'], "From" + name + '\n' + request.POST['message'])


def edcreategroup(request):
    checkEdu(request)
    name = request.POST['name']
    g = TaskGroup(name=name)
    g.save()
    return redirect('edu:topics')


def toLogin(request):
    checkEdu(request)
    del request.session['edu_id']
    return redirect('login:authorise')
