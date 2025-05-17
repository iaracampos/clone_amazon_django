from django.contrib import admin
from .models import Cliente, Pedido, Carrinho, Pagamento, Produto, ItemPedido, ItemCarrinho, Categoria, Review

admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(Carrinho)
admin.site.register(Pagamento)
admin.site.register(Produto)
admin.site.register(ItemPedido)
admin.site.register(ItemCarrinho)
admin.site.register(Categoria)
admin.site.register(Review)
