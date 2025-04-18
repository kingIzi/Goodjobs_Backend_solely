from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from myauthentication.models import CustomUser
from .models import FirebaseApp, UserNotification
from .serializers import UserNotificationSerializer


@csrf_exempt
def create_update_firebase(request):
    try:

        user_id = request.POST.get('user_id')
        token = request.POST.get('token')
        device = request.POST.get('device')

        try:
            FirebaseApp.objects.get(user_id=user_id, token=token)
            return JsonResponse(
                {'status': 'success', 'message': 'Firebase Profile Fetched successfully', 'status_code': 200})

        except:
            firebase_user = FirebaseApp.objects.filter(user_id=user_id)
            if firebase_user is None:
                FirebaseApp.objects.create(user_id=user_id, token=token, device=device)
                return JsonResponse(
                    {'status': 'success', 'message': 'Firebase Profile Created successfully', 'status_code': 201})
            else:
                firebase_user.delete()
                FirebaseApp.objects.create(user_id=user_id, token=token, device=device)
                return JsonResponse(
                    {'status': 'success', 'message': 'Firebase Profile Created successfully', 'status_code': 201})
    except:
        return JsonResponse(
            {'status': 'success', 'message': 'Something went wrong', 'status_code': 400})


def add_user_notification(data):
    try:
        user_id = data.get('user_id')
        title = data.get('title')
        message = data.get('message')

        user = FirebaseApp.objects.get(user_id=user_id)
        UserNotification.objects.create(user=user, title=title, message=message)

        return JsonResponse(
            {'status': 'success', 'message': 'Notification Added successfully', 'status_code': 201})
    except:
        return JsonResponse(
            {'status': 'success', 'message': 'Something went wrong', 'status_code': 400})


@csrf_exempt
def get_user_notifications(request):
    try:
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        notifications = UserNotification.objects.filter(user=user)
        notification_serializer = UserNotificationSerializer(notifications, many=True).data
        return JsonResponse(
            {'status': 'success', 'message': 'Notifications Fetched successfully', 'status_code': 200,
             'data': list(notification_serializer)})
    except:
        return JsonResponse(
            {'status': 'success', 'message': 'Something went wrong', 'status_code': 400})
