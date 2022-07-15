from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import models, serializers


    ################################ GET, DELETE, PUT, PATCH ######################################
class UserViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet, ListModelMixin):
    def get_queryset(self):
        return models.User.objects.filter(user_id=self.request.user.id)
    
    serializer_class = serializers.UserSerializer

    ################################ GET #################################
class AuctionViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    
    # ---------------------------PROTECTING AUCTION DATA FROM NON-ADMINISTRATOR----------------------------------
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Auction.objects.all()
        return models.Auction.objects.filter(start_time__lt=timezone.now(), end_time__gt=timezone.now())
    
    serializer_class = serializers.AuctionSerializer
    
    ################################ GET, POST ######################################
class BiddingViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    
    # -------------------------RETRIEVING RECORDS HAVING AUCTION SAME AS REQUESTED----------------------------------
    
    def get_queryset(self):
        return models.Bidding.objects.filter(auction=self.kwargs['auction_pk'])
    
    # --------------------------HANDLING EXCEPTION FOR BID > STARTING PRICE----------------------------------
    
    def create(self, request, *args, **kwargs):
        bid = Decimal(request.data['bid_amount'])
        start_price = models.Auction.objects.filter(id=request.data['auction']).first().starting_price
        
        if bid < start_price:
            return Response({
                "error": "Bid amount must be greater than starting price of item."
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        return super().create(request, *args, **kwargs)
    
    serializer_class = serializers.BiddingSerializer
