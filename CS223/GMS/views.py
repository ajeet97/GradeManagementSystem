from django.shortcuts import render
from django.http import HttpResponse

def home(request):
	return HttpResponse("Hello :P")


def login(request):
	return HttpResponse("You'r seeing login page")


def logout(request):
	return HttpResponse("You'r seeing logout page")