from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.decorators import login_required

# Decorator para exigir login

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('password')
        
        # First, find the user by email
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "E-mail ou senha inválidos.")
            return redirect('login')
        
        # Authenticate using username and password
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login_django(request, user)
            return redirect('index')
        else:
            messages.error(request, "E-mail ou senha inválidos.")
            return redirect('login')
    
    return render(request, 'app/login.html')


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        senha2 = request.POST.get('confirm_password')
        endereco = request.POST.get('endereco', '')
        telefone = request.POST.get('telefone', '')
        
        # Validate passwords match
        if senha != senha2:
            messages.error(request, "As senhas não conferem.")
            return redirect('cadastro')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "E-mail já cadastrado.")
            return redirect('cadastro')
        
        # Validate password length (Django requirement)
        if len(senha) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            return redirect('cadastro')
        
        try:
            # Create the User object
            user = User.objects.create_user(
                username=email,  # Using email as username
                email=email,
                password=senha,  # Django will hash this automatically
                first_name=nome
            )
            
            # Update the Cliente profile that was automatically created by signal
            cliente = user.cliente
            cliente.endereco = endereco
            cliente.telefone = telefone
            cliente.save()
            
            messages.success(request, "Conta criada com sucesso! Faça login.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {e}")
            return redirect('cadastro')
    
    return render(request, 'app/login.html')

def logout(request):
    logout_django(request)
    messages.success(request, "Logout realizado com sucesso.")
    return redirect('login')

@login_required
def profile(request):
    """View para acessar dados do cliente logado"""
    cliente = request.user.cliente
    context = {
        'cliente': cliente,
        'user': request.user
    }
    return render(request, 'app/profile.html', context)


def index(request):
    query = request.GET.get('search', '')  # Default para string vazia em vez de None
    categoria_id = request.GET.get('categoria')

    products = Produto.objects.all()

    if query:
        products = products.filter(nome__icontains=query)

    if categoria_id:
        products = products.filter(categorias__id=categoria_id)

    categorias = Categoria.objects.all()

    context = {
        'products': products,
        'categorias': categorias,
        'query_original': query,
        'categoria_selecionada': int(categoria_id) if categoria_id else None
    }

    return render(request, 'app/index.html', context)


def product(request, id):
    produto = get_object_or_404(Produto, id=id)
    cliente = None

    if request.user.is_authenticated:
        cliente = request.user.cliente

    comentarios = Review.objects.filter(produto=produto).order_by('-data')
    range_rate = [1] * produto.star_rating()
    range_void = [1] * (5 - produto.star_rating())

    context = {
        'produto': produto,
        'comentarios': comentarios,
        'range_rate': range_rate,
        'range_void': range_void,
        'cliente': cliente,
    }

    return render(request, 'app/product.html', context)


@login_required
def adicionar_comentario(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para comentar.")
        return redirect('login')

    produto = get_object_or_404(Produto, id=id)
    if request.user.is_authenticated:
        cliente = request.user.cliente

    if request.method == 'POST':
        texto = request.POST.get('texto')
        nota = request.POST.get('nota', 5)
        if texto:
            Review.objects.create(
                produto=produto,
                cliente=cliente,
                comentario=texto,
                nota=nota
            )
    return redirect('produto', id=produto.id)


@login_required
def minha_conta(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente

    return render(request, 'app/minha_conta.html', { 'user': cliente })


@login_required
def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)
    itens = ItemCarrinho.objects.filter(carrinho=carrinho)

    # Calcular o valor total do carrinho
    valor_total = sum(item.quantidade * item.preco for item in itens)

    context = {
        'carrinho': carrinho,
        'items': itens,
        'valor_total': f"R$ {valor_total:.2f}".replace('.', ',')  # formato brasileiro opcional
    }
    return render(request, 'app/carrinho.html', context)



@login_required
def adicionar_ao_carrinho(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.user.is_authenticated:
        cliente = request.user.cliente
    carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade': 1, 'preco': produto.preco}
    )
    if not created:
        item.quantidade += 1
        item.save()

    return redirect('carrinho')

def logout_view(request):
    logout(request)
    return redirect('login')

def pagamento(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        messages.error(request, "Você precisa estar logado para realizar o pagamento.")
        return redirect('login')

    carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)

    if not carrinho.itens.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    context = {
        'carrinho': carrinho,
        'valor_total': f"R$ {carrinho.total():.2f}".replace('.', ',')  # formato brasileiro opcional
    }
    return render(request, 'app/pagamento.html', context)


def pos_pagamento(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cliente = request.user.cliente
        carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)

        if not carrinho.itens.exists():
            messages.error(request, "Seu carrinho está vazio.")
            return redirect('carrinho')

        # Criar o pedido
        pedido = Pedido.objects.create(cliente=cliente, status='Pendente')

        # Adicionar itens do carrinho ao pedido
        for item in carrinho.itens.all():
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.quantidade,
                precoUnitario=item.preco
            )

        # Limpar o carrinho
        carrinho.itens.all().delete()

        messages.success(request, "Pedido realizado com sucesso!")
        return render(request, 'app/thanks.html')

    return render(request, 'app/pagamento.html')


@login_required
def remover_item_carrinho(request, item_id):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    carrinho = get_object_or_404(Carrinho, cliente=cliente)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    item.delete()
    messages.success(request, "Item removido do carrinho.")
    return redirect('carrinho')

def thanks(request):
    return render(request, 'app/thanks.html')