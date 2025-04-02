from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustomizado, Guarda, UsuarioGuarda, Troca, TrocaAtirador, TrocaGuarda, Notificacao, Escala

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

class GuardaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_inicio', 'data_fim','data_guarda', 'observacoes', 'id_escala')
    list_filter = ('id_escala',)
    search_fields = ('data_inicio', 'data_fim')
    ordering = ('data_guarda',)

admin.site.register(Guarda, GuardaAdmin)

class UsuarioGuardaAdmin(admin.ModelAdmin):
    list_display = ('id_guarda', 'numero_atirador')
    search_fields = ('numero_atirador__numero_atirador',)
    ordering = ('id_guarda',)

admin.site.register(UsuarioGuarda, UsuarioGuardaAdmin)

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
    list_display = ('id','escala_horario')
    list_filter = ('escala_horario',)
    search_fields = ('escala_horario','id')
    ordering = ('escala_horario',)

admin.site.register(Escala, EscalasAdmin)    
