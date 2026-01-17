# pantheon/context_processors.py
import datetime
from .models import HistoricalFigure


def pantheon_context(request):
    return {
        'total_figures_global': HistoricalFigure.objects.count(),
        'current_year': datetime.datetime.now().year,
        'app_version': '1.0.0',
    }
