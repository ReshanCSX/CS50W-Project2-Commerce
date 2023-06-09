from django.forms import ModelForm, TextInput, Textarea, NumberInput, Select, URLInput
from .models import Listing, Bid, Comments

class CreateListingForm(ModelForm):

    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]
        
        widgets = {
            "title" : TextInput(attrs={'class': 'form-control'}),
            "description" : Textarea(attrs={'class': 'form-control', 'rows': 3}),
            "starting_bid" : NumberInput(attrs={'class': 'form-control'}),
            "image" : URLInput(attrs={'class': 'form-control'}),
            "category" : Select(attrs={'class': 'form-select'})
        }

        labels = {
            "image" : "Image URL",
            "category" : "Select a category"
        }

class BidForm(ModelForm):

    class Meta:
        model = Bid

        fields = ["amount"]

        widgets = {
            "amount" : NumberInput(attrs={'class': 'form-control', 'aria-label' : 'Amount'})
        }

class CommentsForm(ModelForm):
    
    class Meta:
        model = Comments

        fields = ["comment"]

        widgets = {
            "comment" : Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'comments'})
        }