from rest_framework import serializers
from .models import *

class UsuarioCustomizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioCustomizado
        fields = '__all__'

class GuardaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarda
        fields = '__all__'

class UsuarioGuardaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioGuarda
        fields = '__all__'

class TrocaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Troca
        fields = '__all__'

class TrocaAtiradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrocaAtirador
        fields = '__all__'

class TrocaGuardaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrocaGuarda
        fields = '__all__'

class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = '__all__'

class EscalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escala
        fields = '__all__'     