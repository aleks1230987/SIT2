# pantheon/admin.py
from django.contrib import admin
from django.db.models import Count, Avg
from .models import Country, City, Occupation, HistoricalFigure

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'continent', 'city_count', 'figure_count']
    list_filter = ['continent']
    search_fields = ['name']
    list_per_page = 50
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = 'Города'
    city_count.admin_order_field = 'cities__count'
    
    def figure_count(self, obj):
        return HistoricalFigure.objects.filter(city__country=obj).count()
    figure_count.short_description = 'Личности'
    figure_count.admin_order_field = 'cities__historical_figures__count'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_country', 'get_continent', 'state', 'figure_count', 'coordinates']
    list_filter = ['country__continent', 'country']
    search_fields = ['name', 'country__name']
    list_select_related = ['country']
    
    def get_country(self, obj):
        return obj.country.name
    get_country.short_description = 'Страна'
    get_country.admin_order_field = 'country__name'
    
    def get_continent(self, obj):
        return obj.country.continent
    get_continent.short_description = 'Континент'
    get_continent.admin_order_field = 'country__continent'
    
    def figure_count(self, obj):
        return obj.historical_figures.count()
    figure_count.short_description = 'Личности'
    
    def coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
        return "—"
    coordinates.short_description = 'Координаты'


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'domain', 'figure_count', 'avg_popularity']
    list_filter = ['domain', 'industry']
    search_fields = ['name', 'industry']
    list_per_page = 50
    
    def figure_count(self, obj):
        return obj.historical_figures.count()
    figure_count.short_description = 'Личности'
    figure_count.admin_order_field = 'historical_figures__count'
    
    def avg_popularity(self, obj):
        avg = obj.historical_figures.aggregate(avg=Avg('historical_popularity_index'))['avg']
        return f"{avg:.2f}" if avg else "—"
    avg_popularity.short_description = 'Ср. популярность'


@admin.register(HistoricalFigure)
class HistoricalFigureAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 
        'birth_year', 
        'get_location',
        'get_occupation_info',
        'article_languages',
        'page_views_short',
        'historical_popularity_index',
        'popularity_badge'
    ]
    
    list_filter = [
        'occupation__domain',
        'city__country__continent',
        'birth_year'
    ]
    
    search_fields = ['full_name', 'article_id']
    readonly_fields = [
        'article_id',
        'original_city_name', 
        'original_country_name', 
        'original_continent_name',
        'original_occupation_name',
        'original_industry_name',
        'original_domain_name',
        'popularity_category'
    ]
    
    list_select_related = ['city__country', 'occupation']
    list_per_page = 100
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'article_id', 
                'full_name', 
                'birth_year',
                'article_languages'
            )
        }),
        ('Место рождения', {
            'fields': (
                'city',
                ('original_city_name', 'original_country_name', 'original_continent_name')
            )
        }),
        ('Профессия', {
            'fields': (
                'occupation',
                ('original_occupation_name', 'original_industry_name', 'original_domain_name')
            )
        }),
        ('Популярность', {
            'fields': (
                'page_views', 
                'average_views', 
                'historical_popularity_index',
                'popularity_category'
            )
        }),
    )
    
    def get_location(self, obj):
        if obj.city:
            return f"{obj.city.name}, {obj.city.country.name}"
        elif obj.original_city_name:
            return f"{obj.original_city_name}, {obj.original_country_name}"
        return "—"
    get_location.short_description = 'Место рождения'
    
    def get_occupation_info(self, obj):
        if obj.occupation:
            return f"{obj.occupation.name}"
        elif obj.original_occupation_name:
            return f"{obj.original_occupation_name}"
        return "—"
    get_occupation_info.short_description = 'Профессия'
    
    def page_views_short(self, obj):
        """Форматирование больших чисел"""
        if obj.page_views >= 1_000_000:
            return f"{obj.page_views / 1_000_000:.1f}M"
        elif obj.page_views >= 1_000:
            return f"{obj.page_views / 1_000:.1f}K"
        return str(obj.page_views)
    page_views_short.short_description = 'Просмотры'
    
    def popularity_badge(self, obj):
        """Цветовой индикатор популярности"""
        categories = {
            "Очень высокая": "green",
            "Высокая": "blue",
            "Средняя": "orange",
            "Низкая": "gray",
            "Очень низкая": "lightgray"
        }
        category = obj.popularity_category
        color = categories.get(category, "gray")
        
        from django.utils.html import format_html
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'border-radius: 10px; background-color: {}; color: white; '
            'font-size: 12px;">{}</span>',
            color,
            category
        )
    popularity_badge.short_description = 'Категория'
