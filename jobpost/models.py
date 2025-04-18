from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from jobpost.celery_tasks import send_notification_to_users
from myauthentication.models import CustomUser as User


class JobCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.FileField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    about_company = models.TextField()
    image = models.ImageField(upload_to='company_images/')  # Ensure you have Pillow installed and MEDIA_URL configured

    def __str__(self):
        return self.name


class JobPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    job_title = models.CharField(max_length=1000)
    job_type = models.CharField(max_length=1000)
    salary_min = models.DecimalField(max_digits=38, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=38, decimal_places=2, null=True, blank=True)
    datetime_posted = models.DateTimeField(default=timezone.now)
    job_description = models.CharField(max_length=1000)
    job_post_url = models.CharField(max_length=1000)
    #categories = models.ManyToManyField(JobCategory, blank=True, null=True)
    #categories = models.ManyToManyField(JobCategory)
    deadline_day = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-datetime_posted']

    def is_deadline(self):
        if self.deadline_day:
            return self.deadline_day < timezone.now().date()
        return False

    def __str__(self):
        return f"{self.company.name} - {self.location}"
    

class JobPostCategories(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    job_category_id = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='user_cvs/', null=True, blank=True)
    preferred_categories = models.ManyToManyField(JobCategory, blank=True, null=True)
    #preferred_categories = models.ManyToManyField(JobCategory)

    def __str__(self):
        return f"{self.user.username}'s profile"


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    cv = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    cover_letter = models.TextField(null=True, blank=True)
    application_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, default='pending')

    class Meta:
        ordering = ['-application_date']

    def __str__(self):
        return f"Application by {self.user.username} for {self.job.job_title}"


class SavedJobPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job_post')  # Ensures a user can only save a job post once

    def __str__(self):
        return f"{self.user.username} saved {self.job_post.job_title}"


@receiver(post_save, sender=JobPost)
def notify_users_on_new_job(sender, instance, created, **kwargs):
    if created:
        send_notification_to_users.delay(instance.id)
