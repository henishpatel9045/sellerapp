from django.contrib import admin
from django.utils import timezone
from . import models

admin.site.site_header = "SellerApp"
admin.site.index_title = "Dashboard"

# ---------------------------USER ADMIN------------------------------

class AuctionInline(admin.TabularInline):
    model = models.Auction
    fields = ["title", 'starting_price', 'final_bid_price', "end_time"]
    readonly_fields = ["title", 'starting_price', 'final_bid_price', "end_time"]
    extra = 0 
        
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "last_updated"]
    inlines = [AuctionInline]
    search_fields = ['full_name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('user').filter(id=request.user.id)

# ---------------------------AUCTION ADMIN------------------------------

class BidInline(admin.TabularInline):
    model = models.Bidding
    fields = ['user', "bid_amount", "date_created", "has_won"]
    extra = 0
    readonly_fields = ['user', "bid_amount", "date_created", "has_won"]
    
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("user__user")