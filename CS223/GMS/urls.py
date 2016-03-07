from django.conf.urls import url

from . import views

app_name = 'GMS'
urlpatterns = [
	url(r'^$', views.home, name = 'home'),
	url(r'^login/$', views.login, name = 'login'),
	url(r'^logout/$', views.logout, name = 'logout'),
	url(r'^transcript/$', views.transcript, name = 'transcript'),
	url(r'^search/$', views.search, name = 'search'),
	url(r'^transcript/(?P<student_id>\w+)/$', views.transcript, name = 'transcript'),
	url(r'^giveGrade/$', views.giveGrade, name = 'giveGrade'),
	url(r'^giveGrade/(?P<course_id>\w+)/$', views.giveGrade, name = 'giveGrade'),
	#admin
	url(r'^students/$', views.students, name = 'students'),
	url(r'^students/add$', views.addStudent, name = 'addStudent'),
	url(r'^students/(?P<student_id>\w+)/$', views.students, name = 'students'),
	url(r'^students/(?P<student_id>\w+)/delete/$', views.deleteStudent, name = 'deleteStudent'),
	url(r'^instructors/$', views.instructors, name = 'instructors'),
	url(r'^instructors/add$', views.addInstructor, name = 'addInstructor'),
	url(r'^instructors/(?P<instructor_id>\w+)/$', views.instructors, name = 'instructors'),
	url(r'^instructors/(?P<instructor_id>\w+)/delete/$', views.deleteInstructor, name = 'deleteInstructor'),
	url(r'^courses/$', views.courses, name = 'courses'),
	url(r'^courses/add$', views.addCourse, name = 'addCourse'),
	url(r'^courses/(?P<course_id>\w+)/$', views.courses, name = 'courses'),
	url(r'^students/(?P<course_id>\w+)/delete/$', views.deleteStudent, name = 'deleteStudent'),
]