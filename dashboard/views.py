from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import UserAccount, AccountData
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import json
from .models import AccountData
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def landing_page(request):
    return render(request, 'landing_page.html')




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username, email, password)
        account_number = request.POST['account_number']
        user_account = UserAccount(user=user, account_number=account_number)
        user_account.save()
        
        return redirect('login')
    else:
        return render(request, 'register.html')
    

def logout_view(request):
    logout(request)
    return redirect('landing_page')


def is_update_time():
    current_time = datetime.now().time()
    update_time = time(20, 0)  # 20:00 น.
    return current_time >= update_time


@login_required
def dashboard_view(request):
    if request.user.is_authenticated:
        user_accounts = request.user.useraccount_set.all()
        account_data_list = []
        for user_account in user_accounts:
            account_number = user_account.account_number
            account_data = AccountData.objects.filter(account_number=account_number).order_by('timestamp')
            
            if account_data:
                if account_data.count() == 1 or is_update_time():
                    balance = account_data.last().balance
                    equity = account_data.last().equity
                    margin_percentage = account_data.last().margin_percentage
                    open_orders = account_data.last().open_orders
                else:
                    account_data = account_data.exclude(timestamp__date=datetime.now().date())
                    balance = account_data.last().balance
                    equity = account_data.last().equity
                    margin_percentage = account_data.last().margin_percentage
                    open_orders = account_data.last().open_orders

                # Calculate Unrealized P/L
                unrealized_pl = equity - balance
                unrealized_pl = round(unrealized_pl, 2)
                unrealized_pl_color = 'red' if unrealized_pl < 0 else 'green'

                # Calculate Drawdown
                if balance != 0:
                    drawdown = (unrealized_pl / balance) * 100
                    drawdown = round(drawdown, 2)
                    drawdown_color = 'red' if drawdown < 0 else 'green'
                    if drawdown > 0:
                        drawdown = 0
                else:
                    drawdown = 0
                    drawdown_color = 'green'

                balance_data = [data.balance for data in account_data]
                equity_data = [data.equity for data in account_data]
                timestamps = [data.timestamp.strftime('%Y-%m-%d') for data in account_data]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=timestamps, y=balance_data, name='Balance'))
                fig.add_trace(go.Scatter(x=timestamps, y=equity_data, name='Equity'))

                fig.update_layout(
                    title=f'Balance and Equity for Account {account_number}',
                    xaxis_title='Date',
                    yaxis_title='Amount (USD)',
                    legend_title='Account',
                    font=dict(size=10),
                    margin=dict(l=40, r=40, t=40, b=40),
                    hovermode='x unified'
                )

                chart_div = fig.to_html(full_html=False)

                account_data_list.append({
                    'account_number': account_number,
                    'balance': balance,
                    'equity': equity,
                    'unrealized_pl': unrealized_pl,
                    'unrealized_pl_color': unrealized_pl_color,
                    'drawdown': drawdown,
                    'drawdown_color': drawdown_color,
                    'margin_percentage': margin_percentage,
                    'open_orders': open_orders,
                    'chart_div': chart_div
                })

        return render(request, 'dashboard.html', {'account_data_list': account_data_list})
    else:
        return redirect('login')


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


@login_required
def get_dashboard_data(request):
    if request.user.is_authenticated:
        account_number = request.GET.get('account_number')
        if account_number:
            try:
                user_account = request.user.useraccount_set.get(account_number=account_number)
                account_data = AccountData.objects.filter(account_number=account_number).order_by('-timestamp')
                if account_data:
                    balance = account_data[0].balance
                    equity = account_data[0].equity
                    unrealized_pl = equity - balance
                    unrealized_pl = round(unrealized_pl, 2)
                    if balance != 0:
                        drawdown = (unrealized_pl / balance) * 100
                        drawdown = round(drawdown, 2)
                    else:
                        drawdown = 0

                    data = {
                        'balance': balance,
                        'equity': equity,
                        'unrealized_pl': unrealized_pl,
                        'drawdown': drawdown,
                    }
                    return JsonResponse(data)
            except UserAccount.DoesNotExist:
                pass
    return JsonResponse({})


@login_required
def add_account(request):
    if request.method == 'POST':
        account_number = request.POST['account_number']
        user_account = UserAccount(user=request.user, account_number=account_number)
        user_account.save()
    return redirect('dashboard')


@login_required
def delete_one_account(request):
    if request.method == 'POST':
        account_number = request.POST['account_number']
        password = request.POST['password']
        user = request.user
        if check_password(password, user.password):
            try:
                account = UserAccount.objects.get(user=user, account_number=account_number)
                account.delete()
                messages.success(request, f'Account {account_number} has been deleted.')
            except UserAccount.DoesNotExist:
                messages.error(request, f'Account {account_number} does not exist.')
        else:
            messages.error(request, 'Invalid password.')
    return redirect('dashboard')


@login_required
def delete_all_accounts(request):
    if request.method == 'POST':
        password = request.POST['password']
        user = request.user
        if check_password(password, user.password):
            UserAccount.objects.filter(user=user).delete()
            messages.success(request, 'All accounts have been deleted.')
        else:
            messages.error(request, 'Invalid password.')
    return redirect('dashboard')