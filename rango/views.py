from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category,Page
from rango.forms import CategoryForm, PageForm
from django.urls import reverse
from django.shortcuts import redirect, render
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

def register(request):
    registered = False
    categories = Category.objects.all()  
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)  
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)  
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered,})

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
     return render(request, 'rango/about.html')
def show_category(request, category_name_slug):
    
   
    try:
     
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        category.views += 1
        category.save()
        context_dict = {'category': category, 'pages': pages}
     
    except Category.DoesNotExist:
        context_dict = {'category': None, 'pages': None}
    return render(request, 'rango/category.html', context=context_dict)
from django.contrib.auth.decorators import login_required

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=True)
            return redirect('rango:index')
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('rango:index')

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.save()
            return redirect('rango:show_category', category_name_slug=category.slug)
    else:
        form = PageForm()
    
    return render(request, 'rango/add_page.html', {'form': form, 'category': category})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))
@login_required
def restricted_view(request):
    return render(request, 'rango/restricted.html')
