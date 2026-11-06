from django.db import models
from usuarios.models import Pacientes


class Gravacoes(models.Model):
    video = models.FileField(upload_to='gravacoes')
    data = models.DateTimeField()
    transcrever = models.BooleanField(default=False)
    paciente = models.ForeignKey(
        Pacientes,
        on_delete=models.CASCADE,
        related_name='gravacoes',
    )
    humor = models.IntegerField(default=0)
    transcricao = models.TextField()
    resumo = models.JSONField(default=list, blank=True)
    segmentos = models.JSONField(default=list, blank=True)


class DataTreinamento(models.Model):
    recording = models.ForeignKey(Gravacoes, on_delete=models.CASCADE)
    text = models.TextField()


class Pergunta(models.Model):
    paciente = models.ForeignKey(
        Pacientes,
        on_delete=models.CASCADE,
        related_name='perguntas',
    )
    data_treinamento = models.ManyToManyField(DataTreinamento)
    pergunta = models.TextField()

    def __str__(self):
        return self.pergunta
