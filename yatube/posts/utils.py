from django.core.paginator import Paginator

ORDER = 10


def paginator(request, post_list):
    regularity = Paginator(post_list, ORDER)
    page_number = request.GET.get('page')
    return regularity.get_page(page_number)
