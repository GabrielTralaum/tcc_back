from django.contrib.auth.models import BaseUserManager

class Gerenciador(BaseUserManager):
    def create_user(self, email, password=None, nome_completo=None, cpf=None, data_nascimento=None, **extra_fields):
        if not email:
            raise ValueError('O campo email é obrigatório.')
        if not nome_completo:
            raise ValueError('O campo nome completo é obrigatório.')
        if not cpf:
            raise ValueError('O campo CPF é obrigatório.')
        if not data_nascimento:
            raise ValueError('O campo data de nascimento é obrigatório.')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nome_completo=nome_completo,
            cpf=cpf,
            data_nascimento=data_nascimento,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, nome_completo='Admin', cpf='08453757259', data_nascimento='1990-01-01', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, nome_completo, cpf, data_nascimento, **extra_fields)
