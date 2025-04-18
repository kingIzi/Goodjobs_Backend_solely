from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import permission_required
from paymentorder.models import Transactions
from myauthentication.models import CustomUser
from paymentorder.serializers import TransactionSerializer, UserSerializer
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from django.utils import timezone
from django import forms


class UserTransactionSummaryForm(forms.Form):
    user_id = forms.IntegerField(required=True,error_messages={'required': 'Missing user id'})

@csrf_exempt
def user_transaction_summary(request):
    try:
        if request.method != 'POST': 
            raise "NOT POST"
        
        form = UserTransactionSummaryForm(request.POST)
        if not form.is_valid(): return JsonResponse({'message': form.errors},status=400)
        user_id = form.cleaned_data['user_id']
        
        requesting_user = CustomUser.objects.get(id=user_id)

        # Ensure the requesting user has the necessary permissions to view transactions and users
        if not requesting_user.has_perm('paymentorder.view_transactions') or not requesting_user.has_perm('myauthentication.view_customuser'):
            return JsonResponse(
                {'status': 'error', 'message': "You don't have permission to perform this action", 'status_code': 403},
                status=403)

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(weeks=1)

        # Calculate this week's earnings
        this_weeks_transactions = Transactions.objects.filter(transaction_date__gte=week_start, is_success=True)
        week_money = this_weeks_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate last week's earnings for comparison
        last_weeks_transactions = Transactions.objects.filter(transaction_date__range=[last_week_start, week_start], is_success=True)
        last_week_money = last_weeks_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        week_money_change = 0
        if last_week_money > 0:
            week_money_change = ((week_money - last_week_money) / last_week_money) * 100

        # Calculate today's users
        todays_users = CustomUser.objects.filter(date_joined__date=today).count()

        # Calculate yesterday's users for comparison
        yesterday = today - timedelta(days=1)
        yesterdays_users = CustomUser.objects.filter(date_joined__date=yesterday).count()
        todays_users_change = 0
        if yesterdays_users > 0:
            todays_users_change = ((todays_users - yesterdays_users) / yesterdays_users) * 100

        # Calculate total users
        total_users = CustomUser.objects.count()

        # Calculate total users last month for comparison
        first_day_of_last_month = today.replace(day=1) - timedelta(days=1)
        last_month_start = first_day_of_last_month.replace(day=1)
        last_month_end = first_day_of_last_month.replace(day=first_day_of_last_month.day)
        last_month_users = CustomUser.objects.filter(date_joined__range=[last_month_start, last_month_end]).count()
        total_users_change = 0
        if last_month_users > 0:
            total_users_change = ((total_users - last_month_users) / last_month_users) * 100

        # Calculate this month's sales
        first_day_of_this_month = today.replace(day=1)
        this_month_sales = Transactions.objects.filter(transaction_date__gte=first_day_of_this_month, is_success=True).aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate yesterday's sales for comparison
        yesterdays_sales = Transactions.objects.filter(is_success=True, transaction_date=yesterday).aggregate(Sum('amount'))['amount__sum'] or 0
        this_month_sales_change = 0
        if yesterdays_sales > 0:
            this_month_sales_change = ((this_month_sales - yesterdays_sales) / yesterdays_sales) * 100

        summary_data = {
            'week_money': f"{week_money} Tsh",
            'week_money_percentage': f"{week_money_change:.2f}% than last week",
            'todays_users': todays_users,
            'todays_users_percentage': f"{todays_users_change:.2f}% than yesterday",
            'total_users': total_users,
            'total_users_percentage': f"{total_users_change:.2f}% than last month",
            'this_month_sales': f"{this_month_sales} Tsh",
            'this_month_sales_percentage': f"{this_month_sales_change:.2f}% than yesterday"
        }

        return JsonResponse(
            {'status': 'success', 'message': 'User transaction summary fetched successfully', 'status_code': 200, 'data': summary_data},
            status=200)
    except: 
        return JsonResponse({'status': 'An error occurred on the server'},status=500)