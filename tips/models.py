from datetime import timezone

from django.db import models

# Define choices for tips_type
TIPS_TYPE_CHOICES = [
    ('content', 'Content'),
    ('video', 'Video'),
    ('audio', 'Audio'),
]


class Tips(models.Model):
    tip_image = models.FileField(upload_to='tips/')
    tip_title = models.CharField(max_length=1000, )
    datetime_posted = models.DateTimeField(auto_now_add=True)

    tips_type = models.CharField(
        max_length=10,
        choices=TIPS_TYPE_CHOICES,
        default='content',
    )
    audio_content = models.CharField(max_length=1000,null=True,blank=True)
    video_content = models.CharField(max_length=1000,null=True,blank=True)
    writing_content = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.tip_title
