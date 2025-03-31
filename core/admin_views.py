from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Student, Counselor, Appointment, Interview
from datetime import datetime
from django.db.models import Q
from .forms import UserForm
from .views import generate_pdf_report, generate_excel_report, generate_csv_report
import json

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    try:
        total_users = User.objects.count()
        active_students = Student.objects.filter(user__is_active=True).count()
        active_counselors = Counselor.objects.filter(user__is_active=True).count()
        pending_approvals = User.objects.filter(approval_status='pending').count()
        
        # Get recent users
        recent_users = User.objects.order_by('-date_joined')[:5]
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            date__gte=datetime.now()
        ).order_by('date')[:5]
        
        context = {
            'total_users': total_users,
            'active_students': active_students,
            'active_counselors': active_counselors,
            'pending_approvals': pending_approvals,
            'recent_users': recent_users,
            'upcoming_appointments': upcoming_appointments,
        }
        return render(request, 'admin/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def admin_add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'User created successfully')
            return redirect('admin_users')
    else:
        form = UserForm()
    return render(request, 'admin/add_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
                user.save()
            messages.success(request, 'User updated successfully')
            return redirect('admin_users')
    else:
        form = UserForm(instance=user)
    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('admin_users')
    return render(request, 'admin/delete_user.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def admin_approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.approval_status = 'approved'
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved')
    return redirect('admin_users')

@login_required
@user_passes_test(is_admin)
def admin_students(request):
    students = Student.objects.select_related('user').all()
    return render(request, 'admin/students.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def admin_counselors(request):
    counselors = Counselor.objects.select_related('user').all()
    return render(request, 'admin/counselors.html', {'counselors': counselors})

@login_required
@user_passes_test(is_admin)
def admin_appointments(request):
    appointments = Appointment.objects.select_related('student', 'counselor').all()
    return render(request, 'admin/appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    return render(request, 'admin/reports.html')

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    return render(request, 'admin/settings.html')

@login_required
@user_passes_test(is_admin)
def generate_sessions_report(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format', 'pdf')
            
            if not start_date or not end_date:
                messages.error(request, 'Please provide both start and end dates.')
                return redirect('admin_reports')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            if report_format == 'pdf':
                response = generate_pdf_report('sessions', start_date, end_date)
            elif report_format == 'excel':
                response = generate_excel_report('sessions', start_date, end_date)
            elif report_format == 'csv':
                response = generate_csv_report('sessions', start_date, end_date)
            else:
                messages.error(request, 'Invalid report format selected.')
                return redirect('admin_reports')
            
            return response
        
        return render(request, 'reports/generate_sessions_report.html')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('admin_reports')

@login_required
@user_passes_test(is_admin)
def generate_student_report(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format', 'pdf')
            
            if not start_date or not end_date:
                messages.error(request, 'Please provide both start and end dates.')
                return redirect('admin_reports')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            if report_format == 'pdf':
                response = generate_pdf_report('students', start_date, end_date)
            elif report_format == 'excel':
                response = generate_excel_report('students', start_date, end_date)
            elif report_format == 'csv':
                response = generate_csv_report('students', start_date, end_date)
            else:
                messages.error(request, 'Invalid report format selected.')
                return redirect('admin_reports')
            
            return response
        
        return render(request, 'reports/generate_student_report.html')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('admin_reports')

@login_required
@user_passes_test(is_admin)
def generate_counselor_report(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format', 'pdf')
            counselor_id = request.POST.get('counselor_id')
            
            if not start_date or not end_date:
                messages.error(request, 'Please provide both start and end dates.')
                return redirect('admin_reports')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            if report_format == 'pdf':
                response = generate_pdf_report('counselors', start_date, end_date, counselor_id=counselor_id)
            elif report_format == 'excel':
                response = generate_excel_report('counselors', start_date, end_date, counselor_id=counselor_id)
            elif report_format == 'csv':
                response = generate_csv_report('counselors', start_date, end_date, counselor_id=counselor_id)
            else:
                messages.error(request, 'Invalid report format selected.')
                return redirect('admin_reports')
            
            return response
        
        # Get list of counselors for the form
        counselors = Counselor.objects.all()
        return render(request, 'reports/generate_counselor_report.html', {'counselors': counselors})
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('admin_reports')

@login_required
@user_passes_test(is_admin)
def generate_appointment_report(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format', 'pdf')
            status = request.POST.get('status')
            
            if not start_date or not end_date:
                messages.error(request, 'Please provide both start and end dates.')
                return redirect('admin_reports')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Additional parameters for appointment reports
            params = {}
            if status:
                params['status'] = status
            
            if report_format == 'pdf':
                response = generate_pdf_report('appointments', start_date, end_date, **params)
            elif report_format == 'excel':
                response = generate_excel_report('appointments', start_date, end_date, **params)
            elif report_format == 'csv':
                response = generate_csv_report('appointments', start_date, end_date, **params)
            else:
                messages.error(request, 'Invalid report format selected.')
                return redirect('admin_reports')
            
            return response
        
        # Get appointment status choices for the form
        status_choices = Appointment.STATUS_CHOICES
        return render(request, 'reports/generate_appointment_report.html', {
            'status_choices': status_choices
        })
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('admin_reports')

@login_required
@user_passes_test(is_admin)
def generate_custom_report(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_format = request.POST.get('format', 'pdf')
            report_type = request.POST.get('report_type')
            filters = request.POST.get('filters', {})
            
            if not start_date or not end_date:
                messages.error(request, 'Please provide both start and end dates.')
                return redirect('admin_reports')
            
            if not report_type:
                messages.error(request, 'Please select a report type.')
                return redirect('admin_reports')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Handle custom filters based on report type
            params = {}
            if isinstance(filters, str):
                try:
                    filters = json.loads(filters)
                except json.JSONDecodeError:
                    filters = {}
            
            if filters:
                params.update(filters)
            
            if report_format == 'pdf':
                response = generate_pdf_report(report_type, start_date, end_date, **params)
            elif report_format == 'excel':
                response = generate_excel_report(report_type, start_date, end_date, **params)
            elif report_format == 'csv':
                response = generate_csv_report(report_type, start_date, end_date, **params)
            else:
                messages.error(request, 'Invalid report format selected.')
                return redirect('admin_reports')
            
            return response
        
        # Prepare data for the form
        report_types = [
            ('sessions', 'Sessions Report'),
            ('students', 'Students Report'),
            ('counselors', 'Counselors Report'),
            ('appointments', 'Appointments Report')
        ]
        
        status_choices = Appointment.STATUS_CHOICES
        counselors = Counselor.objects.all()
        
        context = {
            'report_types': report_types,
            'status_choices': status_choices,
            'counselors': counselors
        }
        
        return render(request, 'reports/generate_custom_report.html', context)
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('admin_reports')

@login_required
@user_passes_test(is_admin)
def view_interview_form(request, interview_id):
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        return render(request, 'counselor/view_interview.html', {
            'interview': interview,
            'student': interview.student,
            'counselor': interview.counselor,
            'view_only': True
        })
    except Exception as e:
        messages.error(request, f'Error viewing interview form: {str(e)}')
        return redirect('admin_students')
