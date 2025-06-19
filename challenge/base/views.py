from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse 
from .models import Question


def questioning(request, pk):
    latest = get_object_or_404(Question, id=pk)
    context = {"latest": latest}

    return render(request, 'base/index.html', context)
    