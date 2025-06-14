
from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),

    path("produto/<int:id>/", views.product, name="produto"),
    path("produto/<int:id>/adicionar-comentario/", views.adicionar_comentario, name="adicionar_comentario"),
    path("login/", views.login, name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("my-account/", views.minha_conta, name="minha_conta"),
    path("carrinho/", views.carrinho, name="carrinho")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)