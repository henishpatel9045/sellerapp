from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils import timezone

from . import models

admin.site.site_header = "SellerApp"
admin.site.index_title = "Dashboard"

# ---------------------------USER ADMIN------------------------------

class BidInline(admin.TabularInline):
    model = models.Bidding
    fields = ['user', "bid_amount", "date_created", "has_won"]
    extra = 0
    readonly_fields = ['user', "bid_amount", "date_created", "has_won"]
        
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "last_updated"]
    # inlines = [BidInline]
    search_fields = ['full_name']
    
    # ----------------------------SHOWING ONLY THEIR DATA TO NON ADMINISTRATIVE USERS---------------------------
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        print(request.user)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user.id)

# ---------------------------AUCTION ADMIN------------------------------

@admin.register(models.Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ["title", "starting_price", "is_active", "has_ended"]
    inlines = [BidInline]
    search_fields = ["title"]
    readonly_fields = ["user_won", "final_bid_price"]
    exclude = ['updated']
        
    def is_active(self, obj):
        flag = timezone.now() >= obj.start_time and timezone.now() <= obj.end_time
        if flag:
            return "YES"
        return "NO"
    
    # ----------------------------SHOWING ONLY ACTIVE AUCTIONS TO NON ADMINISTATIVE USERS---------------------------
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs    
        return qs.filter(start_time__lt=timezone.now(), end_time__gt=timezone.now())
    
# ---------------------------BIDDING ADMIN------------------------------
    
@admin.register(models.Bidding)
class BiddingAdmin(admin.ModelAdmin):
    list_display = ["id", "auction", "user", "bid_amount", "date_created"]
    readonly_fields = ["has_won"]
    
    # ----------------------------SHOWING ONLY BIDS MADE BY USER TO NON ADMINISTATIVE USERS---------------------------
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("user__user")
        if request.user.is_superuser:
            return qs
        return qs.filter(user__user=request.user.id)



################################## BASE USER MODEL ######################################

# @admin.register(get_user_model())
# class BaseUserAdmin(UserAdmin):
#     list_display = ['id', 'username', 'first_name', 'last_name', 'last_login']  
