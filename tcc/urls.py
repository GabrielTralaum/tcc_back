from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'usuario', UsuarioCustomizadoView)
router.register(r'Guarda', GuardaView)
router.register(r'UsuarioGuarda', UsuarioGuardaView)
router.register(r'Troca', TrocaView)
router.register(r'TrocaAtirador', TrocaAtiradorView)
router.register(r'TrocaGuarda', TrocaGuardaView)
router.register(r'Notificacao', NotificacaoView)
router.register(r'Escala', EscalaView)

urlpatterns = router.urls