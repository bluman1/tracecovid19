import datetime
import statistics
from statistics import mean

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.helpers import random_illustration, validate_email, generate_covid_id
from app.models import Organization, Patient, PotentialContact, PublicTimeline, PatientTimeline, Location, Activity


def show_home(request):
    if request.method == 'GET':
        illustration = random_illustration()
        return render(request, 'frontend/home.html', {'illustration': illustration})


def show_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def show_register(request):
    if request.method == 'GET':
        errors = None
        if request.GET.get('errors') == '1':
            errors = 'Email already exists. Please try again.'
        elif request.GET.get('errors') == '2':
            errors = 'Country already have CDC registered. Please contact us if this is a mistake.'
        elif request.GET.get('errors') == '3':
            errors = 'Invalid email address.'
        elif request.GET.get('errors') == '4':
            errors = 'Password should be more than 5 characters.'
        return render(request, 'backend/register.html', {'errors': errors})
    elif request.method == 'POST':
        organization = request.POST.get('organization')
        email = request.POST.get('email')
        password = request.POST.get('password')
        country = request.POST.get('country')
        if not validate_email(email):
            return HttpResponseRedirect('/new-cdc?errors=3')
        if len(password) < 6:
            return HttpResponseRedirect('/new-cdc?errors=4')
        try:
            User.objects.get(username=email)
            return HttpResponseRedirect('/new-cdc?errors=1')
        except User.DoesNotExist:
            pass
        try:
            Organization.objects.get(country=country)
            return HttpResponseRedirect('/new-cdc?errors=2')
        except Organization.DoesNotExist:
            pass
        user = User.objects.create_user(username=email, email=email)
        user.save()
        user.set_password(password)
        user.save()
        organization = Organization(user=user, name=organization, country=country)
        organization.save()
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseRedirect('/login-cdc/')
        return HttpResponseRedirect('/dashboard/')


def show_login(request):
    if request.method == 'GET':
        errors = None
        if request.GET.get('errors') == '1':
            errors = 'Email or password incorrect.'
        return render(request, 'backend/login.html', {'errors': errors})
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseRedirect('/login-cdc?errors=1')
        return HttpResponseRedirect('/dashboard/')


@login_required
def show_dashboard(request):
    if request.method == 'GET':
        organization = Organization.objects.get(user=request.user)
        positive_cases_all = []
        all_orgs = Organization.objects.all()
        for orgs in all_orgs:
            if orgs.country == organization.country:
                positive_cases = Patient.objects.filter(creator=orgs.user)
                positive_cases_all.extend(positive_cases)
        potential_contacts_all = []
        for positive_case in positive_cases_all:
            potential_contacts = PotentialContact.objects.filter(patient=positive_case)
            potential_contacts_all.extend(potential_contacts)
        public_timelines = PublicTimeline.objects.filter(country=organization.country)
        probabilities = []
        average_probability = 0
        for potential_contact in potential_contacts_all:
            probabilities.append(potential_contact.probability)
        try:
            average_probability = mean(probabilities)
        except statistics.StatisticsError:
            average_probability = 0
        c = {
            'organization': organization,
            'positive_cases': positive_cases_all,
            'positive_cases_count': len(positive_cases_all),
            'potential_contacts': potential_contacts_all,
            'potential_contacts_count': len(potential_contacts_all),
            'public_timelines': public_timelines,
            'average_probability': average_probability,
            'active_tab': 'dashboard'
        }
        return render(request, 'backend/dashboard.html', c)
    elif request.method == 'POST':
        pass


@login_required
def show_positive_cases(request):
    if request.method == 'GET':
        msg = None
        if request.GET.get('msg') == '1':
            msg = 'Patient Created Successfully'
        elif request.GET.get('msg') == '2':
            msg = 'Patient Deleted Successfully'
        organization = Organization.objects.get(user=request.user)
        positive_cases = Patient.objects.filter(creator=request.user)
        c = {
            'organization': organization,
            'positive_cases': positive_cases,
            'msg': msg,
            'active_tab': 'positive_cases'
        }
        return render(request, 'backend/positive_cases.html', c)
    elif request.method == 'POST':
        if request.POST.get('new_case'):
            full_name = request.POST.get('full_name', None)
            covid_id = request.POST.get('covid_id', None)
            if len(covid_id.strip()) < 1:
                covid_id = generate_covid_id()
            else:
                covid_id = 'COVID-' + covid_id
            nationality = request.POST.get('nationality').capitalize()
            state = request.POST.get('state')
            creator = request.user
            patient = Patient(full_name=full_name, covid_id=covid_id, nationality=nationality, state=state,
                              creator=creator)
            patient.save()
            return HttpResponseRedirect('/positive-cases?msg=1')
        elif request.POST.get('delete_case'):
            patient = Patient.objects.get(pk=int(request.POST.get('delete_case')))
            patient.delete()
            return HttpResponseRedirect('/positive-cases?msg=2')


