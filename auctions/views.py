from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, ListingForm


def index(request):

    listings = []

    for listing in Listing.objects.all():
        listings.append((listing, get_current_bid(listing.id)))
    
    return render(request, "auctions/index.html", {
        "listings" : listings
    })


def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            fs = form.save(commit=False)
            fs.author = request.user
            fs.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm()
    
    return render(request, "auctions/create-listing.html", {
        "form" : form
    })


def listing(request, id):
    # if user clicks on button, make get request to this route and add/remove from watchlist (like on SO)
    # reload the page
    # watchlist is a list of ints(ids)
    message = None
    winner = None
    watched = False

    try:
        listing = Listing.objects.get(pk=id)
    except ObjectDoesNotExist:
        return render(request, "auctions/error.html")

    comments = Comment.objects.filter(listing=id)

    # check if auction closed and who is the winner
    if not listing.active:
        # check for winner
        bids = Bid.objects.filter(listing=id)
        if bids:
            bid = bids.aggregate(Max('bid'))['bid__max']
            winner = Bid.objects.get(bid=bid).user


    # check if item in current users watchlist
    if request.user.is_authenticated and request.user.watchlist.filter(id=id):
    # if request.user.is_authenticated and str(id) in request.user.watchlist.split():
        watched = True

    # bid was made
    if request.method == "POST":

        if "new-bid" in request.POST:
            try:
                new_bid = float(request.POST["new-bid"])
            except:
                message = "Not a valid bid."
                pass

            if new_bid <= get_current_bid(id):
                message = "You need to place a higher bid."
            else:
                #add this bid to db
                bid = Bid(listing=listing, bid=new_bid, user=request.user)
                bid.save()

        # here we handle a get request made by clicking a button
        elif "wtchlst" in request.POST:
            if request.POST["wtchlst"] == "add":
                request.user.watchlist.add(id)
                # request.user.watchlist += " " + str(id)
                # request.user.save()
                watched = True
                message = "Item added to watchlist."
            else:
                request.user.watchlist.remove(id)
                # request.user.watchlist = request.user.watchlist.replace(str(id), "")
                # request.user.save()
                watched = False
                message = "Item removed from watchlist."

        # handle submitting a comment
        elif "comment" in request.POST:
            comment = Comment(listing=listing, user=request.user, content=request.POST["comment"])
            comment.save()

        # auction was closed
        else:
            listing.active = False
            listing.save()
        

    return render(request, "auctions/listing.html", {
            "listing" : listing, "current_bid" : get_current_bid(id), "message" : message,
            "watched" : watched, "winner" : winner, "comments" : comments
        })


def watchlist(request):
    # this one should be fine
    # watchlist = []
    # for item_id in request.user.watchlist.split():
    #     watchlist.append(Listing.objects.get(pk=item_id))

    return render(request, "auctions/watchlist.html", {
        "watchlist" : request.user.watchlist.all()
    })


def categories(request):
    
    return render(request, "auctions/categories.html", {
        "categories" : Listing.objects.values('category').distinct().filter(active=True)
    })


def category(request, name):
    
    listings = []

    for listing in Listing.objects.filter(category=name):
        listings.append((listing, get_current_bid(listing.id)))
    
    return render(request, "auctions/index.html", {
        "listings" : listings, "category" : name
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

            # initiate watchlist if there is none (ugly workaround - clears watchlist when user logs out)
            # if not 'watchlist' in request.session:
            #    request.session['watchlist'] = []

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
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


# Helpers
def get_current_bid(id):
    
    listing = Listing.objects.get(pk=id)
    bids = Bid.objects.filter(listing=id)
    if not bids:
        bid = listing.start_bid
    else:
        bid = bids.aggregate(Max('bid'))['bid__max']

    return bid
