from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .gerenciador import Gerenciador

ROLE_CHOICES = [('user', 'Usuário'),('admin', 'Administrador'),]
SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Feminino')]
TIPO_CHOICES = [('SB', 'Subtenente'), ('A', 'Atirador'), ('S', 'Sargento'), ('C', 'Cabo')]
TIPS_CHOICES = [('S', 'Sim'), ('N', 'Não')]
class UsuarioCustomizado(AbstractBaseUser, PermissionsMixin):
    numero_atirador = models.IntegerField(unique=True, null=True, blank=True)
    foto = models.ImageField(upload_to='imagens/%Y/%m/%d/')
    nome_completo = models.CharField(max_length=150)
    nome_guerra = models.CharField(max_length=50)
    patente = models.CharField(max_length=2, choices=TIPO_CHOICES)
    comandante = models.CharField(max_length=2, choices=TIPS_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    tipo_sanguineo = models.CharField(max_length=3, null=True, blank=True)
    pai = models.CharField(max_length=100, null=True, blank=True)
    mae = models.CharField(max_length=100, null=True, blank=True)
    cpf = models.CharField(max_length=20, unique=True)
    ra = models.CharField(max_length=20, null=True, blank=True)
    escolaridade = models.CharField(max_length=50, null=True, blank=True)
    trabalho = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField("endereço de email", unique=True)
    senha = models.CharField(max_length=50)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    numero_casa = models.CharField(max_length=10)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    cep = models.CharField(max_length=8)
    id_turma = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    objects = Gerenciador()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['nome_completo', 'cpf', 'data_nascimento']

    def __str__(self):
        return str(self.numero_atirador) if self.numero_atirador is not None else self.email

class Guarda(models.Model):
    data_guarda = models.DateTimeField(auto_now_add=False) #ver/pensar ainda
    observacoes = models.CharField(max_length=250)
    id_escala = models.ForeignKey('Escala', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Guarda {self.id} - {self.data_guarda.strftime('%d/%m/%Y')}"

class UsuarioGuarda(models.Model):
    id_guarda = models.ForeignKey(Guarda, on_delete=models.CASCADE)
    numero_atirador = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE, to_field='numero_atirador', null=False)
    comandante = models.BooleanField(default=False)

class Troca(models.Model):
    STATUS_CHOICES = [('Pendente', 'Pendente'), ('Aprovada', 'Aprovada'), ('Rejeitada', 'Rejeitada')]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pendente')
    data_solicitada = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(null=True, blank=True)
    ultima_modificacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Troca {self.id} - {self.status}"
    
class TrocaAtirador(models.Model):
    TIPO_CHOICES = [('Solicitante', 'Solicitante'), ('Substituto', 'Substituto')]
    
    id_troca = models.ForeignKey(Troca, on_delete=models.CASCADE)
    numero_atirador = models.ForeignKey(UsuarioCustomizado, to_field='numero_atirador', on_delete=models.CASCADE, null=False)
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES)
    
    def __str__(self):
        return f"{self.tipo} - {self.numero_atirador} na Troca {self.id_troca}"

class TrocaGuarda(models.Model):
    id_guarda = models.ForeignKey(Guarda, on_delete=models.CASCADE)
    id_troca = models.ForeignKey(Troca, on_delete=models.CASCADE)

    def __str__(self):
        return f"Troca {self.id_troca} - Guarda {self.id_guarda}"
    
class Notificacao(models.Model):
    STATUS_CHOICES = [('Enviada', 'Enviada'), ('Lida', 'Lida'), ('Pendente', 'Pendente')]
    
    numero_atirador = models.ForeignKey(UsuarioCustomizado, to_field='numero_atirador', on_delete=models.CASCADE, null=False)
    id_troca = models.ForeignKey(Troca, on_delete=models.CASCADE)
    data_envio = models.DateTimeField(auto_now_add=True)
    mensagem = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pendente')
    
    def __str__(self):
        return f"Notificação para {self.numero_atirador} - {self.status}"
    
class Escala(models.Model):
    nome_escala = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_escala