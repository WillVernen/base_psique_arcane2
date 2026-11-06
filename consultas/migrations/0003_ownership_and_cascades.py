import django.db.models.deletion
from django.db import migrations, models


def assign_pergunta_paciente(apps, schema_editor):
    Pergunta = apps.get_model('consultas', 'Pergunta')
    Pacientes = apps.get_model('usuarios', 'Pacientes')
    paciente = Pacientes.objects.order_by('id').first()
    if paciente is None:
        Pergunta.objects.all().delete()
        return
    Pergunta.objects.filter(paciente__isnull=True).update(paciente_id=paciente.id)


class Migration(migrations.Migration):

    dependencies = [
        ('consultas', '0002_datatreinamento_pergunta'),
        ('usuarios', '0002_pacientes_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gravacoes',
            name='paciente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='gravacoes',
                to='usuarios.pacientes',
            ),
        ),
        migrations.AlterField(
            model_name='datatreinamento',
            name='recording',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='consultas.gravacoes',
            ),
        ),
        migrations.AddField(
            model_name='pergunta',
            name='paciente',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='perguntas',
                to='usuarios.pacientes',
            ),
        ),
        migrations.RunPython(assign_pergunta_paciente, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='pergunta',
            name='paciente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='perguntas',
                to='usuarios.pacientes',
            ),
        ),
    ]
