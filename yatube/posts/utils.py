from django.core.paginator import Paginator


def get_paginator(posts, AMOUNT_POSTS, request):
    paginator = Paginator(posts, AMOUNT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
