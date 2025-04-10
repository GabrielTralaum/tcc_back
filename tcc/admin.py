from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustomizado, Guarda, UsuarioGuarda, Troca, TrocaAtirador, TrocaGuarda, Notificacao, Escala

import random
from datetime import timedelta, datetime
from django.utils import timezone

class UsuarioCustomizadoAdmin(UserAdmin):
    model = UsuarioCustomizado

    list_display = ('email', 'nome_completo', 'cpf', 'sexo', 'numero_atirador','patente', 'is_active')
    search_fields = ('email', 'nome_completo', 'cpf', 'numero_atirador')
    list_filter = ('sexo', 'is_active')
    ordering = ('email',)

    fieldsets = (
        (("Informações Pessoais"), {
            'fields': ('email', 'nome_completo', 'cpf', 'data_nascimento', 'sexo', 'rua', 'bairro', 'cidade', 'numero_casa', 'complemento', 'cep','foto')
        }),
        (("Informações Militares"), {
            'fields': ('numero_atirador','nome_guerra', 'trabalho', 'escolaridade', 'ra', 'mae', 'pai', 'tipo_sanguineo', 'patente', 'comandante')
        }),
        (("Permissões"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'role')
        }),
        (("Senha e autenticação"), {
            'fields': ('password',)  # Adicionado para permitir alteração de senha
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_completo', 'cpf', 'data_nascimento', 'sexo', 'password1', 'password2', 'is_active', 'is_staff', 'role'),
        }),
    )

admin.site.register(UsuarioCustomizado, UsuarioCustomizadoAdmin)

@admin.action(description='Sortear atiradores para guardas da semana')
def sortear_guardas(modeladmin, request, queryset):
    atiradores = list(UsuarioCustomizado.objects.filter(is_active=True).exclude(numero_atirador__isnull=True))
    random.shuffle(atiradores)

    escalas = Escala.objects.all()
    hoje = timezone.now().date()
    qtd_por_guarda = 2
    dias = 7
    index = 0

    for dia in range(dias):
        for escala in escalas:
            data_inicio = datetime.combine(hoje + timedelta(days=dia), escala.escala_horario)
            data_fim = data_inicio + timedelta(hours=6)

            guarda = Guarda.objects.create(
                data_inicio=data_inicio,
                data_fim=data_fim,
                observacoes="Gerada automaticamente",
                id_escala=escala
            )

            for _ in range(qtd_por_guarda):
                if index >= len(atiradores):
                    index = 0
                    random.shuffle(atiradores)

                UsuarioGuarda.objects.create(
                    id_guarda=guarda,
                    numero_atirador=atiradores[index]
                )
                index += 1

    modeladmin.message_user(request, f"Guardas geradas com sucesso para os próximos {dias} dias.")


class GuardaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_guarda', 'data_inicio', 'data_fim', 'id_escala')
    actions = [sortear_guardas]

class GuardaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_guarda', 'observacoes', 'id_escala')
    list_filter = ('id_escala',)
    ordering = ('data_guarda',)

admin.site.register(Guarda, GuardaAdmin)

@admin.register(UsuarioGuarda)
class UsuarioGuardaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo_do_usuario', 'id_guarda')

    def nome_completo_do_usuario(self, obj):
        return obj.numero_atirador.nome_completo
    nome_completo_do_usuario.short_description = 'Nome do Atirador'

class TrocaAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'data_solicitada','motivo', 'ultima_modificacao')
    list_filter = ('status',)
    search_fields = ('id', 'status')
    ordering = ('-data_solicitada',)

admin.site.register(Troca, TrocaAdmin)

class TrocaAtiradorAdmin(admin.ModelAdmin):
    list_display = ('id_troca', 'numero_atirador', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('numero_atirador__numero_atirador', 'id_troca')
    ordering = ('id_troca',)

admin.site.register(TrocaAtirador, TrocaAtiradorAdmin)

class TrocaGuardaAdmin(admin.ModelAdmin):
    list_display = ('id_troca', 'id_guarda')
    search_fields = ('id_troca', 'id_guarda')
    ordering = ('id_troca',)

admin.site.register(TrocaGuarda, TrocaGuardaAdmin)

class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('numero_atirador','id_troca','data_envio','mensagem', 'status')
    list_filter = ('status',)
    search_fields = ('numero_atirador__numero_atirador', 'mensagem')
    ordering = ('-data_envio',)

admin.site.register(Notificacao, NotificacaoAdmin)

class EscalasAdmin(admin.ModelAdmin):
    list_display = ('id','nome_escala')
    list_filter = ('nome_escala',)
    search_fields = ('nome_escala','id')
    ordering = ('nome_escala',)

admin.site.register(Escala, EscalasAdmin)   



class GuardaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_guarda', 'data_inicio', 'data_fim', 'id_escala')
    actions = [sortear_guardas]