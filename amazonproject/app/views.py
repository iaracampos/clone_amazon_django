from django.shortcuts import render
from .models import *
from django.shortcuts import get_object_or_404, redirect

# Create your views here.
def index(request):
    products = Produto.objects.all()
    context = {
        'products': products,
    }
    
    return render(request, 'app/index.html', context)

def product(request, id):
    produto = get_object_or_404(Produto, id=id)
    
    comentarios = Review.objects.filter(produto=produto).order_by('-data')
    
    context = {
        'produto': produto,
        'comentarios': comentarios,
    }

    return render(request, 'app/product.html', context)
    

def adicionar_comentario(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        # Valide e salve o comentário aqui
        texto_comentario = request.POST.get('texto')
        if texto_comentario:
            Review.objects.create(
                produto=produto,
                autor=request.user, # Garante que o usuário esteja logado
                texto=texto_comentario
                # Adicione o campo de avaliação aqui
            )
    return redirect('product', id=produto.id) # Redireciona de volta para a página do produto

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')  # Redireciona para a página inicial após o login bem-sucedido
        else:
            error_message = "Usuário ou senha inválidos."
            return render(request, 'app/login.html', {'error_message': error_message})
    
    return render(request, 'app/login.html')  # Renderiza o formulário de login

def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        user = Cliente.objects.create_user(username=username, password=password, email=email)
        user.save()
        
        return redirect('login')  # Redireciona para a página de login após o cadastro bem-sucedido
    
    return render(request, 'app/cadastro.html')  # Renderiza o formulário de cadastro


def minha_conta(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login se o usuário não estiver autenticado
    
    cliente = get_object_or_404(Cliente, id=request.user.id)
    
    context = {
        'cliente': cliente,
    }
    
    return render(request, 'app/minha_conta.html', context)  # Renderiza a página da conta do usuário autenticado


def carrinho(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to the login page if the user is not authenticated
    
    cliente = get_object_or_404(Cliente, id=request.user.id)
    
    # Use get_or_create to either retrieve the existing cart or create a new one
    carrinho, created = Carrinho.objects.get_or_create(cliente=cliente)
    
    context = {
        'carrinho': carrinho,
    }
    
    return render(request, 'app/carrinho.html', context) 