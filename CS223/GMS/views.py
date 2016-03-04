from django.shortcuts import render
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
	if "loggedinuserid" in request.session:
		return HttpResponseRedirect(reverse('GMS:home'))
	
	userid = request.POST.get('username', '')
	pwd = request.POST.get('password', '')

	c = {}
	c.update(csrf(request))

	if userid == '':
		return render(request, 'GMS/login.html', c)

	try:
		user = User.objects.get(userID = userid)
	except(KeyError, User.DoesNotExist):
		c.update({ 'error_message':'1. Incorrect username or password' })
		return render(request, 'GMS/login.html', c)
	else:
		if pwd != user.password :
			c.update({ 'error_message':'2. Incorrect username or password' })
			return render_to_response('GMS/login.html', c)
		else :
			request.session["loggedinuserid"] = userid
		return HttpResponseRedirect(reverse('GMS:home'))


def logout(request):
	if "loggedinuserid" in request.session:
		try:
			del request.session["loggedinuserid"]
		except(KeyError):
			return HttpResponseRedirect(reverse('GMS:home'))
		
		return render(request, 'GMS/loggedout.html')
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def giveGrade(request, course_id=''):
	# print("Course ID :" + str(course_id))
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])

		if user.role == 1 :
			instr = Instructor.objects.get(user = user)
			courses = instr.course_set.all()
			if course_id == '':
				return render(request, 'GMS/giveGrade.html', {'giveGrade' : 0, 'user' : user, 'courses' : courses})
			else:
				try:
					course = courses.get(courseID = course_id)
				except (KeyError, Course.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:giveGrade'))
				else:
					students = Student.objects.filter(allCourses = course)
					if request.method == 'POST':
						for s in students:
							try:
								g_set = s.grade_set.get(course = course)
							except (KeyError, Grade.DoesNotExist):
								g_set = Grade(student = s, course = course, grade = request.POST.get(s.user.userID, 'U'))
							else:
								g_set.grade = request.POST.get(s.user.userID, 'U')
							g_set.save()
						if course.gradesUploaded == False:
							course.gradesUploaded = True
							course.save()

						return HttpResponseRedirect(reverse('GMS:giveGrade'))
					else:
						grades = []
						for s in students:
							grade = ''
							try:
								g_set = s.grade_set.get(course = course)
							except (KeyError, Grade.DoesNotExist):
								grade = 'U'
							else:
								grade = g_set.grade
							grades.append(grade)

						return render(request, 'GMS/giveGrade.html', {'giveGrade' : 1, 
																	  'user' : user,
																	  'students' : students,
																	  'course' : course,
																	  'grades' : grades,
																	  'std_grd_zipped' : zip(students, grades)})
				
		else :
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


# Function to get Grade points
def getGradePoints(grade):
	return {
		'A' : 10,
		'B' : 8,
		'C' : 6,
		'D' : 4,
		'F' : 0,
	}.get(grade, 0)


def transcript(request, student_id = ''):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		
		# Check if user is Instructor
		if user.role == 1:
			students = Student.objects.all()
			if student_id == '':
				return render(request, 'GMS/transcript.html', {'user' : user, 'students' : students, 'student_selected' : 0})
		
		# Generating transcript for selected student
		if student_id == '':
			student = Student.objects.get(user = user)
			print("student1 : " + str(student))
		else:
			# Generate transcript of selected student (if user = instructor)
			if user.role == 1:
				user_selected = User.objects.get(userID = student_id)
				student = Student.objects.get(user = user_selected)
			else:
				return HttpResponseRedirect(reverse('GMS:transcript'))

		# All assigned grades of selected student
		grades = student.grade_set.all()

		# Current year of selected student
		curr_year = "1"
		sem_of_curr_year = "1"

		# Array of 8 semesters' grades
		all_sem_grades = [[], [], [], [], [], [], [], []]

		# Iterate all grades
		for g in grades:
			course = g.course 
			cID = course.courseID
			grade = g.grade
			year = cID[2]
			acad_year = str(int(float(student.year)) + int(float(year)) - 1)
			acad_year_plus_one = str(int(float(acad_year)) + 1)
			acad_year = acad_year + "-" + acad_year_plus_one			# e.g. : "2014-2015"
			sem_curr_year =  cID[3]										# Semester no. of current year
			sem = (int(float(year))-1) * 2 + int(float(sem_curr_year))	# Overall semester no.

			# Add grades of current course in 'all_sem_grades' list
			all_sem_grades[sem - 1].append({'course' : course, 'grade' : grade, 'acad_year' : acad_year, 'sem_curr_year' : sem_curr_year})

			# Update current year of selected student
			if curr_year < year:
				curr_year = year
				if sem_of_curr_year < sem_curr_year:
					sem_of_curr_year = sem_curr_year

		# Total semesters count of selected student (till now)
		total_sems = (int(float(curr_year))-1) * 2 + int(float(sem_of_curr_year))

		# Calculating SPIs and CPIs
		cpi = 0
		total_points = 0
		points = 0
		for sem_grades in all_sem_grades:
			total_sem_points = 0
			sem_points = 0
			if sem_grades.__len__():
				for g in sem_grades:
					total_sem_points += g['course'].credits * 10
					# sem_points += g.get['course'].credits * getGradePoints(g['grade'])
					gradePoints = ({ 'A' : 10, 'B' : 8, 'C' : 6, 'D' : 4, 'F' : 0 }.get(g['grade'], 0))
					sem_points += g['course'].credits * gradePoints
				
				total_points += total_sem_points
				points += sem_points
				
				spi = sem_points / total_sem_points * 10
				spi = float("{0:.2f}".format(spi))	# limit to 2 decimal places

				cpi = points / total_points * 10
				cpi = float("{0:.2f}".format(cpi))	# limit to 2 decimal places

				for g in sem_grades:
					g.update({'spi' : spi, 'cpi' : cpi})

		
		return render(request, 'GMS/transcript.html', {'user' : user, 
													   'student' : student, 
													   'total_sems' : total_sems, 
													   'all_sem_grades' : all_sem_grades,
													   'student_selected' : 1})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))
