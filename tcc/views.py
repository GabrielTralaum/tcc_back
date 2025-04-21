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
        # Pega a ordem do sorteio (padrão: crescente)
        ordem = request.data.get('ordem', 'crescente')

        # Pega o intervalo de datas fornecido pelo usuário
        data_inicio_str = request.data.get('data_inicio')
        data_fim_str = request.data.get('data_fim')

        # Validação básica
        if not data_inicio_str or not data_fim_str:
            return Response({'error': 'Data de início e fim são obrigatórias.'}, status=status.HTTP_400_BAD_REQUEST)

        # Converte as strings para objeto de data
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # Gera feriados do Brasil dentro do intervalo necessário
        feriados = holidays.Brazil(years=range(data_inicio.year, data_fim.year + 1))

        # Pega todos os atiradores (patente 'A') ordenados por número
        atiradores = list(UsuarioCustomizado.objects.filter(patente='A').order_by('numero_atirador'))

        # Pega todos os comandantes (comandante = 'S')
        comandantes = list(UsuarioCustomizado.objects.filter(comandante='S').order_by('numero_atirador'))

        # Se o usuário escolheu ordem decrescente
        if ordem == 'decrescente':
            atiradores = list(reversed(atiradores))

        # Quantidade de dias no intervalo
        dias_totais = (data_fim - data_inicio).days + 1

        # Índices para percorrer listas
        index_atirador = 0  # para dias úteis
        index_fds = 0       # para fins de semana/feriados

        for i in range(dias_totais):
            dia = data_inicio + timedelta(days=i)
            is_fim_de_semana = dia.weekday() >= 5  # sábado = 5, domingo = 6
            is_feriado = dia in feriados

            escala = Escala.objects.create(nome_escala=f"Escala de {data_inicio} a {data_fim}")
            # Cria o registro da guarda para o dia
            guarda = Guarda.objects.create(data_guarda=dia, observacoes='', id_escala=escala)

            # Dias úteis (segunda a sexta que não sejam feriados)
            if not is_fim_de_semana and not is_feriado:
                count = 0
                atiradores_do_dia = []

                while count < 3:
                    if index_atirador >= len(atiradores):
                        index_atirador = 0  # reinicia a contagem se chegar ao final da lista
                    atirador = atiradores[index_atirador]
                    if atirador.comandante == 'N':
                        atiradores_do_dia.append(atirador)
                        count += 1
                    index_atirador += 1

                # Escolhe um comandante diferente dos 3 atiradores escolhidos
                comandante = next((c for c in comandantes if c not in atiradores_do_dia), comandantes[0])

                # Cria os registros na tabela UsuarioGuarda
                for atirador in atiradores_do_dia:
                    UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=atirador, comandante=False)

                UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=comandante, comandante=True)

            else:
                # Fim de semana ou feriado: sorteio em ordem contínua
                atiradores_do_fds = []
                count = 0

                while count < 3:
                    if index_fds >= len(atiradores):
                        index_fds = 0
                    atirador = atiradores[index_fds]
                    if atirador.comandante == 'N':
                        atiradores_do_fds.append(atirador)
                        count += 1
                    index_fds += 1

                comandante = next((c for c in comandantes if c not in atiradores_do_fds), comandantes[0])

                for atirador in atiradores_do_fds:
                    UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=atirador, comandante=False)

                UsuarioGuarda.objects.create(id_guarda=guarda, numero_atirador=comandante, comandante=True)

        return Response({'mensagem': 'Sorteio realizado com sucesso!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['DELETE'])
def apagar_guardas(request):
    try:
        # Apaga todos os registros relacionados, começando pelos mais dependentes
        UsuarioGuarda.objects.all().delete()
        Guarda.objects.all().delete()
        Escala.objects.all().delete()

        return Response({'mensagem': 'Todas as guardas foram apagadas com sucesso!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


