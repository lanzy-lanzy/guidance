from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import Appointment, Student, GuidanceSession, Interview, Counselor, FollowUp, PsychologicalReport, CounselingReferral, CounselingSessionCertificate, Report, User
from .forms import PsychologicalReportForm, CounselingReferralForm, CounselingSessionCertificateForm
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

def is_counselor(user):
    return user.is_authenticated and user.role == 'counselor'

@login_required
@user_passes_test(is_counselor)
def counselor_dashboard(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    today = timezone.now().date()

    pending_appointments = Appointment.objects.filter(counselor=counselor, status='pending').count()
    total_students = Student.objects.count()
    completed_sessions = GuidanceSession.objects.filter(counselor=counselor, status='completed').count()

    # Get upcoming follow-ups
    upcoming_followups = Interview.objects.filter(
        counselor=counselor,
        follow_up_needed=True,
        follow_up_date__gte=today
    ).order_by('follow_up_date')[:5]

    # Count follow-ups due today
    followups_due_today = Interview.objects.filter(
        counselor=counselor,
        follow_up_needed=True,
        follow_up_date=today
    ).count()

    context = {
        'today': today,
        'pending_appointments': pending_appointments,
        'total_students': total_students,
        'completed_sessions': completed_sessions,
        'followups_due_today': followups_due_today,
        'upcoming_followups': upcoming_followups,
        'upcoming_appointments': Appointment.objects.filter(
            counselor=counselor,
            date__gte=today
        ).order_by('date', 'time')[:5],
        'recent_interviews': Interview.objects.filter(counselor=counselor).order_by('-date')[:5]
    }
    return render(request, 'counselor/dashboard.html', context)

@login_required
@user_passes_test(is_counselor)
def counselor_appointment_list(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    appointments = Appointment.objects.all().order_by('-date', '-time')

    # Get current date for filtering upcoming appointments
    current_date = timezone.now().date()

    # Filter upcoming appointments
    if request.GET.get('status') == 'approved':
        appointments = appointments.filter(
            status='approved',
            date__gte=current_date
        ).order_by('date', 'time')

    context = {
        'appointments': appointments,
        'today_appointments': appointments.filter(date=current_date).count(),
        'pending_appointments': appointments.filter(status='pending').count(),
        'upcoming_appointments': appointments.filter(
            status='approved',
            date__gte=current_date
        ).count(),
    }

    return render(request, 'counselor/appointments.html', context)

@login_required
@user_passes_test(is_counselor)
def counselor_student_list(request):
    students = Student.objects.all().order_by('user__last_name', 'user__first_name')
    return render(request, 'counselor/students.html', {'students': students})

@login_required
@user_passes_test(is_counselor)
def counselor_session_history(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    sessions = GuidanceSession.objects.filter(
        counselor=counselor,
        status='completed'
    ).select_related('appointment', 'student__user').order_by('-date')
    return render(request, 'counselor/session_history.html', {
        'sessions': sessions
    })

@login_required
@user_passes_test(is_counselor)
def counselor_reports_dashboard(request):
    counselor = get_object_or_404(Counselor, user=request.user)

    # Handle report deletion
    delete_report_id = request.GET.get('delete_report')
    if delete_report_id:
        try:
            report = Report.objects.get(id=delete_report_id, generated_by=request.user)
            report_name = report.name
            report.delete()
            messages.success(request, f'Report "{report_name}" has been deleted successfully.')
        except Report.DoesNotExist:
            messages.error(request, 'Report not found or you do not have permission to delete it.')
        except Exception as e:
            messages.error(request, f'Error deleting report: {str(e)}')
        return redirect('counselor_reports_dashboard')

    # Get basic stats
    context = {
        'total_sessions': GuidanceSession.objects.filter(counselor=counselor).count(),
        'total_students': Student.objects.count(),
        'recent_sessions': GuidanceSession.objects.filter(counselor=counselor).order_by('-date')[:5]
    }

    # Get saved reports for this counselor
    try:
        reports = Report.objects.filter(generated_by=request.user).order_by('-generated_at')[:10]
        context['reports'] = reports
    except:
        # If Report model doesn't exist or there's an error, just continue without reports
        pass

    return render(request, 'counselor/reports.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Appointment, Counselor
from .utils import send_appointment_sms
from django.utils import timezone

@login_required
@user_passes_test(is_counselor)
def approve_appointment(request, appointment_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, counselor=counselor)
    appointment.status = 'approved'
    appointment.save()

    # Get student's phone number
    student_phone = appointment.student.contact_number

    # Format the message
    message = f"Your appointment with {counselor.user.get_full_name()} on {appointment.date} at {appointment.time} has been approved."

    # Send SMS notification if phone number is available
    if student_phone:
        # Log the original phone number
        logger.info(f"Original phone number: {student_phone}")

        # Format the phone number to international format if needed
        if not student_phone.startswith('+'):
            # Assuming Philippines phone number format
            student_phone = '+63' + student_phone[1:] if student_phone.startswith('0') else '+63' + student_phone
            logger.info(f"Reformatted phone number to {student_phone}")

        # Print debug information before sending
        print(f"DEBUG: About to send SMS to {student_phone} for appointment approval")

        # Send the SMS
        sms_sent = send_appointment_sms(student_phone, message)

        if sms_sent:
            success_msg = f'Appointment approved successfully. SMS notification sent to {student_phone}.'
            logger.info(success_msg)
            messages.success(request, success_msg)
        else:
            # Check Twilio credentials
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
                error_msg = "Twilio credentials are missing or invalid."
                logger.error(error_msg)
                messages.error(request, f'Appointment approved successfully, but SMS notification failed to send. {error_msg}')
            else:
                error_msg = f'Appointment approved successfully, but SMS notification failed to send to {student_phone}.'
                logger.error(error_msg)
                print(f"ERROR: {error_msg} See console output above for detailed error message.")
                messages.error(request, f'{error_msg} See server logs for details.')
    else:
        messages.success(request, 'Appointment approved successfully. No SMS sent (student phone number not available).')

    return redirect('counselor_appointment_list')

@login_required
@user_passes_test(is_counselor)
def decline_appointment(request, appointment_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, counselor=counselor)
    appointment.status = 'declined'
    appointment.save()

    # Get student's phone number
    student_phone = appointment.student.contact_number

    # Format the message
    message = f"Your appointment with {counselor.user.get_full_name()} on {appointment.date} at {appointment.time} has been declined."

    # Send SMS notification if phone number is available
    if student_phone:
        # Log the original phone number
        logger.info(f"Original phone number: {student_phone}")

        # Format the phone number to international format if needed
        if not student_phone.startswith('+'):
            # Assuming Philippines phone number format
            student_phone = '+63' + student_phone[1:] if student_phone.startswith('0') else '+63' + student_phone
            logger.info(f"Reformatted phone number to {student_phone}")

        # Print debug information before sending
        print(f"DEBUG: About to send SMS to {student_phone} for appointment decline")

        # Send the SMS
        sms_sent = send_appointment_sms(student_phone, message)

        if sms_sent:
            success_msg = f'Appointment declined successfully. SMS notification sent to {student_phone}.'
            logger.info(success_msg)
            messages.success(request, success_msg)
        else:
            # Check Twilio credentials
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
                error_msg = "Twilio credentials are missing or invalid."
                logger.error(error_msg)
                messages.error(request, f'Appointment declined successfully, but SMS notification failed to send. {error_msg}')
            else:
                error_msg = f'Appointment declined successfully, but SMS notification failed to send to {student_phone}.'
                logger.error(error_msg)
                print(f"ERROR: {error_msg} See console output above for detailed error message.")
                messages.error(request, f'{error_msg} See server logs for details.')
    else:
        messages.success(request, 'Appointment declined successfully. No SMS sent (student phone number not available).')

    return redirect('counselor_appointment_list')

@login_required
@user_passes_test(is_counselor)
def start_session(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if session exists and has completed interview/printing
    existing_session = GuidanceSession.objects.filter(
        appointment=appointment,
        status='completed',
        interview__isnull=False
    ).first()

    if existing_session:
        messages.warning(request, 'A completed session for this appointment already exists.')
        return redirect('counselor_appointment_list')

    # Delete any incomplete sessions
    GuidanceSession.objects.filter(
        appointment=appointment,
        status='ongoing'
    ).delete()

    # Create new session and update appointment status
    session = GuidanceSession.objects.create(
        appointment=appointment,
        counselor=appointment.counselor,
        student=appointment.student,
        date=appointment.date,
        status='ongoing'
    )

    # Update appointment status to ongoing
    appointment.status = 'ongoing'
    appointment.save()

    messages.success(request, 'Guidance session started successfully.')
    return redirect('simple_interview_form', student_id=appointment.student.id)
@login_required
@user_passes_test(is_counselor)
def interview_form(request, interview_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    interview = get_object_or_404(Interview, id=interview_id, counselor=counselor)

    if request.method == 'POST':
        # Update interview with form data
        interview.date = timezone.now().date()
        interview.address = request.POST.get('address')
        interview.contact_number = request.POST.get('contact_number')
        interview.birth_date = request.POST.get('birth_date')
        interview.birth_place = request.POST.get('birth_place')
        interview.age = request.POST.get('age')
        interview.civil_status = request.POST.get('civil_status')
        interview.religion = request.POST.get('religion')
        interview.reason_for_interview = request.POST.get('reason_for_interview')
        interview.presenting_problem = request.POST.get('presenting_problem')
        interview.background_of_problem = request.POST.get('background_of_problem')
        interview.counselor_notes = request.POST.get('counselor_notes')
        interview.recommendations = request.POST.get('recommendations')
        interview.follow_up_needed = request.POST.get('follow_up_needed') == 'on'

        # Process follow-up date if follow-up is needed
        if interview.follow_up_needed and request.POST.get('follow_up_date'):
            interview.follow_up_date = request.POST.get('follow_up_date')
        else:
            interview.follow_up_date = None

        interview.save()

        return redirect('print_interview', interview_id=interview.id)

    return render(request, 'counselor/simple_interview_form.html', {
        'interview': interview,
        'student': interview.student,
        'appointment': interview.session.appointment
    })
@login_required
@user_passes_test(is_counselor)
def print_interview(request, interview_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    interview = get_object_or_404(Interview, id=interview_id, counselor=counselor)

    # Mark both session and appointment as completed
    if interview.session:
        # Update session status
        interview.session.status = 'completed'
        interview.session.save()

        # Update appointment status
        if interview.session.appointment:
            appointment = interview.session.appointment
            appointment.status = 'completed'
            appointment.save()

    return render(request, 'counselor/print_interview.html', {
        'interview': interview
    })

@login_required
@user_passes_test(is_counselor)
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    # Get related data
    appointments = Appointment.objects.filter(student=student).order_by('-date')
    sessions = GuidanceSession.objects.filter(student=student).order_by('-date')
    interviews = Interview.objects.filter(student=student).order_by('-date')

    context = {
        'student': student,
        'appointments': appointments,
        'sessions': sessions,
        'interviews': interviews,
    }
    return render(request, 'counselor/student_profile.html', context)

@login_required
@user_passes_test(is_counselor)
def create_interview(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    counselor = get_object_or_404(Counselor, user=request.user)

    if request.method == 'POST':
        # Handle form submission
        interview_type = request.POST.get('interview_type')
        notes = request.POST.get('notes')

        interview = Interview.objects.create(
            student=student,
            counselor=counselor,
            interview_type=interview_type,
            notes=notes,
            date=timezone.now()
        )

        messages.success(request, 'Interview form created successfully.')
        return redirect('student_profile', student_id=student.id)

    return render(request, 'counselor/create_interview.html', {
        'student': student
    })

@login_required
@user_passes_test(is_counselor)
def print_session(request, session_id):
    # Get the session with all related data using select_related
    session = get_object_or_404(
        GuidanceSession.objects.select_related(
            'student',
            'student__user',
            'counselor',
            'counselor__user'
        ),
        id=session_id
    )

    # Verify counselor has access to this session
    if session.counselor.user != request.user:
        raise PermissionDenied

    context = {
        'session': session,
        'student': session.student,
        'counselor': session.counselor,
        'now': timezone.now(),
        'print_mode': True
    }

    return render(request, 'counselor/print_session.html', context)

@login_required
@user_passes_test(is_counselor)
def print_student_info(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'counselor/print_student_info.html', {
        'student': student,
        'now': timezone.now()
    })

@login_required
@user_passes_test(is_counselor)
def psychological_report_list(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    reports = PsychologicalReport.objects.filter(counselor=counselor).order_by('-date')

    context = {
        'reports': reports,
    }
    return render(request, 'counselor/psychological_report_list.html', context)

@login_required
@user_passes_test(is_counselor)
def create_psychological_report(request):
    counselor = get_object_or_404(Counselor, user=request.user)

    if request.method == 'POST':
        form = PsychologicalReportForm(request.POST, counselor=counselor)
        if form.is_valid():
            report = form.save(commit=False)
            report.counselor = counselor
            report.save()
            messages.success(request, 'Psychological report created successfully.')
            return redirect('print_psychological_report', report_id=report.id)
    else:
        form = PsychologicalReportForm(counselor=counselor)

    context = {
        'form': form,
        'title': 'Create Psychological Report',
    }
    return render(request, 'counselor/psychological_report_form.html', context)

@login_required
@user_passes_test(is_counselor)
def edit_psychological_report(request, report_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    report = get_object_or_404(PsychologicalReport, id=report_id, counselor=counselor)

    if request.method == 'POST':
        form = PsychologicalReportForm(request.POST, instance=report, counselor=counselor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Psychological report updated successfully.')
            return redirect('print_psychological_report', report_id=report.id)
    else:
        form = PsychologicalReportForm(instance=report, counselor=counselor)

    context = {
        'form': form,
        'report': report,
        'title': 'Edit Psychological Report',
    }
    return render(request, 'counselor/psychological_report_form.html', context)

@login_required
@user_passes_test(is_counselor)
def print_psychological_report(request, report_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    report = get_object_or_404(PsychologicalReport, id=report_id, counselor=counselor)

    context = {
        'report': report,
        'now': timezone.now(),
        'print_mode': True
    }
    return render(request, 'counselor/print_psychological_report.html', context)

@login_required
@user_passes_test(is_counselor)
def counseling_referral_list(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    referrals = CounselingReferral.objects.all().order_by('-date')

    context = {
        'referrals': referrals,
    }
    return render(request, 'counselor/counseling_referral_list.html', context)

@login_required
@user_passes_test(is_counselor)
def create_counseling_referral(request):
    counselor = get_object_or_404(Counselor, user=request.user)

    if request.method == 'POST':
        form = CounselingReferralForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)

            # Handle the different referral types
            referral_type = form.cleaned_data.get('referral_type')

            # Save the referral first to get an ID
            referral.save()

            # For multiple students, we need to save the many-to-many relationship after saving the referral
            if referral_type == 'multiple':
                # The form.save_m2m() will handle the many-to-many relationship for students
                form.save_m2m()

                # Log the number of students selected for debugging
                student_count = referral.students.count()
                logger.info(f"Multiple students referral created with {student_count} students")

            messages.success(request, 'Counseling referral created successfully.')
            return redirect('print_counseling_referral', referral_id=referral.id)
    else:
        form = CounselingReferralForm()

    context = {
        'form': form,
        'title': 'Create Counseling Referral',
    }
    return render(request, 'counselor/counseling_referral_form.html', context)

@login_required
@user_passes_test(is_counselor)
def edit_counseling_referral(request, referral_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    referral = get_object_or_404(CounselingReferral, id=referral_id)

    if request.method == 'POST':
        form = CounselingReferralForm(request.POST, instance=referral)
        if form.is_valid():
            # Save the form but don't commit yet
            referral = form.save(commit=False)

            # Handle the different referral types
            referral_type = form.cleaned_data.get('referral_type')

            # Save the referral
            referral.save()

            # For multiple students, we need to save the many-to-many relationship after saving the referral
            if referral_type == 'multiple':
                # The form.save_m2m() will handle the many-to-many relationship for students
                form.save_m2m()

                # Log the number of students selected for debugging
                student_count = referral.students.count()
                logger.info(f"Multiple students referral updated with {student_count} students")

            messages.success(request, 'Counseling referral updated successfully.')
            return redirect('print_counseling_referral', referral_id=referral.id)
    else:
        form = CounselingReferralForm(instance=referral)

    context = {
        'form': form,
        'referral': referral,
        'title': 'Edit Counseling Referral',
    }
    return render(request, 'counselor/counseling_referral_form.html', context)

@login_required
@user_passes_test(is_counselor)
def print_counseling_referral(request, referral_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    referral = get_object_or_404(CounselingReferral, id=referral_id)

    context = {
        'referral': referral,
        'now': timezone.now(),
        'print_mode': True
    }
    return render(request, 'counselor/print_counseling_referral.html', context)

@login_required
@user_passes_test(is_counselor)
def session_certificate_list(request):
    counselor = get_object_or_404(Counselor, user=request.user)
    certificates = CounselingSessionCertificate.objects.filter(counselor=counselor).order_by('-date')

    context = {
        'certificates': certificates,
    }
    return render(request, 'counselor/session_certificate_list.html', context)

@login_required
@user_passes_test(is_counselor)
def create_session_certificate(request):
    counselor = get_object_or_404(Counselor, user=request.user)

    if request.method == 'POST':
        form = CounselingSessionCertificateForm(request.POST, counselor=counselor)
        if form.is_valid():
            certificate = form.save()
            messages.success(request, 'Counseling session certificate created successfully.')
            return redirect('print_session_certificate', certificate_id=certificate.id)
    else:
        form = CounselingSessionCertificateForm(counselor=counselor)

    context = {
        'form': form,
        'title': 'Create Counseling Session Certificate',
    }
    return render(request, 'counselor/session_certificate_form.html', context)

@login_required
@user_passes_test(is_counselor)
def edit_session_certificate(request, certificate_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    certificate = get_object_or_404(CounselingSessionCertificate, id=certificate_id, counselor=counselor)

    if request.method == 'POST':
        form = CounselingSessionCertificateForm(request.POST, instance=certificate, counselor=counselor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Counseling session certificate updated successfully.')
            return redirect('print_session_certificate', certificate_id=certificate.id)
    else:
        form = CounselingSessionCertificateForm(instance=certificate, counselor=counselor)

    context = {
        'form': form,
        'certificate': certificate,
        'title': 'Edit Counseling Session Certificate',
    }
    return render(request, 'counselor/session_certificate_form.html', context)

@login_required
@user_passes_test(is_counselor)
def print_session_certificate(request, certificate_id):
    counselor = get_object_or_404(Counselor, user=request.user)
    certificate = get_object_or_404(CounselingSessionCertificate, id=certificate_id, counselor=counselor)

    context = {
        'certificate': certificate,
        'now': timezone.now(),
        'print_mode': True
    }
    return render(request, 'counselor/print_session_certificate.html', context)

@login_required
@user_passes_test(is_counselor)
def view_session(request, session_id):
    session = get_object_or_404(GuidanceSession, id=session_id)
    return render(request, 'counselor/view_session.html', {
        'session': session
    })

@login_required
@user_passes_test(is_counselor)
def print_session(request, session_id):
    session = get_object_or_404(GuidanceSession, id=session_id)
    return render(request, 'counselor/print_session.html', {
        'session': session
    })

@login_required
@user_passes_test(is_counselor)
def counselor_approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approval_status = 'approved'
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved')
    return redirect('counselor_student_list')

@login_required
@user_passes_test(is_counselor)
def counselor_reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approval_status = 'rejected'
    user.save()
    messages.success(request, f'User {user.username} has been rejected')
    return redirect('counselor_student_list')

@login_required
def counselor_profile(request):
    counselor = get_object_or_404(Counselor, user=request.user)

    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']

        # Update user information
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.phone_number = request.POST.get('phone_number')
        request.user.save()

        # Update counselor information
        counselor.specialization = request.POST.get('specialization')
        counselor.bio = request.POST.get('bio')
        counselor.save()

        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        if current_password and new_password:
            if request.user.check_password(current_password):
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password updated successfully.')
            else:
                messages.error(request, 'Current password is incorrect.')

        messages.success(request, 'Profile updated successfully.')
        return redirect('counselor_profile')

    return render(request, 'counselor/profile.html', {'counselor': counselor})

from django.http import HttpResponse
from io import BytesIO
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

@login_required
@user_passes_test(is_counselor)
def generate_counselor_report(request):
    try:
        if request.method == 'POST':
            logger.debug("Received POST request for report generation")
            counselor = get_object_or_404(Counselor, user=request.user)
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format')

            logger.debug(f"Parameters received - start_date: {start_date}, end_date: {end_date}, format: {report_format}")

            # Get sessions within date range
            sessions = GuidanceSession.objects.filter(
                counselor=counselor,
                date__range=[start_date, end_date]
            ).select_related('student__user').order_by('-date')

            logger.debug(f"Found {sessions.count()} sessions")

            if report_format == 'pdf':
                logger.debug("Generating PDF report")
                # Create the HttpResponse object with PDF headers
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

                # Container for the 'Flowable' objects
                elements = []

                # Define styles
                styles = getSampleStyleSheet()
                title_style = styles['Heading1']
                normal_style = styles['Normal']

                # Add title
                elements.append(Paragraph('Counseling Sessions Report', title_style))
                elements.append(Spacer(1, 20))

                # Add report info
                elements.append(Paragraph(f'Counselor: {counselor.user.get_full_name()}', normal_style))
                elements.append(Paragraph(f'Period: {datetime.strptime(start_date, "%Y-%m-%d").strftime("%B %d, %Y")} to {datetime.strptime(end_date, "%Y-%m-%d").strftime("%B %d, %Y")}', normal_style))
                elements.append(Paragraph(f'Total Sessions: {sessions.count()}', normal_style))
                elements.append(Paragraph(f'Generated on: {timezone.now().strftime("%B %d, %Y")}', normal_style))
                elements.append(Spacer(1, 20))

                # Create table data
                data = [['Date', 'Student Name', 'Session Type', 'Status', 'Notes']]
                for session in sessions:
                    data.append([
                        session.date.strftime('%Y-%m-%d'),
                        session.student.user.get_full_name(),
                        session.session_type,
                        session.status,
                        session.notes[:100] + '...' if session.notes and len(session.notes) > 100 else session.notes or ''
                    ])

                # Create table
                table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 2.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ]))
                elements.append(table)

                try:
                    # Build PDF
                    logger.debug("Building PDF document")
                    doc.build(elements)

                    # Get the value of the BytesIO buffer and return it
                    pdf = buffer.getvalue()
                    buffer.close()
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="counselor_report_{start_date}_to_{end_date}.pdf"'
                    response.write(pdf)
                    logger.debug("PDF generated successfully")
                    return response
                except Exception as e:
                    logger.error(f"Error generating PDF: {str(e)}")
                    raise

            elif report_format == 'excel':
                logger.debug("Generating Excel report")
                try:
                    # Prepare data for Excel
                    data = []
                    for session in sessions:
                        data.append({
                            'Date': session.date.strftime('%Y-%m-%d'),
                            'Student Name': session.student.user.get_full_name(),
                            'Session Type': session.session_type,
                            'Status': session.status,
                            'Notes': session.notes
                        })

                    # Create DataFrame and Excel file
                    df = pd.DataFrame(data)
                    excel_file = BytesIO()
                    df.to_excel(excel_file, index=False, sheet_name='Sessions Report')

                    # Create response
                    excel_file.seek(0)
                    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="counselor_report_{start_date}_to_{end_date}.xlsx"'
                    logger.debug("Excel report generated successfully")
                    return response
                except Exception as e:
                    logger.error(f"Error generating Excel report: {str(e)}")
                    raise

        logger.warning("Invalid request method or format")
        messages.error(request, 'Invalid request method or format')
        return redirect('counselor_reports_dashboard')
    except Exception as e:
        logger.error(f"Unexpected error in generate_counselor_report: {str(e)}")
        messages.error(request, f'An error occurred while generating the report: {str(e)}')
        return redirect('counselor_reports_dashboard')

@login_required
@user_passes_test(is_counselor)
def view_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    context = {
        'interview': interview,
        'view_only': True
    }
    return render(request, 'counselor/interview_form.html', context)

@login_required
@user_passes_test(is_counselor)
def schedule_followup(request, interview_id):
    """
    Convert a follow-up interview into an actual appointment
    """
    interview = get_object_or_404(Interview, id=interview_id)
    counselor = get_object_or_404(Counselor, user=request.user)

    # Verify this is a follow-up interview
    if not interview.follow_up_needed or not interview.follow_up_date:
        messages.error(request, "This interview does not require a follow-up.")
        return redirect('counselor_dashboard')

    if request.method == 'POST':
        # Create a new appointment based on the follow-up
        time = request.POST.get('time')
        purpose = f"Follow-up session for interview on {interview.date.strftime('%Y-%m-%d')}"

        # Create the appointment
        appointment = Appointment.objects.create(
            student=interview.student,
            counselor=counselor,
            date=interview.follow_up_date,
            time=time,
            purpose=purpose,
            status='approved'  # Auto-approve since counselor is creating it
        )

        messages.success(request, f"Follow-up appointment scheduled for {interview.student.user.get_full_name} on {interview.follow_up_date.strftime('%Y-%m-%d')} at {time}.")
        return redirect('counselor_dashboard')

    # If GET request, show the form to select time
    context = {
        'interview': interview,
        'follow_up_date': interview.follow_up_date
    }
    return render(request, 'counselor/schedule_followup.html', context)

from django.http import JsonResponse

@login_required
@user_passes_test(is_counselor)
def get_student_group_members(request, group_id):
    """
    API endpoint to get the members of a student group
    """
    try:
        student_group = get_object_or_404(StudentGroup, id=group_id)
        members = []

        for student in student_group.students.all():
            members.append({
                'id': student.id,
                'name': student.user.get_full_name(),
                'course': student.course,
                'year': student.year
            })

        return JsonResponse({
            'success': True,
            'group_name': student_group.name,
            'members': members
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@user_passes_test(is_counselor)
def get_student_details(request, student_id):
    """
    API endpoint to get details of a student
    """
    try:
        student = get_object_or_404(Student, id=student_id)

        # Get student details
        details = {
            'id': student.id,
            'name': student.user.get_full_name(),
            'course': student.course,
            'year': student.year,
            'gender': student.get_gender_display(),
            'contact_number': student.contact_number or 'Not provided',
            'address': student.address or 'Not provided',
            'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else 'Not provided',
            'age': student.get_age() or 'Not provided',
            'email': student.user.email or 'Not provided'
        }

        return JsonResponse({
            'success': True,
            'student': details
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