@login_required
def show_positive_case(request, positive_case_id):
    try:
        positive_case = Patient.objects.get(pk=int(positive_case_id))
        if positive_case.creator != request.user:
            return HttpResponseRedirect('/positive-cases/')
    except Patient.DoesNotExist:
        return HttpResponseRedirect('/positive-cases/')
    if request.method == 'GET':
        msg = None
        if request.GET.get('msg') == '1':
            msg = 'Timeline Created Successfully'
        elif request.GET.get('msg') == '2':
            msg = 'Timeline Deleted Successfully'
        organization = Organization.objects.get(user=request.user)
        potential_contacts = PotentialContact.objects.filter(patient=positive_case)
        patient_timelines = PatientTimeline.objects.filter(patient=positive_case)
        c = {
            'organization': organization,
            'positive_case': positive_case,
            'potential_contacts': potential_contacts,
            'patient_timelines': patient_timelines,
            'msg': msg,
            'active_tab': 'positive_cases'
        }
        return render(request, 'backend/positive_case_timeline.html', c)
    elif request.method == 'POST':
        if request.POST.get('new_timeline'):
            time_range = request.POST.get('time_range')
            timeline_date = request.POST.get('date')
            timeline_date = datetime.datetime.strptime(timeline_date, "%Y-%m-%d").date()  # e.g. 2010-05-24
            state = request.POST.get('state')
            country = request.POST.get('country')
            creator = request.user
            location, _ = Location.objects.get_or_create(name=request.POST.get('location'),
                                                         place_id=request.POST.get('place_id'))
            patient_timeline = PatientTimeline(patient=positive_case, location=location, time_range=time_range,
                                               date=timeline_date, country=country, state=state, creator=creator)
            patient_timeline.save()
            activities = request.POST.get('activities', '').split(',')  # received as a comma separated string
            print(activities)
            for activity in activities:
                try:
                    act = Activity.objects.get(name=activity.lower())
                except Activity.DoesNotExist:
                    act = Activity.objects.create(name=activity.lower(), creator=request.user)
                patient_timeline.activities.add(act)
                location.activities.add(act)
            other_activities = request.POST.get('other_activities', '').split(',')  # received as comma separated string
            print(other_activities)
            for activity in other_activities:
                try:
                    act = Activity.objects.get(name=activity.lower())
                except Activity.DoesNotExist:
                    act = Activity.objects.create(name=activity.lower(), creator=request.user)
                location.activities.add(act)
            return HttpResponseRedirect('/positive-cases/' + str(positive_case_id) + '/?msg=1')
        elif request.POST.get('delete_timeline'):
            patient_timeline = PatientTimeline.objects.get(pk=int(request.POST.get('delete_timeline')))
            patient_timeline.delete()
            return HttpResponseRedirect('/positive-cases/' + str(positive_case_id) + '/?msg=2')


@login_required
def show_timeline_potential_contacts(request, positive_case_id, timeline_id):
    organization = Organization.objects.get(user=request.user)
    try:
        positive_case = Patient.objects.get(pk=int(positive_case_id))
        if positive_case.creator != request.user:
            return HttpResponseRedirect('/positive-cases/')
    except PotentialContact.DoesNotExist:
        return HttpResponseRedirect('/positive-cases/')
    try:
        patient_timeline = PatientTimeline.objects.get(pk=int(timeline_id))
        if patient_timeline.patient != positive_case:
            return HttpResponseRedirect('/positive-cases/')
    except PotentialContact.DoesNotExist:
        return HttpResponseRedirect('/positive-cases/')
    if request.method == 'GET':
        potential_contacts = PotentialContact.objects.filter(patient_timeline=patient_timeline)
        c = {
            'organization': organization,
            'potential_contacts': potential_contacts,
            'active_tab': 'potential_cases'
        }
        return render(request, 'backend/timeline_potential_contacts.html', c)


