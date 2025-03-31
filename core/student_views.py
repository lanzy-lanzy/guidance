from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Student, Appointment, GuidanceSession, Interview, Counselor
from datetime import datetime, timedelta

def is_student(user):
    return user.is_authenticated and user.role == 'student'

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    upcoming_appointments = Appointment.objects.filter(
        student=student,
        date__gte=timezone.now().date()
    ).order_by('date', 'time')[:5]
    
    recent_sessions = GuidanceSession.objects.filter(
        student=student
    ).order_by('-date')[:5]
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'recent_sessions': recent_sessions,
        'total_sessions': GuidanceSession.objects.filter(student=student).count(),
        'pending_appointments': Appointment.objects.filter(student=student, status='pending').count(),
        'completed_sessions': GuidanceSession.objects.filter(student=student, status='completed').count()
    }
    return render(request, 'student/dashboard.html', context)

@login_required
@user_passes_test(is_student)
def student_appointment_list(request):
    student = get_object_or_404(Student, user=request.user)
    appointments = Appointment.objects.filter(student=student).order_by('-date', '-time')
    counselors = Counselor.objects.all()
    
    # Get current date
    current_date = timezone.now().date()
    
    # Calculate pending appointments only
    pending_appointments = appointments.filter(
        status='pending',
        date__gte=current_date
    ).count()
    
    context = {
        'appointments': appointments,
        'counselors': counselors,
        'upcoming_appointments': appointments.filter(
            date__gte=current_date,
            status__in=['pending', 'approved']
        ),
        'past_appointments': appointments.filter(
            date__lt=current_date
        ),
        'pending_count': pending_appointments  # Changed from active_appointments
    }
    return render(request, 'student/appointments.html', context)

@login_required
@user_passes_test(is_student)
def student_session_history(request):
    student = get_object_or_404(Student, user=request.user)
    sessions = GuidanceSession.objects.filter(student=student).order_by('-date')
    return render(request, 'student/session_history.html', {'sessions': sessions})

@login_required
@user_passes_test(is_student)
def student_interview_forms(request):
    student = get_object_or_404(Student, user=request.user)
    interviews = Interview.objects.filter(student=student).order_by('-date')
    return render(request, 'student/interview_forms.html', {'interviews': interviews})

@login_required
@user_passes_test(is_student)
def student_counselor_list(request):
    counselors = Counselor.objects.all()
    return render(request, 'student/counselors.html', {'counselors': counselors})

@login_required
@user_passes_test(is_student)
def request_appointment(request):
    if request.method == 'POST':
        student = Student.objects.get(user=request.user)
        counselor_id = request.POST.get('counselor')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        counseling_type = request.POST.get('counseling_type')
        reason = request.POST.get('reason')
        
        try:
            date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            current_date = timezone.now().date()
            
            # Check if date is not in the past or today
            if date_obj <= current_date:
                messages.error(request, 'Please select a future date for your appointment.')
                return redirect('student_appointment_list')
            
            # Check if date is not a weekend
            if date_obj.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                messages.error(request, 'Appointments cannot be scheduled on weekends.')
                return redirect('student_appointment_list')
            
            # Check pending appointment limit (3 pending appointments)
            pending_count = Appointment.objects.filter(
                student=student,
                status='pending',
                date__gte=current_date
            ).count()
            
            if pending_count >= 3:
                messages.error(request, 'You cannot have more than 3 pending appointments at a time.')
                return redirect('student_appointment_list')
            
            counselor = get_object_or_404(Counselor, id=counselor_id)
            
            # Create the appointment
            appointment = Appointment.objects.create(
                student=student,
                counselor=counselor,
                date=appointment_date,
                time=appointment_time,
                purpose=reason,
                counseling_type=counseling_type,
                status='pending'
            )
            
            messages.success(request, 'Appointment request submitted successfully.')
            return redirect('student_appointment_list')
            
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('student_appointment_list')

    counselors = Counselor.objects.all()
    context = {
        'counselors': counselors,
        'today': timezone.now().date(),
        'pending_count': Appointment.objects.filter(
            student=request.user.student,
            status='pending',
            date__gte=timezone.now().date()
        ).count()
    }
    return render(request, 'student/request_appointment.html', context)

@login_required
@user_passes_test(is_student)
def cancel_appointment(request, appointment_id):
    student = get_object_or_404(Student, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, student=student)

    if appointment.status == 'pending':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this appointment.')

    return redirect('student_appointment_list')

@login_required
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']

        # Update user information
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        # Update student information
        student.course = request.POST.get('course')
        student.year = request.POST.get('year')
        student.contact_number = request.POST.get('contact_number')
        student.address = request.POST.get('address')
        student.birth_date = request.POST.get('birth_date')
        student.birth_place = request.POST.get('birth_place')
        student.civil_status = request.POST.get('civil_status')
        student.religion = request.POST.get('religion')
        
        # Family Background
        student.father_name = request.POST.get('father_name')
        student.father_occupation = request.POST.get('father_occupation')
        student.father_education = request.POST.get('father_education')
        student.mother_name = request.POST.get('mother_name')
        student.mother_occupation = request.POST.get('mother_occupation')
        student.mother_education = request.POST.get('mother_education')
        student.parents_marital_status = request.POST.get('parents_marital_status')
        
        # Educational Background
        student.elementary_school = request.POST.get('elementary_school')
        student.elementary_year_graduated = request.POST.get('elementary_year_graduated')
        student.high_school = request.POST.get('high_school')
        student.high_school_year_graduated = request.POST.get('high_school_year_graduated')
        
        student.save()

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
        return redirect('student_profile')

    return render(request, 'student/profile.html', {
        'student': student,
        'civil_status_choices': Student._meta.get_field('civil_status').choices,
        'parents_marital_status_choices': Student._meta.get_field('parents_marital_status').choices
    })
