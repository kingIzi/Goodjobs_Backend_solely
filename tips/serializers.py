from rest_framework import serializers
from .models import *


class TipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tips
        fields = '__all__'
