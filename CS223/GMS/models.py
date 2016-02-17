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
	

Branch=(
	(1, 'CSE'),
	(2, 'EE'),
	(3, 'ME')
)

class Student(models.Model):
	user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	branch = models.IntegerField(default =1, choices=Branch)
	batch = models.CharField(max_length=6, default="UG2014")
	semester = models.IntegerField(default=1)

	def __str__(self):
		return self.user_id.name + " [" + self.user_id.userID + "]"
	

CourseType=(
	(1, 'Credit'),
	(0, 'Audit')
)

class Course(models.Model):
	instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
	courseID = models.CharField(max_length=5)
	LTP = models.CharField(max_length =5)
	credits = models.IntegerField(default=0)
	courseType = models.BooleanField(default='true',choices = CourseType)
