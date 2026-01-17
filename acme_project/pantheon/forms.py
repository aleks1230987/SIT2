# pantheon/forms.py
from django import forms
from .models import HistoricalFigure, City, Occupation, Country
from django.core.exceptions import ValidationError


class HistoricalFigureForm(forms.ModelForm):
    """Форма для создания и редактирования исторической личности"""
    
    # Поля для выбора связанных объектов
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        label="Место рождения (город)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    occupation = forms.ModelChoiceField(
        queryset=Occupation.objects.all(),
        required=False,
        label="Основная профессия",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Поля для создания новых связанных объектов
    new_city_name = forms.CharField(
        required=False,
        label="Или введите новый город",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название города'})
    )
    
    new_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        label="Страна для нового города",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    new_occupation_name = forms.CharField(
        required=False,
        label="Или введите новую профессию",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название профессии'})
    )
    
    class Meta:
        model = HistoricalFigure
        fields = [
            'article_id',
            'full_name',
            'birth_year',
            'city',
            'occupation',
            'page_views',
            'average_views',
            'historical_popularity_index',
            'article_languages',
            'original_city_name',
            'original_country_name',
            'original_continent_name',
            'original_occupation_name',
            'original_industry_name',
            'original_domain_name',
        ]
        widgets = {
            'article_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'page_views': forms.NumberInput(attrs={'class': 'form-control'}),
            'average_views': forms.NumberInput(attrs={'class': 'form-control'}),
            'historical_popularity_index': forms.NumberInput(attrs={'class': 'form-control'}),
            'article_languages': forms.NumberInput(attrs={'class': 'form-control'}),
            'original_city_name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_country_name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_continent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_occupation_name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_industry_name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_domain_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'article_id': 'ID статьи',
            'full_name': 'Полное имя',
            'birth_year': 'Год рождения',
            'page_views': 'Просмотры страницы',
            'average_views': 'Средние просмотры',
            'historical_popularity_index': 'Индекс популярности',
            'article_languages': 'Языки статьи',
        }
    
    def clean(self):
        """Кастомная валидация формы"""
        cleaned_data = super().clean()
        article_id = cleaned_data.get('article_id')
        
        # Проверка уникальности article_id при создании (не при редактировании)
        if self.instance.pk is None:  # Новая запись
            if HistoricalFigure.objects.filter(article_id=article_id).exists():
                raise ValidationError("Историческая личность с таким ID статьи уже существует.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Переопределение метода сохранения для обработки связанных объектов"""
        instance = super().save(commit=False)
        
        # Создание нового города, если указан
        new_city_name = self.cleaned_data.get('new_city_name')
        new_country = self.cleaned_data.get('new_country')
        
        if new_city_name and new_country:
            city, created = City.objects.get_or_create(
                name=new_city_name,
                country=new_country,
                defaults={
                    'name': new_city_name,
                    'country': new_country,
                }
            )
            instance.city = city
        
        # Создание новой профессии, если указана
        new_occupation_name = self.cleaned_data.get('new_occupation_name')
        
        if new_occupation_name:
            occupation, created = Occupation.objects.get_or_create(
                name=new_occupation_name,
                defaults={
                    'name': new_occupation_name,
                    'industry': 'Не указано',
                    'domain': 'Не указано',
                }
            )
            instance.occupation = occupation
        
        if commit:
            instance.save()
            self.save_m2m()  # Если бы были ManyToMany связи
        
        return instance


class HistoricalFigureDeleteForm(forms.Form):
    """Форма для подтверждения удаления"""
    confirm = forms.BooleanField(
        required=True,
        label="Подтвердите удаление",
        help_text="Отметьте это поле для подтверждения удаления записи."
    )


class BulkImportForm(forms.Form):
    """Форма для массового импорта исторических личностей"""
    file = forms.FileField(
        label="CSV файл с данными",
        help_text="Загрузите CSV файл с колонками: article_id, full_name, birth_year, city, country, occupation, page_views, average_views, historical_popularity_index, article_languages"
    )
    update_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Обновить существующие записи",
        help_text="Если отмечено, существующие записи с таким же article_id будут обновлены"
    )
