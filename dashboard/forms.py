from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1-5 rating

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = Feedback
        fields = ['rating']
