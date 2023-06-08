from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CreateListingForm, Bid
from .models import User, Listing
from django.contrib import messages



def index(request):
    return render(request, "auctions/index.html")


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.warning(request, 'Logged out')
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
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
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

def listing(request, id):

    listing = Listing.objects.get(pk=id)
    print(listing.user.id)
    print(listing.bidcount())

    return render(request, "auctions/listing.html", {
        "id" : listing.id,
        "title": listing.title,
        "description": listing.description,
        "image_url": listing.image,
        "created": listing.user,
        "price": listing.starting_bid,
        "bidform": Bid(),
        "bid_count": listing.bidcount()
    })

@login_required
def bid(request, listing_id):
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
