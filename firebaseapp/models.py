from django.db import models


from myauthentication.models import CustomUser


class FirebaseApp(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=1000)
    device = models.CharField(max_length=1000)

    def __str__(self):
        return f'{self.user.username} - {self.device}'


class UserNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=1000)
    message = models.TextField()
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {"Viewed" if self.is_viewed else "Not Viewed"}'

    class Meta:
        ordering = ['-created_at']
