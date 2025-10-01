from django.shortcuts import render, get_object_or_404
from .models import Spot

def home(request):
    spots = Spot.objects.all()
    return render(request, 'spots/home.html', {'spots': spots})

def spot_list(request):
    keyword = request.GET.get('q', '')
    spots = Spot.objects.filter(title__icontains=keyword)
    return render(request, 'spots/spot_list.html', {'spots': spots, 'keyword': keyword})

def spot_detail(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    return render(request, 'spot_detail.html', {'spot': spot})

def map_view(request):
    spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return render(request, 'spots/map.html', {'spots': spots})