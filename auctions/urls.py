from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="newlisting"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("watchlistchange/<int:listing_id>", views.watchlistchange, name="watchlistchange"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("unwatch/<int:listing_id>", views.unwatch, name="unwatch"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_listing, name="category_listing"),
    path("close/<int:listing_id>", views.close_auction, name="close_auction")
]
