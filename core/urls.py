from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views

router = DefaultRouter()
router.register("me", views.UserViewSet, basename="User Viewset")
router.register("auctions", views.AuctionViewSet, basename="Auction Viewset")

auction_router = NestedDefaultRouter(router, "auctions", lookup="auction")
auction_router.register("bid", views.BiddingViewSet, basename="Bidding Viewset")


urlpatterns = router.urls + auction_router.urls
