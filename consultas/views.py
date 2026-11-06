from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Avg
from usuarios.models import Pacientes
from .models import Gravacoes, DataTreinamento, Pergunta
from django.http import StreamingHttpResponse, JsonResponse, Http404
from .agents import RAGContext
from .wrapper_evolutionapi import SendMessage
from django.contrib.humanize.templatetags.humanize import naturaltime
import json


def get_owned_paciente(request, paciente_id):
    return get_object_or_404(Pacientes, id=paciente_id, usuario=request.user)


def get_owned_gravacao(request, gravacao_id):
    return get_object_or_404(
        Gravacoes,
        id=gravacao_id,
        paciente__usuario=request.user,
    )


def get_owned_pergunta(request, pergunta_id):
    return get_object_or_404(
        Pergunta,
        id=pergunta_id,
        paciente__usuario=request.user,
    )


@login_required
def consultas(request, id):
    paciente = get_owned_paciente(request, id)
    if request.method == 'GET':
        gravacoes = Gravacoes.objects.filter(paciente=paciente).order_by('data')
        datas = [str(naturaltime(item['data'])) for item in gravacoes.values('data')]
        humores = [item['humor'] for item in gravacoes.values('humor')]
        humor_medio = gravacoes.exclude(humor=0).aggregate(media=Avg('humor'))['media']
     
        return render(request, 'consultas.html', {
            'paciente': paciente,
            'gravacoes': gravacoes,
            'datas': json.dumps(datas),
            'humores': json.dumps(humores),
            'humor_medio': round(humor_medio, 1) if humor_medio is not None else None,
        })
    elif request.method == 'POST':
        gravacao = request.FILES.get('gravacao')
        data = request.POST.get('data')
        transcript = request.POST.get('transcript') == 'on'

        gravacao = Gravacoes(
            video=gravacao,
            data=data,  
            transcrever=transcript,
            paciente=paciente,
        )
        gravacao.save()

        return redirect(reverse('consultas', kwargs={'id': id}))


@login_required
def gravacao(request, id):
    gravacao = get_owned_gravacao(request, id)
    humor_medio = (
        Gravacoes.objects.filter(paciente=gravacao.paciente)
        .exclude(humor=0)
        .aggregate(media=Avg('humor'))['media']
    )
    return render(request, 'gravacao.html', {
        'gravacao': gravacao,
        'humor_medio': round(humor_medio, 1) if humor_medio is not None else None,
    })


@login_required
@require_POST
def excluir_gravacao(request, id):
    gravacao = get_owned_gravacao(request, id)
    paciente_id = gravacao.paciente_id
    DataTreinamento.objects.filter(recording=gravacao).delete()
    if gravacao.video:
        gravacao.video.delete(save=False)
    gravacao.delete()
    return redirect(reverse('consultas', kwargs={'id': paciente_id}))


@login_required
def chat(request, id):
    paciente = get_owned_paciente(request, id)
    if request.method == 'GET':
        return render(request, 'chat.html', {'paciente': paciente})
    elif request.method == 'POST':
        pergunta_user = request.POST.get('pergunta')
        pergunta = Pergunta(
            pergunta=pergunta_user,
            paciente=paciente,
        )
        pergunta.save()
        return JsonResponse({'id': pergunta.id})


@login_required
@require_POST
def stream_response(request, id):
    paciente = get_owned_paciente(request, id)
    id_pergunta = request.POST.get('id_pergunta')
    pergunta = get_owned_pergunta(request, id_pergunta)
    if pergunta.paciente_id != paciente.id:
        raise Http404()
    return StreamingHttpResponse(RAGContext().retrieval(id_pergunta, id))


@login_required
def ver_referencias(request, id):
    pergunta = get_owned_pergunta(request, id)
    data_treinamento = pergunta.data_treinamento.all()
    gravacoes = Gravacoes.objects.filter(
        datatreinamento__in=data_treinamento,
        paciente__usuario=request.user,
    ).distinct()

    return render(request, 'ver_referencia.html', {
        'pergunta': pergunta,
        'data_treinamento': data_treinamento,
        'gravacoes': gravacoes,
    })


@login_required
def send_message(request, id):
    gravacao = get_owned_gravacao(request, id)
    for g in gravacao.resumo:
        SendMessage().send_message(
            'teste_arcane2',
            {"number": gravacao.paciente.telefone, "textMessage": {"text": g}},
        )
    return redirect(f'/consultas/gravacao/{id}')
