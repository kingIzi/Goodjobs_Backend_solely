import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Tips
from .serializers import TipsSerializer


@csrf_exempt
def fetch_tips(request):
    try:
        if request.method != 'POST': raise 'NOT POST'
        tips = Tips.objects.all()
        tips_serializer = TipsSerializer(tips, many=True).data
        return JsonResponse(
            {'status': 'success', 'message': 'Tips fetched  successfully',
             'status_code': 200, 'data': list(tips_serializer)},
            status=200)
    except: 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)


@csrf_exempt
def add_tip(request):
    if request.method == 'POST':
        # Retrieve the fields from the request
        tip_title = request.POST.get("tip_title")
        tips_type = request.POST.get("tips_type")
        audio_content = request.POST.get("audio_content", None)
        video_content = request.POST.get("video_content", None)
        writing_content = request.POST.get("writing_content", None)
        tip_image = request.FILES.get('tip_image')
        # Create a new tip instance
        try:

            new_tip = Tips(
                tip_title=tip_title,
                tips_type=tips_type,
                audio_content=audio_content,
                video_content=video_content,
                writing_content=writing_content,
                datetime_posted=timezone.now(),
                tip_image= tip_image
            )
            new_tip.save()
            return JsonResponse({
                'status': 'success',
                'status_code': 200,
                'message': 'Tip added successfully.',
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'status_code': 500,
                'data':{
                    'tip_title': tip_title,
                    'tips_type': tips_type,
                    'audio_content': audio_content,
                    'video_content': video_content,
                    'writing_content': writing_content,
                    'datetime_posted': timezone.now(),
                },
                'message': 'An error occurred while adding the tip. Please try again.',
            }, status=500)
    else:
        # If the request method is not POST, inform the user.
        return JsonResponse({
            'status': 'error',
            'status_code': 405,
            'message': 'Invalid request method. Please use POST to add a tip.'
        }, status=405)
