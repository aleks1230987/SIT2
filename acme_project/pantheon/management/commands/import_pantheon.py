# pantheon/management/commands/import_pantheon_simple.py
import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from pantheon.models import Country, City, Occupation, HistoricalFigure

class Command(BaseCommand):
    help = 'Импорт данных из Pantheon Project dataset (упрощенная версия)'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу с данными')
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'Файл {csv_file} не найден'))
            return
        
        self.stdout.write(f'Начинаем импорт из {csv_file}...')
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                total = 0
                
                for row in reader:
                    total += 1
                    
                    # Создаем или получаем страну
                    country_name = row.get('country', '').strip()
                    continent_name = row.get('continent', '').strip()
                    
                    if country_name:
                        country, _ = Country.objects.get_or_create(
                            name=country_name,
                            defaults={'continent': continent_name}
                        )
                    
                    # Создаем или получаем город
                    city_name = row.get('city', '').strip()
                    if city_name and country_name:
                        city, _ = City.objects.get_or_create(
                            name=city_name,
                            country=country,
                            defaults={
                                'state': row.get('state', '').strip() or None,
                                'latitude': row.get('latitude', '').strip() or None,
                                'longitude': row.get('longitude', '').strip() or None
                            }
                        )
                    
                    # Создаем или получаем профессию
                    occupation_name = row.get('occupation', '').strip()
                    industry_name = row.get('industry', '').strip()
                    domain_name = row.get('domain', '').strip()
                    
                    if occupation_name:
                        occupation, _ = Occupation.objects.get_or_create(
                            name=occupation_name,
                            defaults={
                                'industry': industry_name,
                                'domain': domain_name
                            }
                        )
                    
                    # Создаем историческую личность
                    article_id = row.get('article_id', '').strip()
                    if article_id:
                        try:
                            figure, created = HistoricalFigure.objects.get_or_create(
                                article_id=int(article_id),
                                defaults={
                                    'full_name': row.get('full_name', '').strip(),
                                    'birth_year': row.get('birth_year', '').strip() or None,
                                    'city': city if 'city' in locals() else None,
                                    'occupation': occupation if 'occupation' in locals() else None,
                                    'page_views': row.get('page_views', 0) or 0,
                                    'average_views': row.get('average_views', 0) or 0,
                                    'historical_popularity_index': row.get('historical_popularity_index', 0) or 0,
                                    'article_languages': row.get('article_languages', 0) or 0,
                                }
                            )
                            
                            if created and total % 100 == 0:
                                self.stdout.write(f'Импортировано {total} записей...')
                                
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Ошибка в строке {total}: {e}'))
                            continue
                
                self.stdout.write(self.style.SUCCESS(f'Импорт завершен! Обработано {total} строк.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {e}'))
