from django.urls import path

from app.views import show_home, show_dashboard, show_register, show_login, show_logout, show_positive_cases, \
    show_positive_case, show_potential_contacts, show_timeline_potential_contacts, \
    show_positive_potential_contact, show_profile

urlpatterns = [
    path('', show_home, name="frontend-home"),
    path('dashboard/', show_dashboard, name="backend-home"),
    path('new-cdc/', show_register, name="backend-register"),
    path('login-cdc/', show_login, name="backend-login"),
    path('logout-cdc/', show_logout, name="backend-logout"),

    path('positive-cases/', show_positive_cases, name="backend-positive-cases"),
    path('positive-cases/<int:positive_case_id>/', show_positive_case, name="backend-positive-case"),
    path('positive-cases/<int:positive_case_id>/timeline/<int:timeline_id>/', show_timeline_potential_contacts,
         name="backend-timeline-potential-contact"),
    path('potential-contacts/', show_potential_contacts, name="backend-potential-cases"),
    path('potential-contacts/<int:potential_contact_id>/', show_positive_potential_contact,
         name="backend-positive-potential-contact-info"),

    path('profile/', show_profile, name="backend-profile"),
]
