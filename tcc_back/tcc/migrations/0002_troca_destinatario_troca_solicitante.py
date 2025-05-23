# Generated by Django 5.1.4 on 2025-04-28 22:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tcc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='troca',
            name='destinatario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trocas_que_recebi', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='troca',
            name='solicitante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trocas_que_solicitei', to=settings.AUTH_USER_MODEL),
        ),
    ]
