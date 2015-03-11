from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, objects, ipp):
    paginator = Paginator(objects, ipp)
    page = request.GET.get('p')
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        return paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)
