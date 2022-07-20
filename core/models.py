from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone


# Create your models here.
class User(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.first_name = self.user.first_name
        self.last_name = self.user.last_name
        return super().save(*args, **kwargs)
    
    def full_name(self):
        return self.user.get_full_name()
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ['-date_created']
        

class Auction(models.Model):
    title = models.CharField(max_length=150)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0, "Price must be greater than 0.")], default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_bidder = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="Buyer")
    current_bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # updated = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    
    # -----------------------------------FINDING WINNER OF AUCTION ONLY AFTER
    #                                   REACHING TIME LIMIT I.E. END TIME-----------------------------------------
    
    # def has_ended(self):
        
    #     #---------------------USING BOOLEAN FIELD UPDATED TO PREVENT UNNECESSARY UPDATE QUERIES SEND TO DATABASE DECREASING 5 QUERIES PER REQUEST-------------------
        
    #     if not self.updated and timezone.now() >= self.end_time:
    #         bidders = Bidding.objects.filter(auction=self.id).order_by("-bid_amount", "-date_created").values().first()
    #         if bidders:
    #             a = Auction.objects.filter(pk=self.id).first()
    #             a.user_won = User.objects.filter(pk=bidders["user_id"]).first()
    #             print(User.objects.get(pk=bidders["user_id"]).username)
    #             a.final_bid_price = bidders["bid_amount"]
    #             a.updated = True
    #             a.save()
    #         return "YES"
    #     elif self.updated:
    #         return "YES"
    #     return "NO"
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_created']
        
        
class Bidding(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0, "Price must be greater than 0.")])
    has_won = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}-{self.auction}"
    
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            auction = Auction.objects.get(pk=self.auction.pk)
            if(self.bid_amount > auction.current_bid_price):
                auction.current_bid_price = self.bid_amount
                auction.current_bidder = self.user
            return super().save(*args, **kwargs)
    
    # ---------------------------------HANDLING ANOMALIES FOR PREDICATES 
    #                                 BID AMOUNT > STARTING PRICE 
    #                                 AUCTION MUST BE ACTIVE TO MAKE A BID----------------------------------
    
    class Meta:
        ordering = ['auction', '-date_created']
        