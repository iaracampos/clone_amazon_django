from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('produto/<int:id>/', views.product, name='produto'),
    path('produto/<int:id>/adicionar-comentario/', views.adicionar_comentario, name='adicionar_comentario'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('my-account/', views.minha_conta, name='minha_conta'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar-ao-carrinho/<int:id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
