import datetime
import statistics
from statistics import mean

from django.contrib.auth.models import User

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from app.helpers import error_msg, success_msg, contact_chance, validate_email, generate_covid_id
from app.models import Organization, Patient, PatientTimeline, Activity, PublicTimeline, PotentialContact, Location
from app.permissions import OrganizationPermission
from app.serializers import OrganizationSerializer, PatientSerializer, PatientTimelineSerializer, \
    PublicTimelineSerializer, PotentialContactSerializer, ActivitySerializer


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def logout(request):
    if request.user.is_anonymous:
        return Response(status=status.HTTP_200_OK)
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes(())
@authentication_classes([])
def create_organization(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        country = request.data.get('country')
        name = request.data.get('name')
        if not validate_email(email):
            return Response(error_msg("Invalid email address."), status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response(error_msg("Invalid password. Password should be greater than 5 characters."),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            User.objects.get(username=email)
            return Response(error_msg("User already exists."), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = email
        user.last_name = email
        user.save()
        organization = Organization(user=user, name=name, country=country)
        organization.save()

        serialized_org = OrganizationSerializer(organization)
        return Response(success_msg("Created organization successfully", serialized_org.data), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((OrganizationPermission,))
def update_organization_profile(request, organization_id):
    try:
        organization = Organization.objects.get(pk=int(organization_id))
    except Organization.DoesNotExist:
        return Response(error_msg("Organization not found"), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        first_name = request.data.get('first_name', organization.user.first_name)
        last_name = request.data.get('last_name', organization.user.last_name)
        email = request.data.get('email', organization.user.email)
        name = request.data.get('name', organization.name)
        country = request.data.get('country', organization.country)
        message = request.data.get('message', organization.message)
        organization.name = name
        organization.country = country
        organization.message = message
        organization.user.first_name = first_name
        organization.user.last_name = last_name
        organization.user.email = email
        organization.user.save()
        organization.save()
        serialized = OrganizationSerializer(organization)
        return Response(success_msg("Updated organization successfully", serialized.data),
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((OrganizationPermission,))
def update_organization_password(request):
    if request.method == 'POST':
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if request.user.check_password(old_password):
            if len(new_password) < 6:
                return Response(error_msg("Invalid password. Password should be greater than 5 characters."),
                                status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(pk=request.user.pk)
            user.set_password(new_password)
            user.save()
            serialized = OrganizationSerializer(request.user.organization)
            return Response(success_msg("Password changed successfully", serialized.data), status=status.HTTP_200_OK)
        else:
            response = {
                "status": False
            }
            return Response(success_msg("Password change failed. Old password is incorrect.", response), status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((OrganizationPermission,))
def patients_view(request):
    if request.method == 'GET':
        patients = Patient.objects.filter(creator=request.user)
        serialized = PatientSerializer(patients, many=True)
        return Response(success_msg("Retrieved patients successfully", serialized.data),
                        status=status.HTTP_200_OK)
    elif request.method == 'POST':
        full_name = request.data.get('full_name', None)
        covid_id = request.data.get('covid_id', generate_covid_id())
        nationality = request.data.get('nationality')
        state = request.data.get('state')
        creator = request.user
        patient = Patient(full_name=full_name, covid_id=covid_id, nationality=nationality, state=state, creator=creator)
        patient.save()
        serialized = PatientSerializer(patient)
        return Response(success_msg("Patient created successfully", serialized.data), status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes((OrganizationPermission,))
def patient_view(request, patient_id):
    try:
        patient = Patient.objects.get(pk=int(patient_id))
    except Patient.DoesNotExist:
        return Response(error_msg("Patient not found"), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serialized = PatientSerializer(patient)
        return Response(success_msg("Patient retrieved successfully", serialized.data), status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        patient.delete()
        return Response(success_msg("Patient deleted successfully", None), status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((OrganizationPermission,))
def patient_timelines_view(request, patient_id):
    try:
        patient = Patient.objects.get(pk=int(patient_id))
    except Patient.DoesNotExist:
        return Response(error_msg("Patient not found"), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        patient_timelines = PatientTimeline.objects.filter(patient=patient)
        serialized = PatientTimelineSerializer(patient_timelines, many=True)
        return Response(success_msg("Retrieved patient timelines successfully", serialized.data),
                        status=status.HTTP_200_OK)
    elif request.method == 'POST':
        time_range = request.data.get('time_range')
        timeline_date = request.data.get('date')
        timeline_date = datetime.datetime.strptime(timeline_date, "%Y-%m-%d").date()  # e.g. 2010-05-24
        state = request.data.get('state')
        country = request.data.get('country')
        creator = request.user
        location, _ = Location.objects.get_or_create(name=request.data.get('location'),
                                                               place_id=request.data.get('place_id'))
        patient_timeline = PatientTimeline(patient=patient, location=location, time_range=time_range,
                                           date=timeline_date, country=country, state=state, creator=creator)
        patient_timeline.save()
        activities = request.data.get('activities', '').split(',')  # received as a comma separated string
        for activity in activities:
            try:
                act = Activity.objects.get(name=activity.lower())
            except Activity.DoesNotExist:
                act = Activity.objects.create(name=activity.lower(), creator=request.user)
            patient_timeline.activities.add(act)
            location.activities.add(act)
        other_activities = request.data.get('other_activities', '').split(',')  # received as a comma separated string
        for activity in other_activities:
            try:
                act = Activity.objects.get(name=activity.lower())
            except Activity.DoesNotExist:
                act = Activity.objects.create(name=activity.lower(), creator=request.user)
            location.activities.add(act)
        serialized = PatientTimelineSerializer(patient_timeline)  # TODO: perform a trace using the just created patient timeline
        return Response(success_msg("Patient timeline created successfully", serialized.data), status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes((OrganizationPermission,))
def patient_timeline_view(request, patient_id, timeline_id):
    if request.method == 'GET':
        try:
            patient_timeline = PatientTimeline.objects.get(pk=int(timeline_id))
            serialized = PatientTimelineSerializer(patient_timeline)
            return Response(success_msg("Patient timeline retrieved successfully", serialized.data), status=status.HTTP_200_OK)
        except PatientTimeline.DoesNotExist:
            return Response(error_msg("Patient timeline not found"), status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        try:
            patient_timeline = PatientTimeline.objects.get(pk=int(timeline_id))
            patient_timeline.delete()
            return Response(success_msg("Patient timeline deleted successfully", None), status=status.HTTP_200_OK)
        except PatientTimeline.DoesNotExist:
            return Response(error_msg("Cannot delete patient timeline. Patient timeline not found"),
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes(())
@authentication_classes([])
def public_timelines_view(request):
    if request.method == 'GET':
        if request.GET.get('country'):
            public_timelines = PublicTimeline.objects.filter(country=request.GET.get('country'))
        else:
            public_timelines = PublicTimeline.objects.all()
        serialized = PublicTimelineSerializer(public_timelines, many=True)
        return Response(success_msg("Retrieved public timelines successfully", serialized.data),
                        status=status.HTTP_200_OK)
    elif request.method == 'POST':
        time_range = request.data.get('time_range')
        timeline_date = request.data.get('date')
        timeline_date = datetime.datetime.strptime(timeline_date, "%Y-%m-%d").date()  # e.g. 2010-05-24
        state = request.data.get('state')
        country = request.data.get('country')
        phone_number = request.data.get('phone_number', None)
        address = request.data.get('address', None)
        email = request.data.get('email', None)
        location, _ = Location.objects.get_or_create(name=request.data.get('location'),
                                                     place_id=request.data.get('place_id'))
        public_timeline = PublicTimeline(location=location, time_range=time_range, date=timeline_date, state=state,
                                          country=country, email=email, phone_number=phone_number, address=address)
        public_timeline.save()
        activities = request.data.get('activities')  # received as a comma separated string
        if activities:
            activities = activities.split(',')
            for activity in activities:
                try:
                    act = Activity.objects.get(name=activity.lower())
                except Activity.DoesNotExist:
                    act = Activity.objects.create(name=activity.lower(), creator=request.user)
                public_timeline.activities.add(act)
                location.activities.add(act)
        serialized = PublicTimelineSerializer(public_timeline)
        return Response(success_msg("Public timeline created successfully", serialized.data), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes(())
@authentication_classes([])
def public_timeline_view(request, timeline_id):
    if request.method == 'GET':
        try:
            public_timeline = PublicTimeline.objects.get(pk=int(timeline_id))
            serialized = PublicTimelineSerializer(public_timeline)
            return Response(success_msg("Public timeline retrieved successfully", serialized.data), status=status.HTTP_200_OK)
        except PublicTimeline.DoesNotExist:
            return Response(error_msg("Public timeline not found"), status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        try:
            public_timeline = PublicTimeline.objects.get(pk=int(timeline_id))
            public_timeline.delete()
            return Response(success_msg("Public timeline deleted successfully", None), status=status.HTTP_200_OK)
        except PublicTimeline.DoesNotExist:
            return Response(error_msg("Cannot delete public timeline. public not found"),
                            status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'PUT':
        try:
            public_timeline = PublicTimeline.objects.get(pk=int(timeline_id))
            public_timeline.address = request.data.get('address', public_timeline.address)
            public_timeline.phone_number = request.data.get('phone_number', public_timeline.phone_number)
            public_timeline.email = request.data.get('email', public_timeline.email)
            public_timeline.save()
            serialized = PublicTimelineSerializer(public_timeline)
            return Response(success_msg("Public timeline updated successfully", serialized.data), status=status.HTTP_200_OK)
        except PublicTimeline.DoesNotExist:
            return Response(error_msg("Cannot update public timeline. public not found"),
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((OrganizationPermission,))
def potential_contacts_view(request, patient_id):
    try:
        patient = Patient.objects.get(pk=int(patient_id))
    except Patient.DoesNotExist:
        return Response(error_msg("Patient not found"), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        potential_contacts = PotentialContact.objects.filter(patient=patient)
        serialized = PotentialContactSerializer(potential_contacts, many=True)
        return Response(success_msg("Retrieved potential contacts successfully", serialized.data),
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes(())
@authentication_classes([])
def activities_view(request):
    if request.method == 'GET':
        if len(request.GET) < 1:
            activities = Activity.objects.all().order_by('name')
            serialized = ActivitySerializer(activities, many=True)
            return Response(success_msg("Retrieved activities successfully", serialized.data),
                            status=status.HTTP_200_OK)
        activities = set()
        timelines = PatientTimeline.objects
        if request.GET.get('country'):
            timelines = timelines.filter(country=request.GET.get('country'))
        if request.GET.get('state'):
            timelines = timelines.filter(state=request.GET.get('state'))
        if request.GET.get('location'):
            try:
                location_by_name = Location.objects.get(name=request.GET.get('location'))
                for activity in location_by_name.activities.all():
                    activities.add(activity)
            except Location.DoesNotExist:
                pass
        if request.GET.get('place_id'):
            try:
                location_by_place_id = Location.objects.get(place_id=request.GET.get('place_id'))
                for activity in location_by_place_id.activities.all():
                    activities.add(activity)
            except Location.DoesNotExist:
                pass
        for timeline in timelines:
            timeline_activities = timeline.location.activities.all()
            for timeline_activity in timeline_activities:
                activities.add(timeline_activity)
        serialized = ActivitySerializer(activities, many=True)
        return Response(success_msg("Retrieved activities successfully", serialized.data),
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes(())
@authentication_classes([])
def trace_contact(request, public_timeline_id):
    try:
        public_timeline = PublicTimeline.objects.get(pk=int(public_timeline_id))
    except PublicTimeline.DoesNotExist:
        return Response(error_msg("Public timeline not found"), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        probabilities = []
        matched_activities = set()
        possible_contacts = 0
        patient_timelines = PatientTimeline.objects.filter(country=public_timeline.country)  # 16.6%
        if patient_timelines.exists():
            for patient_timeline in patient_timelines:
                matches = set()
                if patient_timeline.country == public_timeline.country:
                    matches.add('country')
                if patient_timeline.state == public_timeline.state:
                    matches.add('state')
                if patient_timeline.location == public_timeline.location:
                    matches.add('location')
                if patient_timeline.date == public_timeline.date:
                    matches.add('date')
                if patient_timeline.time_range == public_timeline.time_range:
                    matches.add('time_range')
                for patient_activity in patient_timeline.activities.all():
                    if patient_activity in public_timeline.activities.all():
                        matches.add('activity')
                        matched_activities.add(patient_activity.name)
                probability = contact_chance(matches)
                probabilities.append(probability)
                if probability >= 50:
                    possible_contacts += 1
                    potential_contact = PotentialContact(public_timeline=public_timeline, probability=probability,
                                                         patient_timeline=patient_timeline,
                                                         patient=patient_timeline.patient)
                    potential_contact.save()
        try:
            chance = mean(probabilities)
        except statistics.StatisticsError:
            chance = 0
        response = {
            'probability': chance,
            'possible_contacts': possible_contacts,
            'matched_activities': matched_activities
        }
        return Response(success_msg("Trace complete.", response), status=status.HTTP_200_OK)
