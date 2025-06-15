from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Cliente, Produto, Review, Carrinho, ItemCarrinho, Categoria
from functools import wraps
from django.contrib.auth import logout
from django.shortcuts import redirect

# Decorator para exigir login

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('cliente_id') is None:
            messages.error(request, "Você precisa estar logado.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    query = request.GET.get('search')
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
    if request.session.get('cliente_id'):
        cliente = get_object_or_404(Cliente, id=request.session['cliente_id'])

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


def adicionar_comentario(request, id):
    if request.session.get('cliente_id') is None:
        messages.error(request, "Você precisa estar logado para comentar.")
        return redirect('login')

    produto = get_object_or_404(Produto, id=id)
    cliente = get_object_or_404(Cliente, id=request.session['cliente_id'])

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


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('password')

        try:
            user = Cliente.objects.get(email=email)
        except Cliente.DoesNotExist:
            messages.error(request, "E‑mail não cadastrado.")
            return redirect('login')

        if check_password(senha, user.password):
            request.session['cliente_id'] = user.id
            return redirect('index')
        else:
            messages.error(request, "Senha incorreta.")
            return redirect('login')

    return render(request, 'app/login.html')


def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        senha2 = request.POST.get('confirm_password')

        if senha != senha2:
            messages.error(request, "As senhas não conferem.")
            return redirect('cadastro')

        make_hash = make_password(senha)
        Cliente.objects.create(
            nome=nome,
            email=email,
            password=make_hash,
            endereco=request.POST.get('endereco', ''),
            telefone=request.POST.get('telefone', '')
        )
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')

    return render(request, 'app/cadastro.html')


@login_required
def minha_conta(request):
    cliente = get_object_or_404(Cliente, id=request.session['cliente_id'])
    return render(request, 'app/minha_conta.html', { 'cliente': cliente })


@login_required
def carrinho(request):
    cliente = get_object_or_404(Cliente, id=request.session['cliente_id'])
    carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)
    return render(request, 'app/carrinho.html', { 'carrinho': carrinho })


@login_required
def adicionar_ao_carrinho(request, id):
    produto = get_object_or_404(Produto, id=id)
    cliente = get_object_or_404(Cliente, id=request.session['cliente_id'])
    carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade': 1, 'precoUnitario': produto.preco}
    )
    if not created:
        item.quantidade += 1
        item.save()

    return redirect('carrinho')

def logout_view(request):
    logout(request)
    return redirect('login')