from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='')
    country = models.CharField(max_length=300)
    message = models.TextField(default='')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass

    def __str__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(max_length=1023)  # lowercase, frontend must ensure it is in lowercase
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=1023)
    place_id = models.CharField(max_length=1023)
    activities = models.ManyToManyField(Activity, related_name='Activities_at_Location')
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass

    def __str__(self):
        return self.name


class Patient(models.Model):
    full_name = models.CharField(max_length=1023, null=True)
    covid_id = models.CharField(max_length=1023, null=True)
    nationality = models.CharField(max_length=300)
    state = models.CharField(max_length=300)

    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass


class PatientTimeline(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    time_range = models.CharField(max_length=1023, null=True)
    activities = models.ManyToManyField(Activity, related_name='Activities_of_Patient')
    date = models.DateField(default=None)
    state = models.CharField(max_length=300, null=True)
    country = models.CharField(max_length=300, null=True)

    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass


class PublicTimeline(models.Model):
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    time_range = models.CharField(max_length=1023, null=True)
    activities = models.ManyToManyField(Activity)
    date = models.DateField(default=None)
    state = models.CharField(max_length=300, null=True)
    country = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=2048, null=True)
    email = models.CharField(max_length=300, null=True)
    phone_number = models.CharField(max_length=300, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass


class PotentialContact(models.Model):
    probability = models.FloatField(default=0.0)
    patient_timeline = models.ForeignKey(PatientTimeline, on_delete=models.CASCADE, related_name='Timeline_of_Patient')
    public_timeline = models.ForeignKey(PublicTimeline, on_delete=models.CASCADE, related_name='Timeline_of_Public')
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Admin:
        pass
