from django.db import models

# Create your models here.

STATES_CHOICES = [
	('IN-AP' , 'Andhra Pradesh'),
	('IN-AR' , 'Arunachal Pradesh'),
	('IN-AS' , 'Assam'),
	('IN-BR' , 'Bihar'),
	('IN-CT' , 'Chhattisgarh'),
	('IN-GA' , 'Goa'),
	('IN-GJ' , 'Gujarat'),
	('IN-HR' , 'Haryana'),
	('IN-HP' , 'Himachal Pradesh'),
	('IN-JK' , 'Jammu and Kashmir'),
	('IN-JH' , 'Jharkhand'),
	('IN-KA' , 'Karnataka'),
	('IN-KL' , 'Kerala'),
	('IN-MP' , 'Madhya Pradesh'),
	('IN-MH' , 'Maharashtra'),
	('IN-MN' , 'Manipur'),
	('IN-ML' , 'Meghalaya'),
	('IN-MZ' , 'Mizoram'),
	('IN-NL' , 'Nagaland'),
	('IN-OR' , 'Odisha'),
	('IN-PB' , 'Punjab'),
	('IN-RJ' , 'Rajasthan'),
	('IN-SK' , 'Sikkim'),
	('IN-TN' , 'Tamil Nadu'),
	('IN-TG' , 'Telangana'),
	('IN-TR' , 'Tripura'),
	('IN-UT' , 'Uttarakhand'),
	('IN-UP' , 'Uttar Pradesh'),
	('IN-WB' , 'West Bengal'),
	('IN-AN' , 'Andaman and Nicobar Islands'),
	('IN-CH' , 'Chandigarh'),
	('IN-DN' , 'Dadra and Nagar Haveli'),
	('IN-DD' , 'Daman and Diu'),
	('IN-DL' , 'Delhi'),
	('IN-LD' , 'Lakshadweep'),
	('IN-PY' , 'Puducherry'),
]

class Address(models.Model):
    street = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(
    	max_length=4,
    	choices= STATES_CHOICES)
    pin = models.DecimalField(
    	max_digits=6,
    	decimal_places=0)