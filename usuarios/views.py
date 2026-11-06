from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Pacientes

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha não são iguais.')
            return redirect('cadastro')
            
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'Sua senha deve ter pelo meno 6 caracteres.')
            return redirect('cadastro')

        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('cadastro')
        
        User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect('login')
    
def login(request):
    if request.user.is_authenticated:
        return redirect('pacientes')
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username,  password=senha)

        if user:
            auth.login(request, user)
            next_url = request.GET.get('next') or 'pacientes'
            return redirect(next_url)
        
        messages.add_message(request, constants.ERROR, 'Username ou senha inválidos.')
        return redirect('login')


def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required
def pacientes(request):
    if request.method == "GET":
        pacientes = (
            Pacientes.objects.filter(ativo=True)
            .annotate(num_gravacoes=Count('gravacoes'))
            .order_by('nome')
        )
        return render(request, 'pacientes.html', {'pacientes': pacientes})
    elif request.method == "POST":
        foto = request.FILES.get('foto')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        telefone = request.POST.get('telefone') or None

        paciente = Pacientes(
            foto=foto,
            nome=nome,
            descricao=descricao,
            telefone=telefone,
        )

        paciente.save()

        return redirect('pacientes')
