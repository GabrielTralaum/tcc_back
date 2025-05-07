from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import date

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
        ordem = request.data.get('ordem', 'crescente')
        data_inicio_str = request.data.get('data_inicio')
        data_fim_str = request.data.get('data_fim')

        if not data_inicio_str or not data_fim_str:
            return Response({'error': 'Data de início e fim são obrigatórias.'}, status=status.HTTP_400_BAD_REQUEST)

        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

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

        def pegar_atiradores(indice_inicial, lista):
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
            is_fds = dia.weekday() >= 5  # 5 = sábado, 6 = domingo

            guarda = Guarda.objects.create(data_guarda=dia, observacoes='', id_escala=escala)

            if is_fds:
                atiradores_do_dia, index_fds = pegar_atiradores(index_fds, atiradores)
            else:
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

@api_view(['POST'])
def solicitar_troca_guarda(request):
    try:
        solicitante_num = request.data.get('solicitante')
        substituto_num = request.data.get('substituto')
        guarda_solicitante_id = request.data.get('guarda_solicitante')
        guarda_substituto_id = request.data.get('guarda_substituto')
        motivo = request.data.get('motivo')

        from datetime import date

        # Obter o usuário solicitante e substituto
        solicitante = UsuarioCustomizado.objects.get(numero_atirador=solicitante_num)
        substituto = UsuarioCustomizado.objects.get(numero_atirador=substituto_num)

        # Verificar se o solicitante e o substituto são do mesmo tipo (atirador ou comandante)
        if (solicitante.comandante != substituto.comandante):
            return Response({'erro': 'Troca permitida apenas entre atiradores ou entre comandantes.'}, status=status.HTTP_400_BAD_REQUEST)

        # Obter a guarda solicitante
        guarda_solicitante = Guarda.objects.get(id=guarda_solicitante_id)
        data_guarda_solicitante = guarda_solicitante.data_guarda.date()  # Utilizando apenas a data, sem a hora

        # Verificar se o solicitante já está escalado para outra guarda no mesmo dia
        vinculo_existente = UsuarioGuarda.objects.filter(
            numero_atirador_id=solicitante_num,
            id_guarda__data_guarda__date=data_guarda_solicitante  # Filtra pela data sem considerar a hora
        ).exists()

        if vinculo_existente:
            return Response({'erro': 'O solicitante já está escalado para outra guarda neste dia.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se o substituto já está escalado para outra guarda no mesmo dia
        guarda_substituto = Guarda.objects.get(id=guarda_substituto_id)
        data_guarda_substituto = guarda_substituto.data_guarda.date()  # Utilizando apenas a data, sem a hora

        vinculo_substituto_existente = UsuarioGuarda.objects.filter(
            numero_atirador_id=substituto_num,
            id_guarda__data_guarda__date=data_guarda_substituto  # Filtra pela data sem considerar a hora
        ).exists()

        if vinculo_substituto_existente:
            return Response({'erro': 'O substituto já está escalado para outra guarda neste dia.'}, status=status.HTTP_400_BAD_REQUEST)

        if not all([solicitante_num, substituto_num, guarda_solicitante_id, guarda_substituto_id]):
            return Response({'erro': 'Dados incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        troca = Troca.objects.create(motivo=motivo)

        # Relaciona os atiradores à troca
        TrocaAtirador.objects.create(id_troca=troca, numero_atirador_id=solicitante_num, tipo='Solicitante')
        TrocaAtirador.objects.create(id_troca=troca, numero_atirador_id=substituto_num, tipo='Substituto')

        # Relaciona as guardas à troca, especificando quem é quem
        TrocaGuarda.objects.create(id_troca=troca, id_guarda_id=guarda_solicitante_id, tipo='Solicitante')
        TrocaGuarda.objects.create(id_troca=troca, id_guarda_id=guarda_substituto_id, tipo='Substituto')

        return Response({'mensagem': 'Solicitação registrada com sucesso.', 'id_troca': troca.id}, status=status.HTTP_201_CREATED)

    except UsuarioCustomizado.DoesNotExist:
        return Response({'erro': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Guarda.DoesNotExist:
        return Response({'erro': 'Guarda não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def aceitar_troca_guarda(request):
    try:
        id_troca = request.data.get('id_troca')

        if not id_troca:
            return Response({'erro': 'ID da troca não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        troca = Troca.objects.get(id=id_troca)

        if troca.status != 'Pendente':
            return Response({'erro': 'A troca já foi processada.'}, status=status.HTTP_400_BAD_REQUEST)

        troca.status = 'Aprovada'
        troca.save()

        return Response({'mensagem': 'Troca aprovada com sucesso.'}, status=status.HTTP_200_OK)

    except Troca.DoesNotExist:
        return Response({'erro': 'Troca não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def rejeitar_troca_guarda(request):
    try:
        id_troca = request.data.get('id_troca')

        if not id_troca:
            return Response({'erro': 'ID da troca não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        troca = Troca.objects.get(id=id_troca)

        if troca.status != 'Pendente':
            return Response({'erro': 'A troca já foi processada.'}, status=status.HTTP_400_BAD_REQUEST)

        troca.status = 'Rejeitada'
        troca.save()

        return Response({'mensagem': 'Troca rejeitada com sucesso.'}, status=status.HTTP_200_OK)

    except Troca.DoesNotExist:
        return Response({'erro': 'Troca não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def executar_troca_guarda(request):
    try:
        id_troca = request.data.get('id_troca')

        if not id_troca:
            return Response({'erro': 'ID da troca não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        troca = Troca.objects.get(id=id_troca)

        if troca.status != 'Aprovada':
            return Response({'erro': 'A troca não está aprovada.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar solicitante e substituto
        solicitante = TrocaAtirador.objects.get(id_troca=troca, tipo='Solicitante').numero_atirador
        substituto = TrocaAtirador.objects.get(id_troca=troca, tipo='Substituto').numero_atirador

        # Buscar as guardas diretamente pela nova estrutura
        guarda_solicitante = TrocaGuarda.objects.get(id_troca=troca, tipo='Solicitante').id_guarda
        guarda_substituto = TrocaGuarda.objects.get(id_troca=troca, tipo='Substituto').id_guarda

        # Pega os vínculos específicos dos dois atiradores com suas respectivas guardas
        ug_solicitante = UsuarioGuarda.objects.get(numero_atirador=solicitante, id_guarda=guarda_solicitante)
        ug_substituto = UsuarioGuarda.objects.get(numero_atirador=substituto, id_guarda=guarda_substituto)

        # Realizar a troca
        ug_solicitante.numero_atirador, ug_substituto.numero_atirador = substituto, solicitante
        ug_solicitante.save()
        ug_substituto.save()

        return Response({'mensagem': 'Troca realizada com sucesso.'}, status=status.HTTP_200_OK)

    except Troca.DoesNotExist:
        return Response({'erro': 'Troca não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except TrocaAtirador.DoesNotExist:
        return Response({'erro': 'Dados da troca incompletos.'}, status=status.HTTP_400_BAD_REQUEST)
    except TrocaGuarda.DoesNotExist:
        return Response({'erro': 'Guarda da troca não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except UsuarioGuarda.DoesNotExist:
        return Response({'erro': 'Vínculo específico entre atirador e guarda não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
