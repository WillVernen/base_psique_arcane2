import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def assign_paciente_owners(apps, schema_editor):
    Pacientes = apps.get_model('usuarios', 'Pacientes')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    user = User.objects.order_by('id').first()
    if user is None:
        Pacientes.objects.all().delete()
        return
    Pacientes.objects.filter(usuario__isnull=True).update(usuario_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacientes',
            name='usuario',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='pacientes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_paciente_owners, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='pacientes',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='pacientes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
