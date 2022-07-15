from django.core.exceptions import ValidationError
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "total_bids", "auction_win", "phone_number", "country", "state", "date_created", "last_updated"]
        
    total_bids = serializers.SerializerMethodField()
    def get_total_bids(self, obj):
        res = models.Bidding.objects.filter(user=obj.id).count()
        return res
    
    auction_win = serializers.SerializerMethodField()
    def get_auction_win(self, obj):
        res = models.Auction.objects.filter(user_won=obj.id).count()
        return res
        

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Auction
        fields = ["id", "title", "starting_price", "start_time", "end_time", "total_bids", "user_won", "final_bid_price"]
        
    total_bids = serializers.SerializerMethodField()
    def get_total_bids(self, obj):
        res = models.Bidding.objects.filter(auction=obj.id).count()
        return res
        
        
class BiddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bidding
        fields = ["id", "user", "auction", "bid_amount"]
    
    def create(self, validated_data):
        if validated_data['bid_amount'] < models.Auction.objects.filter(id=validated_data['auction'].id).first().starting_price:
            raise ValidationError("Bid amount must be greater than starting price for item.")
        return super().create(validated_data)
