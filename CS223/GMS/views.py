from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.db.models import Q
# from validate_email import validate_email

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
				return render(request, 'GMS/giveGrade.html', {'giveGrade' : 0, 'user' : user, 'courses' : courses, 'curr_tab' : 'giveGrade'})
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
																	  'std_grd_zipped' : zip(students, grades),
																	  'curr_tab' : 'giveGrade'})
				
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
					return render(request, 'GMS/transcript.html', {'user' : user, 'students' : students, 'student_selected' : 0, 'curr_tab' : 'transcript'})
				else:
					return render(request, 'GMS/admin/transcript.html', {'user' : user, 'students' : students, 'student_selected' : 0, 'curr_tab' : 'transcript'})

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
													   'student_selected' : 1,
													   'curr_tab' : 'transcript'})
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
							return render(request, 'GMS/transcript.html', {'user' : user, 'students' : result, 'query' : query, 'student_selected' : 0, 'searched' : True, 'curr_tab' : 'transcript'})
						
						if search_for == "admin_transcript":
							return render(request, 'GMS/admin/transcript.html', {'user' : user, 'students' : result, 'query' : query, 'student_selected' : 0, 'searched' : True, 'curr_tab' : 'transcript'})

						students = []
						for r in result:
							s = Student.objects.get(user = r)
							students.append(s)

						return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : students, 'query' : query, 'edit' : False, 'searched' : True, 'curr_tab' : 'students'})
					else:
						if search_for == "admin_students":
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

						return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : instructors, 'query' : query, 'edit' : False, 'searched' : True, 'curr_tab' : 'instructors'})
					
					return HttpResponseRedirect(reverse('GMS:instructors'))
				elif search_for == "admin_courses":
					if query != '':
						result = Course.objects.filter(Q(courseID__contains = query) | Q(name__contains = query))
						return render(request, 'GMS/admin/courses.html', {'user' : user, 'allCourses' : result, 'query' : query, 'edit' : False, 'searched' : True, 'curr_tab' : 'courses'})

					return HttpResponseRedirect(reverse('GMS:courses'))

				# return HttpResponseRedirect(reverse('GMS:home')) #TODO remove later
			
			# return HttpResponseRedirect(reverse('GMS:home'))
		
		return HttpResponseRedirect(reverse('GMS:home'))
	
	return HttpResponseRedirect(reverse('GMS:login'))


#admin Views

