from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login , logout , authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,'todo/home.html')

def loginuser(request):
    if request.method == 'GET':
        return render(request,'todo/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request , username = request.POST["username"] , password = request.POST["password"])
        if user is None:
            return render(request, 'todo/loginuser.html',{'form':AuthenticationForm,'error':'Username and Passwords did not match'})
        else:
            login(request , user )
            return redirect('currentodos')
def signup(request):
    if request.method == 'GET':
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request , user)
                return redirect('currentodos')
            except IntegrityError:
                return render(request,'todo/signupuser.html',{'form':UserCreationForm, 'error':'Username already exists .Please try another one'})
        else:
            return render(request,'todo/signupuser.html',{'form':UserCreationForm, 'error':'Passwords did not match'})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currentodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request,'todo/currentodos.html',{'todos':todos})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False)
    return render(request,'todo/completedtodos.html',{'todos':todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = TodoForm(instance=todo)
    if request.method == 'GET':
        return render(request,'todo/view.html',{'todo':todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST , instance=todo)
            form.save()
            return redirect('currentodos')
        except ValueError:
            return render(request, 'todo/view.html',{'todo':todo , 'form':form, 'error': 'BAD INFO.TRY AGAIN' })

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm()})
    else:
        form = TodoForm(request.POST)
        newtodo = form.save(commit=False)
        newtodo.user = request.user
        newtodo.save()
        return redirect('currentodos')

@login_required
def completetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currentodos')

@login_required
def deletetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currentodos')
