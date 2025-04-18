from django.db.models.signals import post_save
from django.dispatch import receiver

from firebaseapp.models import UserNotification, FirebaseApp
from jobpost.models import JobPost
from myauthentication.models import CustomUser
from utilities.notification_logic import create_user_notification
#
#
# @receiver(post_save, sender=JobPost)
# def notify_users_on_new_job(sender, instance, created, **kwargs):
#     if created:
#         categories = instance.categories.all()
#
#         for category in categories:
#             users = CustomUser.objects.filter(userprofile__preferred_categories=category)
#
#             for user in users:
#                 firebase_token = FirebaseApp.objects.get(user=user).token
#                 if firebase_token:
#                     data = {
#                         'title': f'New Job Posted: {instance.job_title}',
#                         'body': 'A new job matching your interests has been posted. Check it out!',
#                         'token': firebase_token
#                     }
#                     UserNotification.objects.create(
#                         user=user,
#                         title=data['title'],
#                         message=data['body']
#                     )
#                     create_user_notification(data)
#                     # Create a UserNotification instance
#
