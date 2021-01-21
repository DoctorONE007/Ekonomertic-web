from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from educator.models import Educator
from student.models import Student, StudentGroup


def loginPage(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'authorise.html',
        context={'errors': ''},
    )


def authorize(request):
    login = request.POST['login']
    password = request.POST['password']
    from django.contrib.auth import authenticate
    user = authenticate(username=login, password=password)
    if user is not None:
        if str(login).endswith('@edu.hse.ru'):
            std = Student.objects.get(creator=user)
            request.session['stud_id'] = std.id
            return redirect('stud:main')
        elif str(login).endswith('@hse.ru'):
            ed = Educator.objects.get(creator=user)
            request.session['edu_id'] = ed.id
            return redirect('edu:edmain')
        else:
            return render(
                request,
                'authorise.html',
                context={'errors': 'No such student or educator'},
            )
    else:
        return render(
            request,
            'authorise.html',
            context={'errors': 'No user with such login and password'},
        )


def main(request):
    return render(
        request,
        'main.html',
        context={},
    )


def educators(request):

    return render(
        request,
        'educators.html',
        context={'educators': Educator.objects.all()},
    )


def studentgroups(request):

    return render(
        request,
        'student_groups.html',
        context={'groups': StudentGroup.objects.all()},
    )


def students(request):

    group_id = request.POST['group_id']
    group = StudentGroup.objects.all().get(id=group_id)

    return render(
        request,
        'students.html',
        context={'students': group.members.all()},
    )


def custom404(request, exception):
    if str(exception).find('tried'):
        exception = 'Page not found'
    return render(
        request,
        'authorise.html',
        context={'errors': exception},
    )