from rest_framework import serializers

from myauthentication.serializers import UserSerializer
from .models import *


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    is_active = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Subscription
        fields = ['user','plan','start_date','end_date','is_active','is_free_trial','remaining_days']

    def get_is_active(self, obj):
        return obj.is_active

    def get_remaining_days(self, obj):
        return obj.remaining_days