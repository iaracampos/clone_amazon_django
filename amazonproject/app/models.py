from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    endereco = models.TextField()
    telefone = models.CharField(max_length=15)
    data_cadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.email}"
    

class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()
    categorias = models.ManyToManyField(Categoria)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - R${self.preco}"
    
    def em_estoque(self):
        return self.estoque > 0
    
    def star_rating(self):
        reviews = self.review_set.all()
        if not reviews:
            return 5
        return round(sum(review.nota for review in reviews) / len(reviews))
    
    def count_reviews(self):
        return self.review_set.count()

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20)

    @property
    def total(self):
        return sum(item.precoUnitario * item.quantidade for item in self.itens.all())

    def __str__(self):
        return f"Pedido #{self.id} - Cliente: {self.cliente.nome} - Status: {self.status}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    precoUnitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Produto: {self.produto.nome} - Quantidade: {self.quantidade}"

class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    dataCriacao = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Carrinho #{self.id} - Cliente: {self.cliente.nome} - Status: {self.status}"
    
    def total(self):
        return sum(item.produto.preco * item.quantidade for item in self.itens.all())

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"Produto: {self.produto.nome} - Quantidade: {self.quantidade}"

class Pagamento(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    metodoPagamento = models.CharField(max_length=25)

    def __str__(self):
        return f"Pagamento - Pedido #{self.pedido.id} - Valor: R${self.valor}"

class Review(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nota = models.IntegerField()
    comentario = models.TextField()
    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Review - Produto: {self.produto.nome} - Nota: {self.nota}"
