from django.db import models

Role=(
	(1, 'Instructor'),
	(0, 'Student')
)

class User(models.Model):
	userID = models.CharField(max_length=8, blank = False, null = False)
	name = models.CharField(max_length=50, blank = False, null = False)
	password = models.CharField(max_length=20, blank = False, null = False)
	role = models.BooleanField(default = 'true', choices= Role)
	contact = models.IntegerField(default=0)

	def __str__(self):
		return self.name + " [" + self.userID + "]"

class Instructor(models.Model):
	user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	department = models.CharField(max_length=20)

	def __str__(self):
		return self.user_id.name + " [" + self.user_id.userID + "]"
	

Branch=(
	(1, 'CSE'),
	(2, 'EE'),
	(3, 'ME')
)

Batch=(
	('1', 'UG2012'),
	('2', 'UG2013'),
	('3', 'UG2014'),
	('4','UG2015')
)

Semester=(
	(1, '1'),
	(2, '2'),
	(3, '3'),
	(4, '4'),
	(5, '5'),
	(6, '6'),
	(7, '7'),
	(8, '8')
	)
class Student(models.Model):
	user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	branch = models.IntegerField(default =1, choices=Branch)
	batch = models.CharField(max_length=6,choices=Batch)
	semester = models.IntegerField(default=1,choices= Semester)

	def __str__(self):
		return self.user_id.name + " [" + self.user_id.userID + "]"
	

CourseType=(
	(1, 'Credit'),
	(0, 'Audit')
)

Credits=(
	(0,'0'),
	(3,'3'),
	(4,'4'),
	(5,'5')
)

class Course(models.Model):
	instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
	courseID = models.CharField(max_length=5)
	name = models.CharField(max_length=50, default = 'Unspecified')
	LTP = models.CharField(max_length =5)
	credits = models.IntegerField(default=0,choices=Credits)
	courseType = models.BooleanField(default='true',choices = CourseType)
	def __str__(self):
		return self.name + " [" + self.courseID + "]"

class Courses_CSE(models.Model):
	sem = models.IntegerField(choices=Semester,primary_key=True)
	courses = models.ManyToManyField(Course)
	def __str__(self):
		return "Semester " + str(self.sem) +" Courses"

class Courses_ME(models.Model):
	sem = models.IntegerField(choices=Semester,primary_key=True)
	courses = models.ManyToManyField(Course)
	def __str__(self):
		return "Semester " + str(self.sem) +" Courses"

class Courses_EE(models.Model):
	sem = models.IntegerField(choices=Semester,primary_key=True)
	courses = models.ManyToManyField(Course)
	def __str__(self):
		return "Semester " + str(self.sem) +" Courses"