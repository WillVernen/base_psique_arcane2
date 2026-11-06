from django.conf import settings
from django.db import models


class Pacientes(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pacientes',
    )
    nome = models.CharField(max_length=64)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='fotos')
    ativo = models.BooleanField(default=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.nome
