from rest_framework import serializers

from myauthentication.serializers import UserSerializer
from .models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Transactions
        fields = '__all__'
