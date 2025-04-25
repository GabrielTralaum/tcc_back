from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import holidays
from datetime import datetime, timedelta


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


@api_view(['POST'])
def sortear_guardas(request):
    try:
        # Pergunta a ordem desejada
        ordem = request.data.get('ordem', 'crescente')
        data_inicio_str = request.data.get('data_inicio')
        data_fim_str = request.data.get('data_fim')

        if not data_inicio_str or not data_fim_str:
            return Response({'error': 'Data de início e fim são obrigatórias.'}, status=status.HTTP_400_BAD_REQUEST)

        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        feriados = holidays.Brazil(years=range(data_inicio.year, data_fim.year + 1))

        # Organiza os usuários
        todos_usuarios = list(UsuarioCustomizado.objects.order_by('numero_atirador'))
        atiradores = [u for u in todos_usuarios if u.comandante == 'N']
        comandantes = [u for u in todos_usuarios if u.comandante == 'S']

        if ordem == 'decrescente':
            atiradores.reverse()
            comandantes.reverse()

        if not atiradores or not comandantes:
            return Response({'error': 'É necessário ter ao menos um atirador e um comandante.'}, status=status.HTTP_400_BAD_REQUEST)

        dias_totais = (data_fim - data_inicio).days + 1

        index_uteis = 0
        index_fds = 0
        index_comandante = 0

        escala = Escala.objects.create(nome_escala=f"Escala de {data_inicio} a {data_fim}")

        # Função auxiliar para pegar atiradores válidos
        def pegar_atiradores(indice_inicial, lista, is_fds=False):
            atiradores_do_dia = []
            count = 0
            indice = indice_inicial

            while count < 3:
                candidato = lista[indice % len(lista)]
                if candidato.comandante == 'N':
                    atiradores_do_dia.append(candidato)
                    count += 1
                indice += 1

            return atiradores_do_dia, indice

        for i in range(dias_totais):
            dia = data_inicio + timedelta(days=i)
            is_fds = dia.weekday() >= 5 or dia in feriados  # Inclui feriados na regra de final de semana

            guarda = Guarda.objects.create(data_guarda=dia, observacoes='', id_escala=escala)

            if is_fds:
                # Final de semana ou feriado
                atiradores_do_dia, index_fds = pegar_atiradores(index_fds, atiradores, is_fds=True)
            else:
                # Dias úteis
                atiradores_do_dia, index_uteis = pegar_atiradores(index_uteis, atiradores)

            comandante = comandantes[index_comandante % len(comandantes)]
            index_comandante += 1

            for atirador in atiradores_do_dia:
                UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=atirador, comandante=False)

            UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=comandante, comandante=True)

        return Response({'mensagem': 'Sorteio realizado com sucesso!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def apagar_guardas(request):
    try:
       
        UsuarioGuarda.objects.all().delete()
        Guarda.objects.all().delete()
        Escala.objects.all().delete()

        return Response({'mensagem': 'Todas as guardas foram apagadas com sucesso!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
     


