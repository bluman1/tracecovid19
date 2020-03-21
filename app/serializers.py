from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from app.models import Activity, Organization, Patient, PatientTimeline, PublicTimeline, PotentialContact, Location


class XUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(email=validated_data['username'], username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        Organization.objects.create(user=user, name=validated_data['name'], country=validated_data['country'])
        return user


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ('name',)


class LocationSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(required=False, many=True)
    creator = UserSerializer(required=False)

    class Meta:
        model = Location
        fields = ('name', 'place_id', 'activities', 'creator', 'created')


class OrganizationSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Organization
        fields = ('id', 'user', 'name', 'country', 'message', 'created')


class PatientSerializer(serializers.ModelSerializer):
    creator = UserSerializer(required=False)

    class Meta:
        model = Patient
        fields = ('id', 'full_name', 'covid_id', 'nationality', 'state', 'creator', 'created')


class PatientTimelineSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(required=False)
    location = LocationSerializer(required=False)
    activities = ActivitySerializer(required=False, many=True)
    creator = UserSerializer(required=False)

    class Meta:
        model = PatientTimeline
        fields = ('id', 'patient', 'location', 'time_range', 'date', 'state', 'country', 'activities', 'creator', 'created')


class PublicTimelineSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False)
    activities = ActivitySerializer(required=False, many=True)

    class Meta:
        model = PublicTimeline
        fields = ('id', 'location', 'time_range', 'date', 'state', 'country', 'address', 'email', 'phone_number', 'activities', 'created')


class PotentialContactSerializer(serializers.ModelSerializer):
    patient_timeline = PatientTimelineSerializer(required=False)
    public_timeline = PublicTimelineSerializer(required=False)

    class Meta:
        model = PotentialContact
        fields = ('id', 'patient_timeline', 'public_timeline', 'created')
