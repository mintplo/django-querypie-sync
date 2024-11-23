from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    age = models.IntegerField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    position = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    employees = models.ManyToManyField(Employee, related_name="departments")

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=100)
    departments = models.ManyToManyField(Department, related_name="companies")

    def __str__(self):
        return self.name