@login_required
def show_potential_contacts(request):
    if request.method == 'GET':
        organization = Organization.objects.get(user=request.user)
        positive_cases = Patient.objects.filter(creator=request.user)
        potential_contacts_all = []
        for positive_case in positive_cases:
            potential_contacts = PotentialContact.objects.filter(patient=positive_case)
            potential_contacts_all.extend(potential_contacts)
        c = {
            'organization': organization,
            'potential_contacts': potential_contacts_all,
            'active_tab': 'potential_cases'
        }
        return render(request, 'backend/all_potential_contacts.html', c)


@login_required
def show_positive_potential_contact(request, potential_contact_id):
    organization = Organization.objects.get(user=request.user)
    try:
        potential_contact = PotentialContact.objects.get(pk=int(potential_contact_id))
        if potential_contact.public_timeline.country != organization.country:
            return HttpResponseRedirect('/potential-contacts/')
    except PotentialContact.DoesNotExist:
        return HttpResponseRedirect('/potential-contacts/')
    if request.method == 'GET':
        organization = Organization.objects.get(user=request.user)
        public_activities = ''
        for public_activity in potential_contact.public_timeline.activities.all():
            public_activities += public_activity.name + ', '
        patient_activities = ''
        for patient_activity in potential_contact.patient_timeline.activities.all():
            patient_activities += patient_activity.name + ', '
        address_data = {
            'data': 'Contact',
            'public': potential_contact.public_timeline.address,
            'patient': potential_contact.patient.covid_id
        }
        activity_data = {
            'data': 'Activities',
            'public': public_activities,
            'patient': patient_activities
        }
        location_data = {
            'data': 'Location',
            'public': potential_contact.public_timeline.location.name,
            'patient': potential_contact.patient_timeline.location.name,
        }
        time_range_data = {
            'data': 'Time Range',
            'public': potential_contact.public_timeline.time_range + 'Hrs',
            'patient': potential_contact.patient_timeline.time_range + 'Hrs',
        }
        date_data = {
            'data': 'Date',
            'public': potential_contact.public_timeline.date,
            'patient': potential_contact.patient_timeline.date,
        }
        state_data = {
            'data': 'State',
            'public': potential_contact.public_timeline.state,
            'patient': potential_contact.patient_timeline.state,
        }
        country_data = {
            'data': 'Country',
            'public': potential_contact.public_timeline.country,
            'patient': potential_contact.patient_timeline.country,
        }
        place_data = {
            'data': 'Place ID',
            'public': potential_contact.public_timeline.location.place_id,
            'patient': potential_contact.patient_timeline.location.place_id,
        }
        potential_contact_info = [address_data, location_data, place_data, time_range_data, date_data, activity_data,
                                  state_data, country_data]
        c = {
            'organization': organization,
            'potential_contact': potential_contact,
            'potential_contact_info': potential_contact_info,
            'active_tab': 'potential_cases'
        }
        return render(request, 'backend/positive_potential_contacts.html', c)


@login_required
def show_profile(request):
    organization = Organization.objects.get(user=request.user)
    if request.method == 'GET':
        msg = None
        if request.GET.get('msg') == '1':
            msg = 'Profile Updated Successfully'
        elif request.GET.get('msg') == '2':
            msg = 'Password Changed Successfully'
        errors = None
        if request.GET.get('errors') == '1':
            errors = 'Password length should be more than 5 characters.'
        elif request.GET.get('errors') == '2':
            errors = 'Incorrect old password.'
        c = {
            'organization': organization,
            'msg': msg,
            'errors': errors,
            'active_tab': 'profile'
        }
        return render(request, 'backend/org_profile.html', c)
    elif request.method == 'POST':
        if request.POST.get('basic'):
            email = request.POST.get('email', request.user.email)
            name = request.POST.get('name', organization.name)
            country = request.POST.get('country', organization.country)
            message = request.POST.get('message', organization.message)

            user = User.objects.get(pk=request.user.pk)
            user.email = email
            user.username = email
            user.save()

            organization.name = name
            organization.message = message
            organization.country = country
            organization.save()
            return HttpResponseRedirect('/profile?msg=1')
        elif request.POST.get('change_password'):
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if request.user.check_password(old_password):
                if len(new_password) < 6:
                    return HttpResponseRedirect('/profile?errors=1')
                user = User.objects.get(pk=request.user.pk)
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect('/profile?msg=1')
            else:
                return HttpResponseRedirect('/profile?errors=2')
