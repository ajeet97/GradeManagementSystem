from django.conf.urls import url

from . import views

app_name = 'GMS'
urlpatterns = [
	url(r'^$', views.home, name = 'home'),
	url(r'^login/$', views.login, name = 'login'),
	url(r'^logout/$', views.logout, name = 'logout'),
	url(r'^transcript/$', views.transcript, name = 'transcript'),
	url(r'^transcript/search/$', views.search, name = 'search'),
	url(r'^transcript/(?P<student_id>\w+)/$', views.transcript, name = 'transcript'),
	url(r'^giveGrade/$', views.giveGrade, name = 'giveGrade'),
	url(r'^giveGrade/(?P<course_id>\w+)/$', views.giveGrade, name = 'giveGrade')
]