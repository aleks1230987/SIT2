# pantheon/views.py (только необходимые функции)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
import datetime
from .models import HistoricalFigure, Country, City, Occupation
from django.db.models import Count, Avg, Sum, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import HistoricalFigureForm, HistoricalFigureDeleteForm


class HomeView(TemplateView):
    template_name = 'jinja2/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['recent_figures'] = HistoricalFigure.objects.select_related(
            'city', 'city__country', 'occupation'
        ).order_by('-id')[:10]
        
        context['stats'] = {
            'total_figures': HistoricalFigure.objects.count(),
            'total_countries': Country.objects.count(),
            'total_cities': City.objects.count(),
            'total_occupations': Occupation.objects.count(),
            'avg_popularity': HistoricalFigure.objects.aggregate(
                avg=Avg('historical_popularity_index')
            )['avg'] or 0,
            'max_popularity': HistoricalFigure.objects.aggregate(
                max=Max('historical_popularity_index')
            )['max'] or 0,
            'avg_languages': HistoricalFigure.objects.aggregate(
                avg=Avg('article_languages')
            )['avg'] or 0,
            'avg_views': HistoricalFigure.objects.aggregate(
                avg=Avg('average_views')
            )['avg'] or 0,
            'total_views': HistoricalFigure.objects.aggregate(
                total=Sum('page_views')
            )['total'] or 0,
        }
        
        context['last_update'] = datetime.datetime.now()
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        return render(self.request, self.template_name, context, using='jinja2')


def figure_list(request):
    all_figures = HistoricalFigure.objects.select_related(
        'city', 'city__country', 'occupation'
    ).order_by('-historical_popularity_index')
    
    page_size = 100
    paginator = Paginator(all_figures, page_size)
    
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'jinja2/figures.html', {
        'figures': page_obj.object_list,
        'total_figures': paginator.count,
        'page_size': page_size,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'title': 'Исторические личности'
    }, using='jinja2')


def statistics_view(request):
    from .models import City, Country, HistoricalFigure
    
    cities_stats = City.objects.annotate(
        figure_count=Count('historical_figures'),
        avg_popularity=Avg('historical_figures__historical_popularity_index')
    ).filter(
        figure_count__gt=0
    ).select_related('country').order_by('-avg_popularity')[:100]
    
    countries_stats = Country.objects.annotate(
        figure_count=Count('cities__historical_figures')
    ).filter(
        figure_count__gt=0
    ).order_by('-figure_count')[:100]
    
    total_figures = HistoricalFigure.objects.count()
    stats = {
        'total_countries': Country.objects.count(),
        'total_cities': City.objects.count(),
        'total_figures': total_figures,
        'avg_popularity': HistoricalFigure.objects.aggregate(
            avg=Avg('historical_popularity_index')
        )['avg'] or 0,
    }
    
    return render(request, 'jinja2/statistic.html', {
        'cities_stats': cities_stats,
        'countries_stats': countries_stats,
        'stats': stats,
        'total_figures': total_figures,
        'last_update': datetime.datetime.now(),
        'title': 'Статистика'
    }, using='jinja2')


# Новые представления для работы с формами

def figure_create(request):
    """Создание новой исторической личности"""
    if request.method == 'POST':
        form = HistoricalFigureForm(request.POST)
        if form.is_valid():
            figure = form.save()
            messages.success(request, f'Историческая личность "{figure.full_name}" успешно создана!')
            return redirect('figure_detail', pk=figure.pk)
    else:
        form = HistoricalFigureForm()
    
    return render(request, 'jinja2/figure_form.html', {
        'form': form,
        'title': 'Добавить историческую личность',
        'submit_text': 'Создать',
    }, using='jinja2')


def figure_update(request, pk):
    """Редактирование существующей исторической личности"""
    figure = get_object_or_404(HistoricalFigure, pk=pk)
    
    if request.method == 'POST':
        form = HistoricalFigureForm(request.POST, instance=figure)
        if form.is_valid():
            figure = form.save()
            messages.success(request, f'Историческая личность "{figure.full_name}" успешно обновлена!')
            return redirect('figure_detail', pk=figure.pk)
    else:
        form = HistoricalFigureForm(instance=figure)
    
    return render(request, 'jinja2/figure_form.html', {
        'form': form,
        'figure': figure,
        'title': f'Редактирование: {figure.full_name}',
        'submit_text': 'Сохранить изменения',
    }, using='jinja2')


def figure_delete(request, pk):
    """Удаление исторической личности"""
    figure = get_object_or_404(HistoricalFigure, pk=pk)
    
    if request.method == 'POST':
        form = HistoricalFigureDeleteForm(request.POST)
        if form.is_valid():
            figure_name = figure.full_name
            figure.delete()
            messages.success(request, f'Историческая личность "{figure_name}" успешно удалена!')
            return redirect('figure_list')
    else:
        form = HistoricalFigureDeleteForm()
    
    return render(request, 'jinja2/figure_delete.html', {
        'form': form,
        'figure': figure,
        'title': f'Удаление: {figure.full_name}',
    }, using='jinja2')


def figure_detail(request, pk):
    """Детальная информация об исторической личности"""
    figure = get_object_or_404(
        HistoricalFigure.objects.select_related('city', 'city__country', 'occupation'),
        pk=pk
    )
    
    return render(request, 'jinja2/figure_detail.html', {
        'figure': figure,
        'title': figure.full_name,
    }, using='jinja2')
