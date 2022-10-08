from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_paginator

AMOUNT_POSTS: int = 10
TITLE_POST_LENGTH: int = 30


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = get_paginator(posts, AMOUNT_POSTS, request)
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_paginator(posts, AMOUNT_POSTS, request)
    title = 'Записи сообщества: ' + str(group)
    context = {
        'posts': posts,
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    post_count = user_posts.count()
    page_obj = get_paginator(user_posts, AMOUNT_POSTS, request)
    title = f'Профайл пользователя {username}'
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        'user_posts': user_posts,
        'title': title,
        'page_obj': page_obj,
        'post_count': post_count,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author_post = post.author
    is_edit = False
    post_count = Post.objects.filter(author=author_post).count()
    comments = post.comments.all()
    form = CommentForm(request.POST)
    title = f'Пост {post.text[:TITLE_POST_LENGTH]}'
    context = {
        'post': post,
        'author_post': author_post,
        'post_count': post_count,
        'title': title,
        'is_edit': is_edit,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)

    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'post': post,
        'is_edit': True,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    page_obj = get_paginator(posts, AMOUNT_POSTS, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    follower = Follow.objects.filter(user=user, author=author)

    if user != author and not follower.exists():
        Follow.objects.create(user=user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)

    if follower.exists():
        follower.delete()

    return redirect('posts:profile', username=username)