def students(request, student_id=''):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role == 2:
			allCourses = Course.objects.all().extra(select = {'lower_course_id' : 'lower(courseID)'}).order_by('lower_course_id')
			if request.method == 'POST':
				name = request.POST.get('name', '')
				userid = request.POST.get('userid', '')
				p_userid = request.POST.get('p_userid', '')
				email = request.POST.get('email', '')
				newPassword = request.POST.get('newPassword', '')
				p_password = request.POST.get('p_password', '')
				cnfPassword = request.POST.get('cnfPassword', '')
				contact = request.POST.get('contact', '')
				# branch = request.POST.get('branch', '')
				year = request.POST.get('year', '')
				batch = request.POST.get('batch', '')
				if userid[3] == 'C':
					branch = 1
				elif userid[3] == 'E':
					branch = 2
				else:
					branch = 3
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
						c.update({'edit' : True, 'user' : user, 'student' : std, 'err_msg' : "Password does not match.", 'curr_tab' : 'students'})
						return render(request, 'GMS/admin/students.html', c)
					if newPassword == '':
						newPassword = p_password

					p_user = User.objects.get(userID = p_userid)
					p_student = Student.objects.get(user = p_user)
				
					p_reg_courses = p_student.allCourses.all()
					
					courses_to_be_reg = []

					if userid == p_userid:
						p_user.name = name
						p_user.email = email
						p_user.password = newPassword
						p_user.contact = contact
						p_user.save()


						for c1 in allCourses:
							if request.POST.get(c1.courseID, ''):
								try:
									in_prc = p_reg_courses.get(courseID = c1.courseID)
								except (KeyError, Course.DoesNotExist):
									c1.gradesUploaded = False
									c1.save()
								courses_to_be_reg.append(c1)

						p_student.branch = branch
						p_student.batch = batch
						p_student.year = year
						p_student.allCourses = courses_to_be_reg
						p_student.save()

						allStudents = Student.objects.all().order_by('user_id')

						c.update({'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The Student with Roll No. = '%s' was updated successfully." % userid, 'curr_tab' : 'students'})
						
						return render(request, 'GMS/admin/students.html', c)
					else:
						try:
							new_user = User.objects.get(userID = userid)
						except (KeyError, User.DoesNotExist):
							new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 0)
							new_user.save()

							new_student = Student(user = new_user, branch = branch, batch = batch, year = year)
							new_student.save()
							
							for c1 in allCourses:
								if request.POST.get(c1.courseID, ''):
									c1.gradesUploaded = False
									c1.save()
									courses_to_be_reg.append(c1)

							new_student.allCourses = courses_to_be_reg
							new_student.save()
							
							p_student.delete()
							p_user.delete()

							allStudents = Student.objects.all().order_by('user_id')
							c.update({'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The Student with Roll No. = '%s' was updated successfully." % userid, 'curr_tab' : 'students'})
							return render(request, 'GMS/admin/students.html', c)
						else:
							for c1 in allCourses:
								if request.POST.get(c1.courseID, ''):
									courses_to_be_reg.append(c1)

							c.update({'user' : user, 
									  'student' : std,
									  'allCourses' : allCourses,
									  'p_reg_courses' : courses_to_be_reg, 
									  'edit' : True, 
									  'err_msg' : "User id '%s' already exists." % userid,
									  'curr_tab' : 'students'})
							return render(request, 'GMS/admin/students.html', c)
				else:
					redirect_url = '/admin/students/%s' % p_userid
					return HttpResponseRedirect(redirect_url)

			if student_id == '':
				allStudents = Student.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/students.html', { 'user' : user, 'allStudents' : allStudents, 'edit' : False, 'curr_tab' : 'students' })
			else:
				try:
					requested_user = User.objects.get(userID = student_id)
				except (KeyError, User.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:students'))
				else:
					requested_student = Student.objects.get(user = requested_user)
				
				p_reg_courses = requested_student.allCourses.all()
				return render(request, 'GMS/admin/students.html', { 'user' : user,
																	'student' : requested_student,
									  								'p_reg_courses' : p_reg_courses, 
																	'allCourses' : allCourses,
																	'edit' : True,
																	'curr_tab' : 'students' })
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def viewStudent(request, student_id):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role != 2:
			return HttpResponseRedirect(reverse('GMS:home'))
		try:
			requested_user = User.objects.get(userID = student_id)
		except(KeyError, User.DoesNotExist):
			return HttpResponseRedirect(reverse('GMS:home'))
		else:
			try:
				student = Student.objects.get(user = requested_user)
			except(KeyError, Student.DoesNotExist):
				return HttpResponseRedirect(reverse('GMS:home'))

		reg_courses = student.allCourses.all()
		return render(request, 'GMS/admin/viewStudent.html', { 'user' : user,
															   'student' : student,
															   'reg_courses' : reg_courses,
															   'curr_tab' : 'students' })
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def addStudent(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role != 2:
			return HttpResponseRedirect(reverse('GMS:home'))
		allCourses = Course.objects.all().extra(select = {'lower_course_id' : 'lower(courseID)'}).order_by('lower_course_id')
		if request.method == "POST":
			name = request.POST.get('name', '')
			userid = request.POST.get('userid', '')
			email = request.POST.get('email', '')
			newPassword = request.POST.get('newPassword', '')
			cnfPassword = request.POST.get('cnfPassword', '')
			contact = request.POST.get('contact', '')
			# branch = request.POST.get('branch', '')
			year = request.POST.get('year', '')
			batch = request.POST.get('batch', '')

			# is_email_exist = validate_email(email, verify=True)

			if userid[3] == 'C':
				branch = 1
			elif userid[3] == 'E':
				branch = 2
			else:
				branch = 3
			if batch == '0':
				batch = False
			else:
				batch = True

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
			

			courses_to_be_reg = []


			c.update({'user' : user, 'student' : std, 'allCourses' : allCourses, 'curr_tab' : 'students'})

			try:
				new_user = User.objects.get(userID = userid)
			except (KeyError, User.DoesNotExist):
				# if is_email_exist == False:
				# 	c.update({'err_msg' : 'Email does not exists.'})
				# 	return render('GMS/admin/addStudent.html', c)

				if newPassword != cnfPassword:
					c.update({'err_msg' : "Password does not match."})
					return render(request, 'GMS/admin/addStudent.html', c)
				new_user = User(userID = userid, password = newPassword, name = name, email = email, contact = contact, role = 0)
				new_user.save()

				new_student = Student(user = new_user, branch = branch, batch = batch, year = year)
				new_student.save()
				

				for c1 in allCourses:
					if request.POST.get(c1.courseID, ''):
						c1.gradesUploaded = False
						c1.save()
						courses_to_be_reg.append(c1)

				new_student.allCourses = courses_to_be_reg
				new_student.save()

				allStudents = Student.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The user with userid = '%s' was added successfully." % userid, 'curr_tab' : 'students'})
			else:
				for c1 in allCourses:
					if request.POST.get(c1.courseID, ''):
						courses_to_be_reg.append(c1)
				c.update({'err_msg' : "User id %s already exists." % userid, 'courses_to_be_reg' : courses_to_be_reg})
				return render(request, 'GMS/admin/addStudent.html', c)

		return render(request, 'GMS/admin/addStudent.html', {'user' : user, 'allCourses' : allCourses, 'curr_tab' : 'students'})
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
				return render(request, 'GMS/admin/students.html', {'user' : user, 'allStudents' : allStudents, 'edit' : False, 'success_msg' : "The user with userid = '%s' was deleted successfully." % student_id, 'curr_tab' : 'students'})
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
				# department = request.POST.get('department', '')
				if userid[2] == 'C':
					department="Computer Science & Engineering"
				elif userid[2] == 'E':
					department="Electrical Engineering"
				else:
					department="Mechanical Engineering"
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

				c.update({'curr_tab' : 'instructors'})

				if name != '' and userid != '' and email != '' and contact != '' and department != '':
					if newPassword != cnfPassword:
						c.update({'edit' : True, 'user' : user, 'instructor' : ins, 'err_msg' : "Password does not match.", 'curr_tab' : 'instructors'})
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

						c.update({'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The Instructor with ID = '%s' was updated successfully." % userid})
						
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
							c.update({'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The Instructor with ID = '%s' was updated successfully." % userid})
							return render(request, 'GMS/admin/instructors.html', c)
						else:
							c.update({'user' : user, 'instructor' : ins, 'edit' : True, 'err_msg' : "ID '%s' already exists." % userid})
							return render(request, 'GMS/admin/instructors.html', c)
				else:
					redirect_url = '/admin/instructors/%s' % p_userid
					return HttpResponseRedirect(redirect_url)

			if instructor_id == '':
				allInstructors = Instructor.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/instructors.html', { 'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'curr_tab' : 'instructors' })
			else:
				try:
					requested_user = User.objects.get(userID = instructor_id)
				except (KeyError, User.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:instructors'))
				else:
					requested_instructor = Instructor.objects.get(user = requested_user)
				return render(request, 'GMS/admin/instructors.html', { 'user' : user, 'instructor' : requested_instructor, 'edit' : True, 'curr_tab' : 'instructors' })
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def viewInstructor(request, instructor_id):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role != 2:
			return HttpResponseRedirect(reverse('GMS:home'))
		try:
			requested_user = User.objects.get(userID = instructor_id)
		except(KeyError, User.DoesNotExist):
			return HttpResponseRedirect(reverse('GMS:home'))
		else:
			try:
				instructor = Instructor.objects.get(user = requested_user)
			except(KeyError, Instructor.DoesNotExist):
				return HttpResponseRedirect(reverse('GMS:home'))

		courses = instructor.course_set.all()
		return render(request, 'GMS/admin/viewInstructor.html', { 'user' : user,
															   	  'instructor' : instructor,
															   	  'courses' : courses,
															   	  'curr_tab' : 'instructors' })
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def addInstructor(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role != 2:
			return HttpResponseRedirect(reverse('GMS:home'))
		if request.method == "POST":
			name = request.POST.get('name', '')
			userid = request.POST.get('userid', '')
			email = request.POST.get('email', '')
			newPassword = request.POST.get('newPassword', '')
			cnfPassword = request.POST.get('cnfPassword', '')
			contact = request.POST.get('contact', '')
			# department = request.POST.get('department', '')
			if userid[2] == 'C':
				department="Computer Science & Engineering"
			elif userid[2] == 'E':
				department="Electrical Engineering"
			else:
				department="Mechanical Engineering"
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

			c.update({'user' : user, 'instructor' : ins, 'curr_tab' : 'instructors'})
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
				return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The user with userid = '%s' was added successfully." % userid, 'curr_tab' : 'instructors'})
			else:
				c.update({'err_msg' : "ID %s already exists." % userid})
				return render(request, 'GMS/admin/addInstructor.html', c)

		return render(request, 'GMS/admin/addInstructor.html', {'user' : user, 'curr_tab' : 'instructors'})
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
				return render(request, 'GMS/admin/instructors.html', {'user' : user, 'allInstructors' : allInstructors, 'edit' : False, 'success_msg' : "The Instructor with ID = '%s' was deleted successfully." % instructor_id, 'curr_tab' : 'instructors'})
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def courses(request, course_id=''):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if user.role == 2:
			if request.method == 'POST':
				name = request.POST.get('name', '')
				courseid = request.POST.get('courseid', '')
				p_courseid = request.POST.get('p_courseid', '')
				LTP = request.POST.get('LTP', '')
				# credit = request.POST.get('credit', '')
				courseType = request.POST.get('courseType', '')
				Iuserid = request.POST.get('Iuserid', '')
				temp=LTP.split("-")
				credit=(int)(temp[0])+(int)(temp[1])+((int)(temp[2]))/3
				c = {}
				c = c.update(csrf(request))

				crs = {
					'name' : name,
					'courseID' : courseid,
					'LTP' : LTP,
					'credit' : credit,
					'courseType' : courseType,
					'instructor' : Instructor.objects.get(user = User.objects.get(userID = Iuserid))
				}

				if c == None:
					c = {}

				c.update({'curr_tab' : 'courses'})

				if name != '' and courseid != '' and LTP != '' and credit != '' and courseType != '' and Iuserid != '':

					p_course = Course.objects.get(courseID = p_courseid)
					if courseid == p_courseid:
						p_course.name = name
						p_course.LTP = LTP
						p_course.credit = credit
						p_course.courseType = courseType
						p_course.instructor = Instructor.objects.get(user = User.objects.get(userID = Iuserid))
						p_course.save()

						allCourses = Course.objects.all().extra(select = {'lower_name' : 'lower(name)'}).order_by('lower_name')

						c.update({'user' : user, 'allCourses' : allCourses, 'edit' : False, 'success_msg' : "The Course with courseID = '%s' was updated successfully." % courseid})
						
						return render(request, 'GMS/admin/courses.html', c)
					else:
						try:
							new_course = Course.objects.get(courseID = courseid)
						except (KeyError, Course.DoesNotExist):
							new_course = Course(instructor=Instructor.objects.get(user = User.objects.get(userID = Iuserid)),courseID=courseid,name=name,LTP=LTP,credits=credit,courseType=courseType,gradesUploaded=0)
							new_course.save()

							p_course.delete()

							allCourses = Course.objects.all().extra(select = {'lower_name' : 'lower(name)'}).order_by('lower_name')
							c.update({'user' : user, 'allCourses' : allCourses, 'edit' : False, 'success_msg' : "The Course with courseID = '%s' was updated successfully." % courseid})
							return render(request, 'GMS/admin/courses.html', c)
						else:
							c.update({'user' : user, 'course' : crs, 'edit' : True, 'err_msg' : "ID '%s' already exists." % courseid})
							return render(request, 'GMS/admin/courses.html', c)
				else:
					redirect_url = '/admin/courses/%s' % p_courseid
					return HttpResponseRedirect(redirect_url)

			if course_id == '':
				allCourses = Course.objects.all().extra(select = {'lower_name' : 'lower(name)'}).order_by('lower_name')
				return render(request, 'GMS/admin/courses.html', { 'user' : user, 'allCourses' : allCourses, 'edit' : False, 'curr_tab' : 'courses' })
			else:
				try:
					requested_course = Course.objects.get(courseID = course_id)
				except (KeyError, Course.DoesNotExist):
					return HttpResponseRedirect(reverse('GMS:courses'))
				allInstructors = Instructor.objects.all().order_by('user_id')
				return render(request, 'GMS/admin/courses.html', { 'user' : user, 
																   'course' : requested_course, 
																   'allInstructors' : allInstructors, 
																   'edit' : True,
																   'curr_tab' : 'courses' })
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))

def addCourse(request):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session['loggedinuserid'])
		if request.method == "POST":
			name = request.POST.get('name', '')
			courseid = request.POST.get('courseid', '')
			LTP = request.POST.get('LTP', '')
			# credit = request.POST.get('credit', '')
			courseType = request.POST.get('courseType', '')
			Iuserid = request.POST.get('Iuserid', '')
			temp=LTP.split("-")
			credit=(int)(temp[0])+(int)(temp[1])+((int)(temp[2]))/3
			c = {}
			c = c.update(csrf(request))

			if c == None:
				c = {}
			c.update({'user' : user, 'curr_tab' : 'courses'})
			try:
				inst = Instructor.objects.get(user=User.objects.get(userID=Iuserid))
			except (KeyError, Instructor.DoesNotExist):
				c.update({'err_msg' : "Instructor id %s does not exists." % Iuserid})
				return render(request, 'GMS/admin/addCourse.html', c)
			else:
				try:
					course=Course.objects.get(courseID=courseid)
				except (KeyError, Course.DoesNotExist):
					crs=Course(instructor=inst, courseID=courseid, name=name, LTP=LTP, credits=credit, courseType=courseType, gradesUploaded=False)
					crs.save()

					allCourses = Course.objects.all().extra(select = {'lower_name' : 'lower(name)'}).order_by('lower_name')
					c.update({
						'allCourses' : allCourses, 
						'edit' : False, 
						'success_msg' : "The Course with courseID = '%s' was added successfully." % courseid
					})
					return render(request, 'GMS/admin/courses.html', c)	
				else:
					c.update({'err_msg' : "Course ID %s already exists." % courseid})
					return render(request, 'GMS/admin/addCourse.html', c)

		allInstructors = Instructor.objects.all().order_by('user_id')
		return render(request, 'GMS/admin/addCourse.html', {'user' : user, 'allInstructors' : allInstructors, 'curr_tab' : 'courses'})
	else:
		return HttpResponseRedirect(reverse('GMS:login'))


def deleteCourse(request, course_id):
	if "loggedinuserid" in request.session:
		user = User.objects.get(userID = request.session["loggedinuserid"])
		if user.role == 2:
			try:
				requested_course = Course.objects.get(courseID = course_id)
			except (KeyError, Course.DoesNotExist):
				return HttpResponseRedirect(reverse('GMS:courses'))
			else:
				requested_course.delete()

				allCourses = Course.objects.all().extra(select = {'lower_name' : 'lower(name)'}).order_by('lower_name')
				return render(request, 'GMS/admin/courses.html', {'user' : user, 'allCourses' : allCourses, 'edit' : False, 'success_msg' : "The Course with courseID = '%s' was deleted successfully." % course_id, 'curr_tab' : 'courses'})
		else:
			return HttpResponseRedirect(reverse('GMS:home'))
	else:
		return HttpResponseRedirect(reverse('GMS:login'))
