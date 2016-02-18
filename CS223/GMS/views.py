from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf

from .models import User

def home(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		return render(request, 'GMS/home.html', {'user' : user})
		# return HttpResponse("Hello, " + request.session["loggedinuserid"])
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def login(request):
	userid = request.POST.get('username', '')
	pwd = request.POST.get('password', '')

	c = {}
	c.update(csrf(request))

	if "loggedinuserid" in request.session:
		return HttpResponseRedirect(reverse('GMS:home'))

	if userid == '':
		return render_to_response('GMS/login.html', c)

	try:
		user = User.objects.get(userID = userid)
	except(KeyError, User.DoesNotExist):
		c.update({ 'error_message':'1. Incorrect username or password' })
		return render_to_response('GMS/login.html', c)
	else:
		if pwd != user.password :
			c.update({ 'error_message':'2. Incorrect username or password' })
			return render_to_response('GMS/login.html', c)
		else :
			request.session["loggedinuserid"] = userid
			return HttpResponseRedirect(reverse('GMS:home'))


def logout(request):
	try:
		del request.session["loggedinuserid"]
	except(KeyError):
		return HttpResponseRedirect(reverse('GMS:home'))
	
	return render(request, 'GMS/loggedout.html')