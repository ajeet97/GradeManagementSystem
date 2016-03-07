from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.db.models import Q

from .models import *

def home(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		template = 'GMS/home.html'
		if user.role == 2:
			template = 'GMS/admin/home.html'
		return render(request, template, {'user' : user})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def login(request):
	if "loggedinuserid" in request.session:
		return HttpResponseRedirect(reverse('GMS:home'))
	if request.method == 'POST':
		userid = request.POST.get('username', '')
		pwd = request.POST.get('password', '')

		c = {}
		c.update(csrf(request))

		if userid == '':
			return render(request, 'GMS/login.html', c)
		try:
			user = User.objects.get(userID = userid)
		except(KeyError, User.DoesNotExist):
			c.update({ 'error_message':'Incorrect username or password' })
			return render(request, 'GMS/login.html', c)
		else:
			if pwd != user.password :
				c.update({ 'error_message':'Incorrect username or password' })
				return render(request, 'GMS/login.html', c)
			request.session["loggedinuserid"] = userid
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return render(request, 'GMS/login.html', {})		


def logout(request):
	try:
		del request.session["loggedinuserid"]
	except(KeyError):
		return HttpResponseRedirect(reverse('GMS:home'))
	
	return HttpResponseRedirect(reverse('GMS:login'))

def giveGrade(request, course_id=''):
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
		
		# Check if user is not Student
		if user.role != 0:
			students = Student.objects.all().order_by('user_id')
			if student_id == '':
				if user.role == 1:
					return render(request, 'GMS/transcript.html', {'user' : user, 'students' : students, 'student_selected' : 0})
				else:
					return render(request, 'GMS/admin/transcript.html', {'user' : user, 'students' : students, 'student_selected' : 0})

		# Generating transcript for selected student
		if student_id == '':
			student = Student.objects.get(user = user)
		else:
			# Generate transcript of selected student (if user = instructor)
			if user.role != 0:
				try:
					user_selected = User.objects.get(userID = student_id)
				except (KeyError, User.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:transcript'))
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

		template_name = 'GMS/transcript.html'
		if user.role == 2:
			template_name = 'GMS/admin/transcript.html'

		return render(request, template_name, {'user' : user, 
													   'student' : student, 
													   'total_sems' : total_sems, 
													   'all_sem_grades' : all_sem_grades,
													   'student_selected' : 1})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def search(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])

		if user.role != 0:
			if request.method == 'POST':
				query = request.POST.get('search', '')
				search_for = request.POST.get('search_for', '')
				if search_for == "instructor_transcript" or search_for == "admin_students" or search_for == "admin_transcript":
					if query != '':
						result = User.objects.filter(Q(userID__contains = query) | Q(name__contains = query))
						result = result.filter(role = 0)

						if search_for == "instructor_transcript":
							return render(request, 'GMS/transcript.html', {'user' : user, 'students' : result, 'query' : query, 'student_selected' : 0, 'searched' : True})
						
						if search_for == "admin_transcript":
							return render(request, 'GMS/admin/transcript.html', {'user' : user, 'students' : result, 'query' : query, 'student_selected' : 0, 'searched' : True})

						students = []
						for r in result:
							s = Student.objects.get(user = r)
							students.append(s)

						return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : students, 'query' : query, 'edit' : False, 'searched' : True})
					else:
						if serach_for == "admin_students":
							return HttpResponseRedirect(reverse('GMS:students'))
						return HttpResponseRedirect(reverse('GMS:transcript'))
				elif search_for == "admin_instructors":
					if query != '':
						result = User.objects.filter(Q(userID__contains = query) | Q(name__contains = query))
						result = result.filter(role = 1)

						instructors = []
						for r in result:
							i = Instructor.objects.get(user = r)
							instructors.append(i)

						return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : instructors, 'query' : query, 'edit' : False, 'searched' : True})
					
					return HttpResponseRedirect(reverse('GMS:instructors'))
				
				return HttpResponseRedirect(reverse('GMS:home')) #TODO remove later
			
			return HttpResponseRedirect(reverse('GMS:home'))
		
		return HttpResponseRedirect(reverse('GMS:home'))
	
	return HttpResponseRedirect(reverse('GMS:login'))


#admin Views

