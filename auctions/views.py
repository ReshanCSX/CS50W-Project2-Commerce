from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CreateListingForm, BidForm, CommentsForm
from .models import User, Listing, Comments, Category
from django.contrib import messages



def index(request):
    listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html",{
        "listings" : listings.filter(active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # Redirect user
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.warning(request, 'You are now logged out.')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return HttpResponseRedirect(reverse("register"))

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required()
def new_listing(request):

    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            added_listing = form.save()
            messages.success(request, "Listing Created")
            return HttpResponseRedirect(reverse("listing", args=[added_listing.pk]))

    return render(request, "auctions/newlisting.html", {
        "form": CreateListingForm()
        })


def listing(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)

    if not listing.active:
        messages.error(request, "This auction is closed")

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "price": listing.highest_bid(),
        "bidform": BidForm(),
        "bid_count": listing.bidcount(),
        "watch_list": listing.watchlist_exist(request.user),
        "addcomments": CommentsForm(),
        "comments": listing.comments.all().order_by('-time'),
        "commentscount": listing.comments.all().count(),
        "user_in_bids": listing.user_in_bids(request.user)
    })


@login_required
def bid(request, listing_id):

    def bid_save():
        form.instance.user = request.user
        form.instance.listing = listing
        form.save()
        messages.success(request, "Your bid has been successfully added.")
        HttpResponseRedirect(reverse("listing", args=[listing_id]))

    if request.method == "POST":
        form = BidForm(request.POST)

        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            listing = Listing.objects.get(pk=listing_id)

            if listing.bidcount() is 0:
                if listing.highest_bid() > bid_amount:
                    messages.error(request, 'Please make sure your bid is higher than or equal to the current highest bid.')
                else:
                    bid_save()
            elif listing.highest_bid() >= bid_amount:
                messages.error(request, 'Please ensure your bid exceeds the current highest bid.')
            elif not listing.active:
                messages.error(request, 'Sorry, you cannot place a bid on a closed auction.')
            else:
                bid_save()

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def watchlistchange(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        if listing.watchlist_exist(user):
            listing.watchlist.remove(user)
            messages.warning(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        else:
            listing.watchlist.add(user)
            messages.success(request, "Item successfully added to watchlist.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def watchlist(request):
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })


@login_required
def unwatch(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        if listing.watchlist_exist(user):
            listing.watchlist.remove(user)
            messages.error(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            messages.error(request, "Item is not in watchlist")


@login_required
def comment(request, listing_id):
    
    if request.method == "POST":
        
        form = CommentsForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            form.instance.listing = Listing.objects.get(pk=listing_id)
            form.save()
            messages.success(request, "Comment added successfully.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        else:
            messages.error(request, "Failed to add comment. Please try again later.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        

def categories(request):

    categories = Category.objects.all()

    return render(request, "auctions/categories.html",{
        "categories" : categories
    })


def category_listing(request, category_id):
    
    category = Category.objects.get(pk=category_id)

    return render(request, "auctions/categorylisting.html",{
        "category": category.listings.filter(active=True),
        "category_name": category
    })


@login_required
def close_auction(request, listing_id):

    if request.method == "POST":

        listing = Listing.objects.get(pk=listing_id)

        if listing.user == request.user:
            Listing.objects.filter(pk=listing_id).update(active=False)
            messages.success(request, f"Auction successfully closed. The winning bid goes to {listing.highest_bid_user()}.") 
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Sorry, you do not have the necessary permissions to close the auction.")


