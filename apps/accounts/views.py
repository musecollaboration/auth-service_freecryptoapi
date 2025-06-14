from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response


def test(request):
    return HttpResponse('OK')
