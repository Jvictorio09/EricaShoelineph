from django import forms
from .models import Comment

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    guest_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    guest_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))

    class Meta:
        model = Comment
        fields = ['guest_name', 'guest_email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a comment...'}),
        }


from django import forms
from .models import Color

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name", "hex_code"]
        widgets = {
            "hex_code": forms.TextInput(attrs={"type": "color"}),
        }



from django import forms
from .models import Order

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