def students(request, student_id=''):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role == 2:
			if request.method == 'POST':
				name = request.POST.get('name', '')
				userid = request.POST.get('userid', '')
				p_userid = request.POST.get('p_userid', '')
				email = request.POST.get('email', '')
				newPassword = request.POST.get('newPassword', '')
				p_password = request.POST.get('p_password', '')
				cnfPassword = request.POST.get('cnfPassword', '')
				contact = request.POST.get('contact', '')
				branch = request.POST.get('branch', '')
				year = request.POST.get('year', '')
				batch = request.POST.get('batch', '')

				if batch == '0':
					batch = False
				else:
					batch = True

				c = {}
				c = c.update(csrf(request))

				if c == None:
					c = {}

				std = {
					'user' : {
						'userID' : userid,
						'p_userID' : p_userid,
						'name' : name,
						'password' : p_password,
						'email' : email,
						'contact' : contact
					},
					'branch' : branch,
					'batch' : batch,
					'year' : year
				}

				if name != '' and userid != '' and email != '' and contact != '' and branch != '' and year != '' and batch != '':
					if newPassword != cnfPassword:
						c.update({'edit' : True, 'user' : user, 'student' : std, 'err_msg' : "Password does not match."})
						return render(request, 'GMS/admin/students.html', c)
					if newPassword == '':
						newPassword = p_password

					p_user = User.objects.get(userID = p_userid)
					p_student = Student.objects.get(user = p_user)
					if userid == p_userid:
						p_user.name = name
						p_user.email = email
						p_user.password = newPassword
						p_user.contact = contact
						p_user.save()

						p_student.branch = branch
						p_student.batch = batch
						p_student.year = year
						p_student.save()

						allStudents = Student.objects.all().order_by('user_id')

						c.update({'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "Successfully Updated"})
						
						return render(request, 'GMS/admin/students.html', c)
					else:
						try:
							new_user = User.objects.get(userID = userid)
						except (KeyError, User.DoesNotExist):
							new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 0)
							new_user.save()

							new_student = Student(user = new_user, branch = branch, batch = batch, year = year)
							new_student.save()
							
							p_student.delete()
							p_user.delete()

							allStudents = Student.objects.all().order_by('user_id')
							c.update({'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "Successfully Updated"})
							return render(request, 'GMS/admin/students.html', c)
						else:
							c.update({'user' : user, 'student' : std, 'edit' : True, 'err_msg' : "User id '%s' already exists." % userid})
							return render(request, 'GMS/admin/students.html', c)
				else:
					redirect_url = '/admin/students/%s' % p_userid
					return HttpResponseRedirect(redirect_url)

			if student_id == '':
				allStudents = Student.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/students.html', { 'user' : user, 'allStudents' : allStudents, 'edit' : False })
			else:
				try:
					requested_user = User.objects.get(userID = student_id)
				except (KeyError, User.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:students'))
				else:
					requested_student = Student.objects.get(user = requested_user)
				return render(request, 'GMS/admin/students.html', { 'user' : user, 'student' : requested_student, 'edit' : True })
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def addStudent(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if request.method == "POST":
			name = request.POST.get('name', '')
			userid = request.POST.get('userid', '')
			email = request.POST.get('email', '')
			newPassword = request.POST.get('newPassword', '')
			cnfPassword = request.POST.get('cnfPassword', '')
			contact = request.POST.get('contact', '')
			branch = request.POST.get('branch', '')
			year = request.POST.get('year', '')
			batch = request.POST.get('batch', '')

			std = {
				'user' : {
					'userID' : userid,
					'name' : name,
					'password' : newPassword,
					'email' : email,
					'contact' : contact
				},
				'branch' : branch,
				'batch' : batch,
				'year' : year
			}

			c = {}
			c = c.update(csrf(request))

			if c == None:
				c = {}
			c.update({'user' : user, 'student' : std})
			try:
				new_user = User.objects.get(userID = userid)
			except (KeyError, User.DoesNotExist):
				if newPassword != cnfPassword:
					c.update({'err_msg' : "Password does not match."})
					return render(request, 'GMS/admin/addStudent.html', c)
				new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 0)
				new_user.save()

				new_student = Student(user = new_user, branch = branch, batch = batch, year = year)
				new_student.save()

				allStudents = Student.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The user with userid = '%s' was added successfully." % userid})
			else:
				c.update({'err_msg' : "User id %s already exists." % userid})
				return render(request, 'GMS/admin.addStudent.html', c)

		return render(request, 'GMS/admin/addStudent.html', {'user' : user})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def deleteStudent(request, student_id):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		if user.role == 2:
			try:
				requested_user = User.objects.get(userID = student_id)
			except (KeyError, User.DoesNotExist):
				return HttpResponseRedirect(reverse('GMS:students'))
			else:
				requested_student = Student.objects.get(user = requested_user)
				requested_student.delete()
				requested_user.delete()

				allStudents = Student.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The user with userid = '%s' was deleted successfully." % student_id})
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def instructors(request, instructor_id = ''):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role == 2:
			if request.method == 'POST':
				name = request.POST.get('name', '')
				userid = request.POST.get('userid', '')
				p_userid = request.POST.get('p_userid', '')
				email = request.POST.get('email', '')
				newPassword = request.POST.get('newPassword', '')
				p_password = request.POST.get('p_password', '')
				cnfPassword = request.POST.get('cnfPassword', '')
				contact = request.POST.get('contact', '')
				department = request.POST.get('department', '')

				c = {}
				c = c.update(csrf(request))

				if c == None:
					c = {}

				ins = {
					'user' : {
						'userID' : userid,
						'p_userID' : p_userid,
						'name' : name,
						'password' : p_password,
						'email' : email,
						'contact' : contact
					},
					'department' : department
				}

				if name != '' and userid != '' and email != '' and contact != '' and department != '':
					if newPassword != cnfPassword:
						c.update({'edit' : True, 'user' : user, 'instructor' : ins, 'err_msg' : "Password does not match."})
						return render(request, 'GMS/admin/instructors.html', c)
					if newPassword == '':
						newPassword = p_password

					p_user = User.objects.get(userID = p_userid)
					p_instructor = Instructor.objects.get(user = p_user)
					if userid == p_userid:
						p_user.name = name
						p_user.email = email
						p_user.password = newPassword
						p_user.contact = contact
						p_user.save()

						p_instructor.department = department
						p_instructor.save()

						allInstructors = Instructor.objects.all().order_by('user_id')

						c.update({'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "Successfully Updated"})
						
						return render(request, 'GMS/admin/instructors.html', c)
					else:
						try:
							new_user = User.objects.get(userID = userid)
						except (KeyError, User.DoesNotExist):
							new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 1)
							new_user.save()

							new_instructor = Instructor(user = new_user, department = department)
							new_instructor.save()
							
							p_instructor.delete()
							p_user.delete()

							allInstructors = Instructor.objects.all().order_by('user_id')
							c.update({'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "Successfully Updated"})
							return render(request, 'GMS/admin/instructors.html', c)
						else:
							c.update({'user' : user, 'instructor' : ins, 'edit' : True, 'err_msg' : "ID '%s' already exists." % userid})
							return render(request, 'GMS/admin/instructors.html', c)
				else:
					redirect_url = '/admin/instructors/%s' % p_userid
					return HttpResponseRedirect(redirect_url)

			if instructor_id == '':
				allInstructors = Instructor.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/instructors.html', { 'user' : user, 'allInstructors' : allInstructors, 'edit' : False })
			else:
				try:
					requested_user = User.objects.get(userID = instructor_id)
				except (KeyError, User.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:instructors'))
				else:
					requested_instructor = Instructor.objects.get(user = requested_user)
				return render(request, 'GMS/admin/instructors.html', { 'user' : user, 'instructor' : requested_instructor, 'edit' : True })
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def addInstructor(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if request.method == "POST":
			name = request.POST.get('name', '')
			userid = request.POST.get('userid', '')
			email = request.POST.get('email', '')
			newPassword = request.POST.get('newPassword', '')
			cnfPassword = request.POST.get('cnfPassword', '')
			contact = request.POST.get('contact', '')
			department = request.POST.get('department', '')

			ins = {
				'user' : {
					'userID' : userid,
					'name' : name,
					'password' : newPassword,
					'email' : email,
					'contact' : contact
				},
				'department' : department
			}

			c = {}
			c = c.update(csrf(request))

			if c == None:
				c = {}

			c.update({'user' : user, 'instructor' : ins})
			try:
				new_user = User.objects.get(userID = userid)
			except (KeyError, User.DoesNotExist):
				if newPassword != cnfPassword:
					c.update({'err_msg' : "Password does not match."})
					return render(request, 'GMS/admin/addInstructor.html', c)
				new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 1)
				new_user.save()

				new_instructor = Instructor(user = new_user, department = department)
				new_instructor.save()

				allInstructors = Instructor.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The user with userid = '%s' was added successfully." % userid})
			else:
				c.update({'err_msg' : "ID %s already exists." % userid})
				return render(request, 'GMS/admin/addInstructor.html', c)

		return render(request, 'GMS/admin/addInstructor.html', {'user' : user})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def deleteInstructor(request, instructor_id):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		if user.role == 2:
			try:
				requested_user = User.objects.get(userID = instructor_id)
			except (KeyError, User.DoesNotExist):
				return HttpResponseRedirect(reverse('GMS:instructors'))
			else:
				requested_instructor = Instructor.objects.get(user = requested_user)
				requested_instructor.delete()
				requested_user.delete()

				allInstructors = Instructor.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The user with userid = '%s' was deleted successfully." % instructor_id})
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def courses(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		return render(request, 'GMS/admin/courses.html', {'user' : user})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))