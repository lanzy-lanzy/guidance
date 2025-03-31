from django.urls import path
from core import views
from . import admin_views, counselor_views, student_views



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Keep this as a fallback
    path('schedule-session/', views.schedule_session, name='schedule_session'),

    # Student URLs
    path('student/dashboard/', student_views.student_dashboard, name='student_dashboard'),
    path('student/appointments/', student_views.student_appointment_list, name='student_appointment_list'),
    path('student/sessions/history/', student_views.student_session_history, name='student_session_history'),
    path('student/interviews/', student_views.student_interview_forms, name='student_interview_forms'),
    path('student/counselors/', student_views.student_counselor_list, name='student_counselor_list'),
    path('student/appointments/request/', student_views.request_appointment, name='request_appointment'),
    path('student/appointments/<int:appointment_id>/cancel/', student_views.cancel_appointment, name='cancel_appointment'),
    path('student/profile/', student_views.student_profile, name='student_profile'),
    path('student/counselor/<int:counselor_id>/profile/', views.counselor_profile, name='counselor_profile'),

    # Counselor URLs
    path('counselor/dashboard/', counselor_views.counselor_dashboard, name='counselor_dashboard'),
    path('counselor/appointments/', counselor_views.counselor_appointment_list, name='counselor_appointment_list'),
    path('counselor/students/', counselor_views.counselor_student_list, name='counselor_student_list'),
    path('counselor/sessions/history/', counselor_views.counselor_session_history, name='counselor_session_history'),
    path('counselor/sessions/<int:session_id>/', counselor_views.view_session, name='view_session'),
    path('counselor/sessions/<int:session_id>/print/', counselor_views.print_session, name='print_session'),
    path('counselor/reports/', counselor_views.counselor_reports_dashboard, name='counselor_reports_dashboard'),
    path('counselor/reports/generate/', counselor_views.generate_counselor_report, name='generate_counselor_report'),
    path('counselor/appointments/<int:appointment_id>/approve/', counselor_views.approve_appointment, name='approve_appointment'),
    path('counselor/appointments/<int:appointment_id>/decline/', counselor_views.decline_appointment, name='decline_appointment'),
    path('counselor/appointments/<int:appointment_id>/start-session/', counselor_views.start_session, name='start_session'),
    path('counselor/student/<int:student_id>/', counselor_views.student_profile, name='student_profile'),
    path('counselor/profile/', counselor_views.counselor_profile, name='counselor_profile'),
    path('counselor/interview/<int:interview_id>/print/', views.print_interview, name='print_interview'),
    path('counselor/appointments/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),

    # Interview URLs
    path('counselor/student/<int:student_id>/interview/', views.simple_interview_form, name='simple_interview_form'),
    path('counselor/interview/<int:interview_id>/view/', views.view_interview, name='view_interview'),
    path('counselor/interview/<int:interview_id>/view-form/', admin_views.view_interview_form, name='view_interview_form'),
    path('counselor/interview/<int:session_id>/completed/', views.view_completed_interview, name='view_completed_interview'),

    # Psychological Report URLs
    path('counselor/psychological-reports/', counselor_views.psychological_report_list, name='psychological_report_list'),
    path('counselor/psychological-reports/create/', counselor_views.create_psychological_report, name='create_psychological_report'),
    path('counselor/psychological-reports/<int:report_id>/edit/', counselor_views.edit_psychological_report, name='edit_psychological_report'),
    path('counselor/psychological-reports/<int:report_id>/print/', counselor_views.print_psychological_report, name='print_psychological_report'),

    # Counseling Referral URLs
    path('counselor/counseling-referrals/', counselor_views.counseling_referral_list, name='counseling_referral_list'),
    path('counselor/counseling-referrals/create/', counselor_views.create_counseling_referral, name='create_counseling_referral'),
    path('counselor/counseling-referrals/<int:referral_id>/edit/', counselor_views.edit_counseling_referral, name='edit_counseling_referral'),
    path('counselor/counseling-referrals/<int:referral_id>/print/', counselor_views.print_counseling_referral, name='print_counseling_referral'),

    # Counseling Session Certificate URLs
    path('counselor/session-certificates/', counselor_views.session_certificate_list, name='session_certificate_list'),
    path('counselor/session-certificates/create/', counselor_views.create_session_certificate, name='create_session_certificate'),
    path('counselor/session-certificates/<int:certificate_id>/edit/', counselor_views.edit_session_certificate, name='edit_session_certificate'),
    path('counselor/session-certificates/<int:certificate_id>/print/', counselor_views.print_session_certificate, name='print_session_certificate'),

    # Admin URLs
    path('admin-panel/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', admin_views.admin_users, name='admin_users'),
    path('admin-panel/users/add/', admin_views.admin_add_user, name='admin_add_user'),
    path('admin-panel/users/<int:user_id>/edit/', admin_views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/users/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/users/<int:user_id>/approve/', admin_views.admin_approve_user, name='admin_approve_user'),
    path('admin-panel/students/', admin_views.admin_students, name='admin_students'),
    path('admin-panel/counselors/', admin_views.admin_counselors, name='admin_counselors'),
    path('admin-panel/appointments/', admin_views.admin_appointments, name='admin_appointments'),
    path('admin-panel/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin-panel/reports/sessions/', admin_views.generate_sessions_report, name='generate_sessions_report'),
    path('admin-panel/reports/students/', admin_views.generate_student_report, name='generate_student_report'),
    # path('admin-panel/reports/counselors/', admin_views.generate_counselor_report, name='generate_counselor_report'),
    path('admin-panel/reports/appointments/', admin_views.generate_appointment_report, name='generate_appointment_report'),
    path('admin-panel/reports/custom/', admin_views.generate_custom_report, name='generate_custom_report'),
    path('admin-panel/settings/', admin_views.admin_settings, name='admin_settings'),

    # Other URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('reschedule-appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
]




