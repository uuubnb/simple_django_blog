from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView
from .forms import CommentForm, PostForm
from .models import Post, Author, PostView
from marketing.models import Signup

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        "queryset": queryset
    }
    return render(request, 'search_results.html', context)

def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset

def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method =="POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)

# def blog(request):
#     category_count = get_category_count()
#     most_recent = Post.objects.order_by('-timestamp')[:3]
#     post_list = Post.objects.all()
#     paginator = Paginator(post_list, 4)
#     page_request_var = 'page'
#     page = request.GET.get(page_request_var)
#     try:
#         paginated_queryset = paginator.page(page)
#     except PageNotAnInteger:
#         paginated_queryset = paginator.page(1)
#     except EmptyPage:
#         paginated_queryset = paginator.page(paginator.num_pages)
    

#     context = {
#         'queryset': paginated_queryset,
#         'most_recent': most_recent,
#         'page_request_var': page_request_var,
#         'category_count': category_count
#     }
#     return render(request, 'blog.html', context)

class PostListView(ListView):
    model = Post #использовать данные модели Post
    template_name = 'blog.html' #использовать этот template
    context_object_name = 'queryset' #определяет какая переменная будет использоваться для передачи контекста  
    paginate_by = 4 #встроенный пагинатор, число - сколько объектов будет на странице

    def get_context_data(self, **kwargs): #Возвращает данные контекста для отображения списка объектов
        category_count = get_category_count() #вызов функции get_category_count
        most_recent = Post.objects.order_by('-timestamp')[:3] #извлечение трех последних записей из модели Post
        context = super().get_context_data(**kwargs) # вызов метода супер-класса (препдположение) для получения контекста в качестве аргументов дале  
        context['most_recent'] = most_recent #не понимаю конструкцию
        context['page_request_var'] = "page"
        context['category_count'] = category_count #не понимаю конструкцию
        return context #возвращает результат выполнения метода get_context_data с аргументами выше

# def post(request, id):
#     category_count = get_category_count()
#     most_recent = Post.objects.order_by('-timestamp')[:3]
#     post = get_object_or_404(Post, id=id)
#     form = CommentForm(request.POST or None)
#     if request.method == "POST":
#         if form.is_valid():
#             form.instance.user = request.user
#             form.instance.post = post
#             form.save()
#             return redirect(reverse("post-detail", kwargs={
#                 'id': post.pk
#             }))
#     context = {
#         'form': form,
#         'post': post,
#         'most_recent': most_recent,
#         'category_count': category_count
#     }
#     return render(request, 'post.html', context) 

class PostDetailView(DetailView):
    model = Post  #использовать данные модели Post
    template_name = 'post.html' #использовать этот template 
    context_object_name = 'post' #определяет какая переменная будет использоваться для передачи контекста
    form = CommentForm() #переменная для вывода формы комментариев

    def get_object(self): #Возвращает объект, который отображается данным представлением
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user=self.request.user,
                post=obj
            )
        return obj

    def get_context_data(self, **kwargs): #Возвращает данные контекста для отображения списка объектов
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'pk': post.pk
            }))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))