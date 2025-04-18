from rest_framework import serializers

from myauthentication.serializers import UserSerializer
from .models import *


class CompanySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['name','id', 'about_company', 'image']  # Specify which fields to include (or use '__all__' if needed)

    def get_image(self, obj):
        request = self.context.get('request')  # Access the request context (if using DRF with views)
        if obj.image:
            # Generate the full URL for the image
            image_url = f"https://goodthings.s3.amazonaws.com/{obj.image}"
            return image_url
        return None

class JobPostSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    is_deadline = serializers.ReadOnlyField()

    class Meta:
        model = JobPost
        fields = ['company', 'location', 'salary_min', 'salary_max', 'datetime_posted', 'job_title', 'job_type',
                  'job_description', 'id', 'job_post_url', 'is_deadline','deadline_day']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    preferred_categories = serializers.SerializerMethodField(method_name='get_preferred_categories')

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_preferred_categories(self, obj):
        # Fetching all preferred categories for the user profile
        categories = obj.preferred_categories.all()
        # Returning a list of category names using list comprehension
        category_names = [category.name for category in categories]
        return category_names


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'


class SavedJobPostSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializer()

    class Meta:
        model = SavedJobPost
        fields = ['id', 'job_post', 'saved_at']


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'
