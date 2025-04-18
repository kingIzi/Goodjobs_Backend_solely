import logging
from celery import shared_task
from django.apps import apps
from firebaseapp.models import FirebaseApp, UserNotification
from myauthentication.models import CustomUser as User
from utilities.notification_logic import create_user_notification

logger = logging.getLogger('celery_notification')

@shared_task
def send_notification_to_users(job_post_id):
    print(f'Starting sending notifications {job_post_id}')
    JobPost = apps.get_model('jobpost', 'JobPost')
    job_post = JobPost.objects.get(id=job_post_id)
    categories = job_post.categories.all()
    success_count = 0
    failure_count = 0

    for category in categories:
        users = User.objects.filter(userprofile__preferred_categories=category)
        for user in users:
            try:
                firebase_app = FirebaseApp.objects.filter(user=user).first()
                if firebase_app:
                    data = {
                        'title': f'New Job: {job_post.job_title} at {job_post.company.name}',
                        'body': f'A new job matching your interests at {job_post.company.name} has been posted. Check it out!',
                        'token': firebase_app.token
                    }
                    UserNotification.objects.create(
                        user=user,
                        title=data['title'],
                        message=data['body']
                    )
                    create_user_notification(data)
                    success_count += 1
                    print("Notification sent successfully to user: ", user.id)
                    logger.info(f'Notification sent successfully to user: {user.id}')
                else:
                    print("No FirebaseApp found for user: ", user.id)
                    logger.warning(f'No FirebaseApp found for user: {user.id}')
                    failure_count += 1
            except Exception as e:
                failure_count += 1
                print(f'Error sending notification to user: , Error: {str(e)}')
                logger.error(f'Error sending notification to user: , Error: {str(e)}')

    logger.info(f'Total notifications sent: {success_count}, Failed: {failure_count}')

