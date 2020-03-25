from django.urls import path
from app.auth import OrganizationAuthToken
from app.api_views import create_organization, update_organization_profile, update_organization_password, patients_view, \
    patient_view, patient_timelines_view, public_timelines_view, public_timeline_view, potential_contacts_view, \
    activities_view, trace_contact, logout, patient_timeline_view, country_message_view

urlpatterns = [
    path('logout/', logout, name="api-logout"),

    path("organizations/auth/", OrganizationAuthToken.as_view(), name="api-one-auth"),
    path("organizations/signup/", create_organization, name="api-create-organization"),
    path("organizations/profile/<int:organization_id>/", update_organization_profile, name="api-organization-profile"),
    path("organizations/password/", update_organization_password, name="api-organization-password"),

    path("country-message/", country_message_view, name="api-country-message"),

    path("activities/", activities_view, name="api-activities"),

    path("trace/<int:public_timeline_id>/", trace_contact, name="api-trace"),

    path("patients/", patients_view, name="api-patients"),
    path("patients/<int:patient_id>/", patient_view, name="api-patient-detail"),
    path("patients/<int:patient_id>/timelines/", patient_timelines_view, name="api-patient-timelines"),
    path("patients/<int:patient_id>/timelines/<int:timeline_id>/", patient_timeline_view,
         name="api-patient-timeline-detail"),
    path("patients/<int:patient_id>/potentials/", potential_contacts_view, name="api-potentials"),

    path("public/timelines/", public_timelines_view, name="api-public-timelines"),
    path("public/timelines/<int:timeline_id>/", public_timeline_view, name="api-public-timeline-detail"),
]
