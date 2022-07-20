from email.policy import default
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["user", "first_name", "last_name", "total_bids", "auction_win", "phone_number", "country", "state", "date_created", "last_updated"]
    
    total_bids = serializers.SerializerMethodField()
    def get_total_bids(self, obj):
        res = models.Bidding.objects.filter(user=obj.pk).count()
        return res
    
    auction_win = serializers.SerializerMethodField()
    def get_auction_win(self, obj):
        res = models.Auction.objects.filter(user_won=obj.pk).count()
        return res
        

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Auction
        fields = ["id", "title", "starting_price", "start_time", "end_time", "total_bids", "current_bidder", "current_bid_price"]
        
    total_bids = serializers.SerializerMethodField()
    def get_total_bids(self, obj):
        res = models.Bidding.objects.filter(auction=obj.id).count()
        return res
        
        
class BiddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bidding
        fields = ["id", "auction", "bid_amount"]
    
    def create(self, validated_data):
        validated_data['user'] = models.User.objects.filter(pk=self.context['user']).first()
        validated_data['auction'] = models.Auction.objects.filter(pk=self.context['auction']).first()
        return super().create(validated_data)    

#################################### DJOSER CUSTOM SERIALIZERS ######################################

class UserCreateSerializer(DjoserUserCreateSerializer):    
    # def create(self, validated_data):
    #     validated_data['is_staff'] = True
    #     return super().create(validated_data)
    
    def perform_create(self, validated_data):
        with transaction.atomic():
            user = super().perform_create(validated_data)
            models.User.objects.create(user_id=user.pk)
        return user
        
class DjangoUserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
    
    def update(self, instance, validated_data):
        with transaction.atomic():
            user = get_user_model().objects.get(pk=instance.user.pk)
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            user.save()
            print(validated_data)
            return super().update(instance, validated_data)
