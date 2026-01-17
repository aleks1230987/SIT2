from django.db import models

# Create your models here.

class Country(models.Model):
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Название страны")
    continent = models.CharField(max_length=50, verbose_name="Континент")
    
    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ['name']
        indexes = [
            models.Index(fields=['continent']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.continent})"
        
class City(models.Model):
    
    name = models.CharField(max_length=100, verbose_name="Название города")
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name="Штат")
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        verbose_name="Широта"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        verbose_name="Долгота"
    )
    country = models.ForeignKey(
        Country, 
        on_delete=models.PROTECT,
        related_name='cities',
        verbose_name="Страна"
    )
    
    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['name']
        # Город уникален в рамках страны
        unique_together = ['name', 'country']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"
        
class Occupation(models.Model):
    
    name = models.CharField(max_length=200, unique=True, verbose_name="Профессия")
    industry = models.CharField(max_length=200, verbose_name="Индустрия")
    domain = models.CharField(max_length=200, verbose_name="Домен")
    
    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"
        ordering = ['name']
    
    def __str__(self):
        return self.name
        
class HistoricalFigure(models.Model):
    
    article_id = models.IntegerField(unique=True, verbose_name="ID статьи")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    birth_year = models.IntegerField(blank=True, null=True, verbose_name="Год рождения")
    
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='historical_figures',
        blank=True,
        null=True,
        verbose_name="Место рождения"
    )
    occupation = models.ForeignKey(
        Occupation,
        on_delete=models.PROTECT,
        related_name='historical_figures',
        blank=True,
        null=True,
        verbose_name="Профессия"
    )
    
    page_views = models.BigIntegerField(default=0, verbose_name="Количество просмотров страницы")
    average_views = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.0,
        verbose_name="Среднее количество просмотров"
    )
    historical_popularity_index = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0.0,
        verbose_name="Индекс исторической популярности"
    )
    
    article_languages = models.IntegerField(
        default=0, 
        verbose_name="Количество языков статьи"
    )
    
    # Дополнительные поля для данных, которые могут отсутствовать в нормализованных таблицах
    original_city_name = models.CharField(max_length=100, blank=True, verbose_name="Город (оригинал)")
    original_country_name = models.CharField(max_length=100, blank=True, verbose_name="Страна (оригинал)")
    original_continent_name = models.CharField(max_length=100, blank=True, verbose_name="Континент (оригинал)")
    original_occupation_name = models.CharField(max_length=200, blank=True, verbose_name="Профессия (оригинал)")
    original_industry_name = models.CharField(max_length=200, blank=True, verbose_name="Сфера деятельности (оригинал)")
    original_domain_name = models.CharField(max_length=200, blank=True, verbose_name="Домен (оригинал)")
    
    class Meta:
        verbose_name = "Историческая личность"
        verbose_name_plural = "Исторические личности"
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['birth_year']),
            models.Index(fields=['historical_popularity_index']),
            models.Index(fields=['article_languages']),
            models.Index(fields=['page_views']),
        ]
    
    def __str__(self):
        return self.full_name
    
    @property
    def birth_location(self):
        """Возвращает место рождения в удобном формате"""
        if self.city:
            return str(self.city)
        elif self.original_city_name and self.original_country_name:
            return f"{self.original_city_name}, {self.original_country_name}"
        return "Не указано"
    
    @property
    def popularity_category(self):
        """Определяет категорию популярности на основе индекса"""
        if self.historical_popularity_index >= 24.0:
            return "Очень высокая"
        elif self.historical_popularity_index >= 21.0:
            return "Высокая"
        elif self.historical_popularity_index >= 18.0:
            return "Средняя"
        elif self.historical_popularity_index >= 14.0:
            return "Низкая"
        else:
            return "Очень низкая"
        
