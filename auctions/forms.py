from django.forms import ModelForm, TextInput, Textarea, NumberInput, Select, URLInput
from .models import NewListing

class CreateListingForm(ModelForm):

    class Meta:
        model = NewListing
        fields = ["title", "description", "starting_bid", "image", "category"]

        styles = {'class': 'form-control'}
        
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