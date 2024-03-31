from django.core.management.base import BaseCommand
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from dashboard.models import AccountData

class Command(BaseCommand):
    help = 'Receives account data from HTTP POST request'

    def handle(self, *args, **options):
        # สร้าง view สำหรับรับ HTTP POST request
        @csrf_exempt
        def receive_account_data(request):
            if request.method == 'POST':
                data = json.loads(request.body)
                account_number = data['account_number']
                balance = data['balance']
                equity = data['equity']
                margin_percentage = data['margin_percentage']
                open_orders = data['open_orders']
                AccountData.objects.create(
                    account_number=account_number,
                    balance=balance,
                    equity=equity,
                    margin_percentage=margin_percentage,
                    open_orders=open_orders
                )
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=405)  # Method Not Allowed

        # เรียกใช้ view ผ่าน URL pattern
        from django.urls import path
        urlpatterns = [
            path('receive-account-data/', receive_account_data, name='receive_account_data'),
        ]

        # เรียกใช้ URL pattern
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        from django.conf import settings
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])