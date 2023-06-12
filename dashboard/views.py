from django.shortcuts import render
from .forms import FeedbackForm

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard/home.html')


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = FeedbackForm()
    return render(request, 'dashboard/feedback/feedback.html', {'form': form})
