from django.conf.urls import url

from . import views

app_name = 'GMS'
urlpatterns = [
	url(r'^student/$', views.home, name = 'home'),
	url(r'^student/transcript/$', views.transcript, name = 'transcript'),
	url(r'^instructor/$', views.homeInst, name = 'homeInst'),
	url(r'^login/$', views.login, name = 'login'),
	url(r'^logout/$', views.logout, name = 'logout'),
	url(r'^giveGrade/$', views.giveGrade, name = 'giveGrade')
]