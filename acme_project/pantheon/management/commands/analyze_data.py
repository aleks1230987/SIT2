# pantheon/management/commands/analyze_data.py
from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Max, Min, Sum
from pantheon.models import HistoricalFigure, Country, City, Occupation

class Command(BaseCommand):
    help = 'Анализ данных Pantheon Project'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== АНАЛИЗ ДАННЫХ PANTHON PROJECT ==='))
        
        # Базовая статистика
        stats = HistoricalFigure.objects.aggregate(
            total=Count('id'),
            avg_popularity=Avg('historical_popularity_index'),
            max_popularity=Max('historical_popularity_index'),
            min_popularity=Min('historical_popularity_index'),
            avg_languages=Avg('article_languages'),
            total_views=Sum('page_views'),
            avg_views=Avg('page_views')
        )
        
        self.stdout.write(f'\nОБЩАЯ СТАТИСТИКА:')
        self.stdout.write(f'   Всего личностей: {stats["total"]:,}')
        self.stdout.write(f'   Всего просмотров: {stats["total_views"]:,}')
        self.stdout.write(f'   Средняя популярность: {stats["avg_popularity"]:.2f}')
        self.stdout.write(f'   Максимальная популярность: {stats["max_popularity"]:.2f}')
        self.stdout.write(f'   Среднее количество языков: {stats["avg_languages"]:.1f}')
        
        # Распределение по континентам
        self.stdout.write(f'\nРАСПРЕДЕЛЕНИЕ ПО КОНТИНЕНТАМ:')
        continent_stats = Country.objects.values('continent').annotate(
            figure_count=Count('cities__historical_figures', distinct=True)
        ).order_by('-figure_count')
        
        total_figures = stats['total']
        for stat in continent_stats:
            if stat['figure_count'] > 0:
                percentage = (stat['figure_count'] / total_figures) * 100
                continent_name = stat['continent'] if stat['continent'] else 'Не указан'
                self.stdout.write(
                    f'   {continent_name:15}: '
                    f'{stat["figure_count"]:6,} '
                    f'({percentage:.1f}%)'
                )
        
        # Топ-10 самых популярных
        self.stdout.write(f'\nТОП-10 САМЫХ ПОПУЛЯРНЫХ:')
        top_figures = HistoricalFigure.objects.select_related(
            'city__country', 'occupation'
        ).order_by('-historical_popularity_index')[:10]
        
        for i, figure in enumerate(top_figures, 1):
            location = figure.birth_location[:30] if figure.birth_location else "Место не указано"
            self.stdout.write(
                f'   {i:2}. {figure.full_name:35} '
                f'{figure.historical_popularity_index:5.2f} '
                f'| {location}'
            )
        
        # Самые распространенные профессии
        self.stdout.write(f'\nТОП-5 ПРОФЕССИЙ:')
        occupations = Occupation.objects.annotate(
            figure_count=Count('historical_figures')
        ).order_by('-figure_count')[:5]
        
        for i, occ in enumerate(occupations, 1):
            self.stdout.write(
                f'   {i}. {occ.name:30} '
                f'{occ.figure_count:4,} '
                f'({occ.domain})'
            )
        
        # Города с наибольшим количеством личностей
        self.stdout.write(f'\nТОП-5 ГОРОДОВ:')
        cities = City.objects.select_related('country').annotate(
            figure_count=Count('historical_figures')
        ).order_by('-figure_count')[:5]
        
        for i, city in enumerate(cities, 1):
            self.stdout.write(
                f'   {i}. {city.name:20}, {city.country.name:15} '
                f'{city.figure_count:3,}'
            )
        
        # Дополнительная статистика
        self.stdout.write(f'\nДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:')
        
        # Личности с наибольшим количеством просмотров
        self.stdout.write(f'\nТОП-5 ПО ПРОСМОТРАМ:')
        top_views = HistoricalFigure.objects.order_by('-page_views')[:5]
        for i, figure in enumerate(top_views, 1):
            views_millions = figure.page_views / 1_000_000
            self.stdout.write(
                f'   {i}. {figure.full_name:30} '
                f'{views_millions:6.1f}M просмотров'
            )
        
        # Личности с наибольшим количеством языков
        self.stdout.write(f'\nТОП-5 ПО КОЛИЧЕСТВУ ЯЗЫКОВ:')
        top_languages = HistoricalFigure.objects.order_by('-article_languages')[:5]
        for i, figure in enumerate(top_languages, 1):
            self.stdout.write(
                f'   {i}. {figure.full_name:30} '
                f'{figure.article_languages:3} языков'
            )
        
        # Распределение по доменам деятельности
        self.stdout.write(f'\nРАСПРЕДЕЛЕНИЕ ПО ДОМЕНАМ:')
        domain_stats = Occupation.objects.values('domain').annotate(
            figure_count=Count('historical_figures')
        ).order_by('-figure_count')
        
        for stat in domain_stats:
            if stat['figure_count'] > 0:
                percentage = (stat['figure_count'] / total_figures) * 100
                domain_name = stat['domain'] if stat['domain'] else 'Не указан'
                self.stdout.write(
                    f'   {domain_name:15}: '
                    f'{stat["figure_count"]:5,} '
                    f'({percentage:.1f}%)'
                )
        
        self.stdout.write(self.style.SUCCESS('\nАНАЛИЗ ЗАВЕРШЕН'))
