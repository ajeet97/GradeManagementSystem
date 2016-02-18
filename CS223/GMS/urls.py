from django.conf.urls import url

from . import views

app_name = 'GMS'
urlpatterns = [
	url(r'^$', views.home, name = 'home'),
	url(r'^login/', views.login, name = 'login'),
	url(r'^logout/', views.logout, name = 'logout')
]