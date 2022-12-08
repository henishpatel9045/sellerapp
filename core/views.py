from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import models, serializers


    ################################ GET, DELETE, PUT, PATCH ######################################
class UserViewSet(GenericViewSet, ListModelMixin):
    def get_queryset(self):
        qs = models.User.objects.all()
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(user_id=user.id)
    
    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            user = get_user_model().objects.get(id=user.id)
            res = {"username": user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'response': {"message": "You are Administrator, please login to dashboard to update your profile.", "direction": "Admin user can't bid on auction he/she needs to create seperate user account to participate in bidding."}}
            return Response(res, status=status.HTTP_200_OK)
        elif not user.username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
    
    serializer_class = serializers.UserSerializer

    ################################ GET #################################
class AuctionViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    
    # ---------------------------PROTECTING AUCTION DATA FROM NON-ADMINISTRATOR----------------------------------
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Auction.objects.all()
        return models.Auction.objects.filter(start_time__lt=timezone.now(), end_time__gt=timezone.now())
    
    def update(self, request, *args, **kwargs):
        if (self.request.user.is_superuser):
            return super().update(request, *args, **kwargs)
        return Response({"error": "Only admin can update auction."}, status=status.HTTP_401_UNAUTHORIZED)
    
    def create(self, request, *args, **kwargs):
        if (self.request.user.is_superuser):
            return super().create(request, *args, **kwargs)
        return Response({"error": "Only admin can add auction."}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer_class = serializers.AuctionSerializer
    
    ################################ GET, POST ######################################
class BiddingViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    
    # -------------------------RETRIEVING RECORDS HAVING AUCTION SAME AS REQUESTED----------------------------------
    
    def get_queryset(self):
        return models.Bidding.objects.filter(auction=self.kwargs['auction_pk'])
    
    # --------------------------HANDLING EXCEPTION FOR BID > STARTING PRICE
    #                           AND ONLY ACTIVE AUCTION RETURNED FOR BUYERS----------------------------------
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user.pk, 'auction': self.kwargs['auction_pk']})
        return context
    
    def create(self, request, *args, **kwargs):
        if (self.request.user and not self.request.user.is_superuser):    
            bid = Decimal(request.data['bid_amount'])
            auction = models.Auction.objects.filter(id=request.data['auction']).first()
            
            if bid < auction.starting_price:
                return Response({
                    "error": "Bid amount must be greater than starting price of item."
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            elif auction.start_time > timezone.now():
                return Response({
                    "error": "Bid for this item is not started yet."
                }, status=status.HTTP_401_UNAUTHORIZED)
            elif auction.end_time < timezone.now():
                return Response({
                    "error": "Bid for this item is stopped."
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if bid <= auction.current_bid_price:
                return Response({
                    "error": f"Bid amount must be greater than current bid price {auction.current_bid_price}."
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            with transaction.atomic():
                res = super().create(request, *args, **kwargs)
                auction.current_bidder = models.User.objects.get(user=self.request.user) 
                auction.current_bid_price = bid
                auction.save()
                return res
                
        return Response({"error": "No user found."}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer_class = serializers.BiddingSerializer

    