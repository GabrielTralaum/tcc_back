from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

class UsuarioCustomizadoView(ModelViewSet):
    queryset = UsuarioCustomizado.objects.all()
    serializer_class = UsuarioCustomizadoSerializer

class GuardaView(ModelViewSet):
    queryset = Guarda.objects.all()
    serializer_class = GuardaSerializer

class UsuarioGuardaView(ModelViewSet):
    queryset = UsuarioGuarda.objects.all()
    serializer_class = UsuarioGuardaSerializer

@api_view(['POST'])
def upload_foto(request):
    if request.method == 'POST':
        serializer = UsuarioCustomizadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class TrocaView(ModelViewSet):
    queryset = Troca.objects.all()
    serializer_class = TrocaSerializer

class TrocaAtiradorView(ModelViewSet):
    queryset = TrocaAtirador.objects.all()
    serializer_class = TrocaAtiradorSerializer

class TrocaGuardaView(ModelViewSet):
    queryset = TrocaGuarda.objects.all()
    serializer_class = TrocaGuardaSerializer

class NotificacaoView(ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer

class EscalaView(ModelViewSet):
    queryset = Escala.objects.all()
    serializer_class = EscalaSerializer


