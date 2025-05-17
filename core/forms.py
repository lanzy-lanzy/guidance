from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User, Student, Counselor, Appointment, Interview, PsychologicalReport, CounselingReferral, CounselingSessionCertificate
from django import forms
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'profile_picture']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300'})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300'})
    )
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300'})
    )

    class Meta:
        model = Appointment
        fields = ['counselor', 'date', 'time', 'purpose']
        widgets = {
            'counselor': forms.Select(attrs={'class': 'form-select mt-1 block w-full rounded-md border-gray-300'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['counselor'].queryset = Counselor.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        counselor = cleaned_data.get('counselor')

        if not date or not time or not counselor:
            return cleaned_data

        # Check if date is not in the past
        from django.utils import timezone
        current_date = timezone.now().date()
        if date < current_date:
            raise forms.ValidationError("Cannot schedule appointments in the past.")

        # Check if time is within business hours (8 AM to 5 PM)
        from datetime import time as dt_time
        if time < dt_time(8, 0) or time > dt_time(17, 0):
            raise forms.ValidationError("Appointments must be scheduled between 8:00 AM and 5:00 PM.")

        # Check for double booking
        from django.db.models import Q
        existing_appointment = Appointment.objects.filter(
            counselor=counselor,
            date=date,
            time=time,
            status__in=['pending', 'approved']
        ).exists()

        if existing_appointment:
            raise forms.ValidationError("This time slot is already booked. Please select a different time.")

        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
                })


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'address', 'contact_number', 'birth_date', 'birth_place', 'age',
            'civil_status', 'religion', 'father_name', 'father_occupation',
            'father_education', 'mother_name', 'mother_occupation',
            'mother_education', 'parents_marital_status', 'elementary_school',
            'elementary_year_graduated', 'high_school', 'high_school_year_graduated',
            'college_school', 'college_course', 'reason_for_interview',
            'presenting_problem', 'background_of_problem', 'counselor_notes',
            'recommendations', 'follow_up_needed', 'follow_up_date'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'civil_status': forms.Select(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'father_education': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_education': forms.TextInput(attrs={'class': 'form-control'}),
            'parents_marital_status': forms.Select(attrs={'class': 'form-control'}),
            'elementary_school': forms.TextInput(attrs={'class': 'form-control'}),
            'elementary_year_graduated': forms.TextInput(attrs={'class': 'form-control'}),
            'high_school': forms.TextInput(attrs={'class': 'form-control'}),
            'high_school_year_graduated': forms.TextInput(attrs={'class': 'form-control'}),
            'college_school': forms.TextInput(attrs={'class': 'form-control'}),
            'college_course': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_for_interview': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'presenting_problem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'background_of_problem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'counselor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_needed': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class PsychologicalReportForm(forms.ModelForm):
    class Meta:
        model = PsychologicalReport
        fields = [
            'student', 'date', 'mental_ability', 'raw_score', 'percentile_rank',
            'ability_description', 'personality_assessment', 'personality_scales', 'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'mental_ability': forms.TextInput(attrs={'class': 'form-control'}),
            'raw_score': forms.TextInput(attrs={'class': 'form-control'}),
            'percentile_rank': forms.TextInput(attrs={'class': 'form-control'}),
            'ability_description': forms.Select(attrs={'class': 'form-control'}),
            'personality_assessment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'personality_scales': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        counselor = kwargs.pop('counselor', None)
        super().__init__(*args, **kwargs)

        # Set the counselor field to the current counselor
        if counselor:
            self.instance.counselor = counselor

        # Apply Tailwind CSS classes to all form fields
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })


class CounselingReferralForm(forms.ModelForm):
    class Meta:
        model = CounselingReferral
        fields = [
            'to_counselor_name', 'referral_type', 'student', 'student_group', 'students', 'contact_number', 'date',
            'reason_aggression', 'reason_dramatic_change', 'reason_bullying_victim', 'reason_bullying_bully',
            'reason_self_injury', 'reason_daydreams', 'reason_anger_management', 'reason_fighting',
            'reason_stealing', 'reason_sexual_acting_out', 'reason_peer_relationships', 'reason_social_skills',
            'reason_family_concerns', 'reason_cries_easily', 'reason_self_image', 'reason_personal_hygiene',
            'reason_lying', 'reason_grief_loss',
            'reason_impulsive', 'reason_always_tired', 'reason_worried', 'reason_sadness',
            'reason_scared', 'reason_absenteeism', 'reason_inattentive', 'reason_disruptive',
            'reason_withdrawn', 'reason_anxious', 'reason_motivation', 'reason_academics',
            'reason_study_skills', 'reason_homework_completion', 'reason_organization_skills',
            'reason_early_pregnancy', 'reason_public_display_affection', 'reason_other',
            'recommendation', 'referred_by_name', 'subject'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'to_counselor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'referral_type': forms.RadioSelect(attrs={'class': 'referral-type-radio'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'student_group': forms.Select(attrs={'class': 'form-control'}),
            'students': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8', 'style': 'min-height: 200px;', 'multiple': 'multiple'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_other': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify other reason'}),
            'recommendation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'referred_by_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Tailwind CSS classes to all form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })

        # Add data attributes for dynamic showing/hiding
        self.fields['student'].widget.attrs['data-referral-type'] = 'individual'
        self.fields['student_group'].widget.attrs['data-referral-type'] = 'group'
        self.fields['students'].widget.attrs['data-referral-type'] = 'multiple'

        # Set initial state
        if not self.instance.pk:  # If this is a new form
            self.fields['student_group'].widget.attrs['class'] += ' hidden'
            self.fields['students'].widget.attrs['class'] += ' hidden'
        else:  # If editing an existing form
            if self.instance.referral_type == 'individual':
                self.fields['student_group'].widget.attrs['class'] += ' hidden'
                self.fields['students'].widget.attrs['class'] += ' hidden'
            elif self.instance.referral_type == 'group':
                self.fields['student'].widget.attrs['class'] += ' hidden'
                self.fields['students'].widget.attrs['class'] += ' hidden'
            elif self.instance.referral_type == 'multiple':
                self.fields['student'].widget.attrs['class'] += ' hidden'
                self.fields['student_group'].widget.attrs['class'] += ' hidden'

    def clean(self):
        cleaned_data = super().clean()
        referral_type = cleaned_data.get('referral_type')
        student = cleaned_data.get('student')
        student_group = cleaned_data.get('student_group')
        students = cleaned_data.get('students')

        if referral_type == 'individual' and not student:
            self.add_error('student', 'Please select a student for individual referral.')
        elif referral_type == 'group' and not student_group:
            self.add_error('student_group', 'Please select a student group for group referral.')
        elif referral_type == 'multiple' and (not students or students.count() == 0):
            self.add_error('students', 'Please select at least one student for multiple student referral.')

        return cleaned_data

class CounselingSessionCertificateForm(forms.ModelForm):
    class Meta:
        model = CounselingSessionCertificate
        fields = [
            'student', 'date', 'time_from', 'time_to', 'session_type',
            'other_session_type', 'purpose', 'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_from': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'time_to': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'session_type': forms.Select(attrs={'class': 'form-control'}),
            'other_session_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify if Other is selected'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        counselor = kwargs.pop('counselor', None)
        super().__init__(*args, **kwargs)

        # Set the counselor field to the current counselor
        if counselor:
            self.instance.counselor = counselor

        # Apply Tailwind CSS classes to all form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-200 focus:ring-opacity-50'
                })

        # Show/hide other_session_type field based on session_type
        self.fields['other_session_type'].widget.attrs['class'] += ' hidden'
        self.fields['other_session_type'].widget.attrs['data-show-if-session-type'] = 'other'
