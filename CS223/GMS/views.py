from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf

from .models import *

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

def giveGrade(request):
	course = request.POST.get('course','')
	student_id = request.POST.get('student', '')
	grade = request.POST.get('grade','')
	
	if student_id != '':
		u = User.objects.get(userID = student_id)
		student = Student.objects.get(user_id = u)
		# semester = student.semester
		# branch = student.branch
		# if branch == 1:

		# elif branch == 2:

		# else:
		try:
			q = Grade.objects.get(student = student)
		except (KeyError, Grade.DoesNotExist):
			q = Grade(student = student, crs1 = grade, crs2 = '', crs3 = '', crs4 = '', crs5 = '', crs6 = '')
		else:
			q.crs1 = grade

		q.save()

	if "loggedinuserid" in request.session:
		# if course_id == "" or student_id == "" or grade == "" :
			user = User.objects.get(userID = request.session["loggedinuserid"])
			instr = Instructor.objects.get(user_id = user)
			crs = instr.course_set.all()
			students = Student.objects.all()
			return render(request, 'GMS/giveGrade.html', {'user' : user,'crs' : crs,'students' : students})
		# else :
			# return render(request,'GMS/giveGrade.html')

			# userStudent = User.objects.get(UserID = student_id)
			# student = Student.objects.get(user_id = userStudent)
			# gradeDB = Grade.objects.get(student = student)
			
			#TODO Remove later
			# if gradeDB.crs1 == '':
			# 	gradeDB.crs1 = grade
			# elif gradeDB.crs2 == '':
			# 	gradeDB.crs2 = grade
			# elif gradeDB.crs3 == '':
			# 	gradeDB.crs3 = grade
			# elif gradeDB.crs4 == '':
			# 	gradeDB.crs4 = grade
			# elif gradeDB.crs5 == '':
			# 	gradeDB.crs5 = grade
			# else:
				# gradeDB.crs6 = grade
			#END
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def transcript(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		# instr = Instructor.objects.get(user_id = user)
		# crs = Course.objects.all()
		# crs = instr.course_set.all()
		# crs = Course.objects.filter(instructor = instr)
		student = Student.objects.get(user_id = user)
		semester = student.semester
		branch = student.branch
		if branch == 1:
			crsall = Courses_CSE.objects.all()
		elif branch == 2:
			crsall = Courses_EE.objects.all()
		else:
			crsall = Courses_ME.objects.all()
	
		return render(request, 'GMS/transcript.html',{'user' : user,'student' : student ,'crsall' : crsall})
		# return HttpResponse("Hello, " + request.session["loggedinuserid"])
	else:
		return HttpResponseRedirect(reverse('GMS:login'))
