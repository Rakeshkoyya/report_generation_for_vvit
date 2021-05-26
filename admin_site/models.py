from django.db import models
from numpy import mod

# Create your models here.
class firstyear(models.Model):
	regd_number = models.CharField(max_length=15)
	# full_name = models.CharField(max_length=50)
	# branch=models.CharField(default='null', max_length=30)

class secondyear(models.Model):
	regd_number = models.CharField(max_length=15)
	# full_name = models.CharField(max_length=50)
	# branch=models.CharField(default='null', max_length=30)

class thirdyear(models.Model):
	regd_number = models.CharField(max_length=15)
	# full_name = models.CharField(max_length=50)
	# branch=models.CharField(default='null', max_length=30)

class fourthyear(models.Model):
	regd_number = models.CharField(max_length=15)
	# full_name = models.CharField(max_length=50)
	# branch=models.CharField(default='null', max_length=30)

class count_info(models.Model):
	total_reports=models.IntegerField()
	id_number=models.IntegerField()