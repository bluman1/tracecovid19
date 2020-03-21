from django.contrib import admin

# Register your models here.
from app.models import Organization, Activity, Patient, PatientTimeline, PublicTimeline, PotentialContact

admin.site.register(Organization)
admin.site.register(Activity)
admin.site.register(Patient)
admin.site.register(PatientTimeline)
admin.site.register(PublicTimeline)
admin.site.register(PotentialContact)
