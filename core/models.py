from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# Create your models here.
class User(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, default=" ")
    last_name = models.CharField(max_length=50, default=" ")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return self.user.get_full_name()
    
    # -------------------------SYNC THE COMMON FIELDS BETWEEN USER CLASSES-----------------------------
    def save(self):
        user = get_user_model().objects.get(id=self.user.id)
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.save()
        return super().save()
    
    def __str__(self):
        return self.full_name()
    
    class Meta:
        ordering = ['-date_created']
        

class Auction(models.Model):
    title = models.CharField(max_length=150)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0, "Price must be greater than 0.")])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user_won = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="Buyer")
    final_bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # -----------------------------------FINDING WINNER OF AUCTION ONLY AFTER
    #                                   REACHING TIME LIMIT I.E. END TIME-----------------------------------------
    
    def has_ended(self):
        
        #---------------------USING BOOLEAN FIELD UPDATED TO PREVENT UNNECESSARY UPDATE QUERIES SEND TO DATABASE DECREASING 5 QUERIES PER REQUEST-------------------
        
        if not self.updated and timezone.now() >= self.end_time:
            bidders = Bidding.objects.filter(auction=self.id).order_by("-bid_amount", "-date_created").values().first()
            if bidders:
                a = Auction.objects.get(id=self.id)
                a.user_won = User.objects.get(id=bidders["user_id"])
                a.final_bid_price = bidders["bid_amount"]
                a.updated = True
                a.save()
            return "YES"
        elif self.updated:
            return "YES"
        return "NO"
    
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
    
    # ---------------------------------HANDLING ANOMALIES FOR PREDICATES 
    #                                 BID AMOUNT > STARTING PRICE 
    #                                 AUCTION MUST BE ACTIVE TO MAKE A BID----------------------------------
    
    def clean(self):
        if self.auction.starting_price >= self.bid_amount:
            raise ValidationError(f"Bid amount can't be less than starting price {self.auction.starting_price}.")
        elif self.auction.start_time > timezone.now():
            raise ValidationError("Bidding are not start for this item yet.")
        elif self.auction.end_time < timezone.now():
            raise ValidationError("Bidding for this item had stopped.")
    
    class Meta:
        ordering = ['auction', '-date_created']
        