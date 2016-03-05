from django.db import models

Role=(
	(0, 'Student'),
	(1, 'Instructor')
)

class User(models.Model):
	userID = models.CharField(max_length=8, blank = False, null = False, primary_key=True)
	password = models.CharField(max_length=20, blank = False, null = False)
	name = models.CharField(max_length=50, blank = False, null = False)
	email = models.CharField(max_length=50, blank=False, null = False)
	contact = models.IntegerField(default=0)
	role = models.BooleanField(default = 'true', choices= Role)

	def __str__(self):
		return self.name + " [" + self.userID + "]"


class Instructor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	department = models.CharField(max_length=20)

	def __str__(self):
		return self.user.name + " [" + self.user.userID + "]"
	

CourseType=(
	(0, 'Audit'),
	(1, 'Credit')
)

Credits=(
	(0,'0'),
	(3,'3'),
	(4,'4'),
	(5,'5')
)

class Course(models.Model):
	instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
	# Format of Course ID is CCYSN	C = Course Discipline, Y = Year, S = Semester, N = Course No.
	courseID = models.CharField(max_length=5, default='Unspecified', primary_key=True)
	name = models.CharField(max_length=50, default='Unspecified')
	LTP = models.CharField(max_length=5, default='0-0-0')		# Shouldn't it be like L, T, P
	credits = models.IntegerField(default=0, choices=Credits)
	courseType = models.BooleanField(default=True, choices=CourseType)
	gradesUploaded = models.BooleanField(default=False)

	def __str__(self):
		return self.name + " [" + self.courseID + "]"


Branch=(
	(1, 'CSE'),
	(2, 'EE'),
	(3, 'ME')
)

Batch=(
	(0, 'UG'),
	(1, 'PG')
)

class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	branch = models.IntegerField(default=1, choices=Branch)
	# batch = models.CharField(max_length=6,choices=Batch)
	# semester = models.IntegerField(default=1,choices= Semester)
	batch = models.BooleanField(default=0, choices=Batch)
	year = models.IntegerField(default=2015)
	allCourses = models.ManyToManyField(Course)

	def __str__(self):
		return self.user.name + " [" + self.user.userID + "]"
	
GradeChoice=(
	('U','U'),
	('A','A'),
	('B','B'),
	('C','C'),
	('D','D'),
	('F','F'),
	('I','I'),
	('S','S'),
	('X','X')
)

class Grade(models.Model):
	ID = models.AutoField(primary_key=True)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	grade = models.CharField(max_length=1, default='U', choices=GradeChoice)

	def __str__(self):
		return self.student.user.userID + " : " + self.course.courseID + " - " + "\'" + self.grade + "\'."
		