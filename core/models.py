from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import os

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('counselor', 'Counselor'),
        ('student', 'Student'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    counselor = models.OneToOneField('Counselor', on_delete=models.CASCADE, null=True, blank=True, related_name='user_profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_active = True
            self.approval_status = 'approved'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    YEAR_LEVEL_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year')
    ]

    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed')
    ]

    PARENTS_MARITAL_STATUS_CHOICES = [
        ('Married', 'Married'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=1, choices=YEAR_LEVEL_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, default='Single')
    religion = models.CharField(max_length=100, blank=True, null=True)

    # Family Background
    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_education = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=255, blank=True, null=True)
    mother_education = models.CharField(max_length=255, blank=True, null=True)
    parents_marital_status = models.CharField(max_length=20, choices=PARENTS_MARITAL_STATUS_CHOICES, blank=True, null=True)

    # Educational Background
    elementary_school = models.CharField(max_length=255, blank=True, null=True)
    elementary_year_graduated = models.CharField(max_length=4, blank=True, null=True)
    high_school = models.CharField(max_length=255, blank=True, null=True)
    high_school_year_graduated = models.CharField(max_length=4, blank=True, null=True)

    reason_for_referral = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.course}, Year {self.year})"

    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def is_profile_complete(self):
        """
        Check if the student's profile is complete with all required information.
        Returns True if all required fields are filled, False otherwise.
        """
        required_fields = [
            self.course,
            self.year,
            self.gender,
            self.contact_number,
            self.address,
            self.birth_date,
            self.birth_place,
            self.civil_status,
            self.religion,
            # Family Background
            self.father_name,
            self.mother_name,
            self.parents_marital_status,
            # Educational Background
            self.elementary_school,
            self.elementary_year_graduated,
            self.high_school,
            self.high_school_year_graduated,
        ]

        return all(field for field in required_fields)

class Counselor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='counselor_profile')
    email = models.EmailField()

    def __str__(self):
        return self.user.username

class GuidanceSession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('Interview', 'Interview'),
        ('Referral', 'Referral'),
        ('Assessment', 'Assessment'),
        ('Follow-Up', 'Follow-Up'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="sessions")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    date = models.DateField(auto_now_add=True)
    time_started = models.DateTimeField(blank=True, null=True)
    time_ended = models.DateTimeField(blank=True, null=True)
    problem_statement = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    action_items = models.TextField(blank=True, null=True)
    next_steps = models.TextField(blank=True, null=True)
    appointment = models.OneToOneField('Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='session')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def start_session(self):
        if self.status == 'scheduled':
            self.status = 'in_progress'
            self.time_started = timezone.now()
            self.save()

    def end_session(self, problem_statement=None, recommendations=None, notes=None, action_items=None, next_steps=None):
        if self.status == 'in_progress':
            self.status = 'completed'
            self.time_ended = timezone.now()
            if problem_statement:
                self.problem_statement = problem_statement
            if recommendations:
                self.recommendations = recommendations
            if notes:
                self.notes = notes
            if action_items:
                self.action_items = action_items
            if next_steps:
                self.next_steps = next_steps
            self.save()

    def cancel_session(self):
        self.status = 'cancelled'
        self.save()

    @property
    def duration(self):
        if self.time_started and self.time_ended:
            return self.time_ended - self.time_started
        return None

    def __str__(self):
        return f"{self.session_type} with {self.student.user.username} by {self.counselor.user.username}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    TYPE_CHOICES = [
        ('ACADEMIC', 'Academic Counseling'),
        ('CAREER', 'Career Counseling'),
        ('PERSONAL', 'Personal Counseling'),
        ('MENTAL', 'Mental Health Counseling')
    ]


    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="appointments")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    purpose = models.TextField()
    counseling_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='ACADEMIC')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_rescheduled = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment for {self.student.user.username} with {self.counselor.user.username}"

    def check_conflicts(self):
        return Appointment.objects.filter(
            counselor=self.counselor,
            date=self.date,
            time=self.time,
            status__in=['pending', 'approved']
        ).exists()

class FollowUp(models.Model):
    session = models.OneToOneField(GuidanceSession, on_delete=models.CASCADE, related_name="followup")
    followup_date = models.DateField()
    followup_notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        return f"Follow-Up for {self.session.student.user.username} ({status})"

class Interview(models.Model):
    session = models.OneToOneField(GuidanceSession, on_delete=models.CASCADE, related_name='interview')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='interview_forms')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='conducted_interviews')
    date = models.DateField(auto_now_add=True)

    # Personal Information
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=255)
    age = models.IntegerField()
    civil_status = models.CharField(max_length=50)
    religion = models.CharField(max_length=100)

    # Family Background
    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_education = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=255, blank=True, null=True)
    mother_education = models.CharField(max_length=255, blank=True, null=True)
    parents_marital_status = models.CharField(max_length=100)

    # Educational Background
    elementary_school = models.CharField(max_length=255)
    elementary_year_graduated = models.CharField(max_length=50)
    high_school = models.CharField(max_length=255)
    high_school_year_graduated = models.CharField(max_length=50)
    college_school = models.CharField(max_length=255, blank=True, null=True)
    college_course = models.CharField(max_length=255, blank=True, null=True)

    # Interview Details
    reason_for_interview = models.TextField()
    presenting_problem = models.TextField()
    background_of_problem = models.TextField()
    counselor_notes = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    follow_up_needed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Interview Form - {self.student.user.username} - {self.date}"

class PsychologicalReport(models.Model):
    ABILITY_DESCRIPTION_CHOICES = [
        ('Very Superior', 'Very Superior'),
        ('Superior', 'Superior'),
        ('Above Average', 'Above Average'),
        ('Average', 'Average'),
        ('Below Average', 'Below Average'),
        ('Borderline', 'Borderline'),
        ('Intellectually Deficient', 'Intellectually Deficient'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='psychological_reports')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='conducted_psychological_reports')
    date = models.DateField(default=timezone.now)

    # Mental Ability Section
    mental_ability = models.CharField(max_length=255, blank=True, null=True)
    raw_score = models.CharField(max_length=10, blank=True, null=True)
    percentile_rank = models.CharField(max_length=10, blank=True, null=True)
    ability_description = models.CharField(max_length=50, choices=ABILITY_DESCRIPTION_CHOICES, blank=True, null=True)

    # Personality Section
    personality_assessment = models.TextField(blank=True, null=True)
    personality_scales = models.TextField(blank=True, null=True)

    # Remarks
    remarks = models.TextField(default="The results reflect the student's performance at the time of the assessment.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Psychological Report - {self.student.user.get_full_name()} - {self.date}"

class CounselingReferral(models.Model):
    # Referral information
    to_counselor_name = models.CharField(max_length=255, verbose_name='To Guidance Counselor', default='Guidance Counselor')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='referrals')
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateField(default=timezone.now)

    # Referral reasons - each as a boolean field
    reason_aggression = models.BooleanField(default=False)
    reason_dramatic_change = models.BooleanField(default=False)
    reason_bullying_victim = models.BooleanField(default=False)
    reason_bullying_bully = models.BooleanField(default=False)
    reason_self_injury = models.BooleanField(default=False)
    reason_daydreams = models.BooleanField(default=False)
    reason_anger_management = models.BooleanField(default=False)
    reason_fighting = models.BooleanField(default=False)
    reason_stealing = models.BooleanField(default=False)
    reason_sexual_acting_out = models.BooleanField(default=False)
    reason_peer_relationships = models.BooleanField(default=False)
    reason_social_skills = models.BooleanField(default=False)
    reason_family_concerns = models.BooleanField(default=False)
    reason_cries_easily = models.BooleanField(default=False)
    reason_self_image = models.BooleanField(default=False)
    reason_personal_hygiene = models.BooleanField(default=False)
    reason_lying = models.BooleanField(default=False)
    reason_grief_loss = models.BooleanField(default=False)

    reason_impulsive = models.BooleanField(default=False)
    reason_always_tired = models.BooleanField(default=False)
    reason_worried = models.BooleanField(default=False)
    reason_sadness = models.BooleanField(default=False)
    reason_scared = models.BooleanField(default=False)
    reason_absenteeism = models.BooleanField(default=False)
    reason_inattentive = models.BooleanField(default=False)
    reason_disruptive = models.BooleanField(default=False)
    reason_withdrawn = models.BooleanField(default=False)
    reason_anxious = models.BooleanField(default=False)
    reason_motivation = models.BooleanField(default=False)
    reason_academics = models.BooleanField(default=False)
    reason_study_skills = models.BooleanField(default=False)
    reason_homework_completion = models.BooleanField(default=False)
    reason_organization_skills = models.BooleanField(default=False)
    reason_early_pregnancy = models.BooleanField(default=False)
    reason_public_display_affection = models.BooleanField(default=False)
    reason_other = models.CharField(max_length=255, blank=True, null=True)

    # Recommendation
    recommendation = models.TextField(blank=True, null=True)

    # Referrer information
    referred_by_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Counseling Referral'
        verbose_name_plural = 'Counseling Referrals'

    def __str__(self):
        return f"Referral for {self.student.user.get_full_name()} - {self.date}"

class CounselingSessionCertificate(models.Model):
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual Counseling'),
        ('group', 'Group Counseling'),
        ('career', 'Career Counseling'),
        ('academic', 'Academic Counseling'),
        ('crisis', 'Crisis Intervention'),
        ('other', 'Other')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='session_certificates')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='issued_certificates')
    date = models.DateField(default=timezone.now)
    time_from = models.TimeField(verbose_name='Time From')
    time_to = models.TimeField(verbose_name='Time To')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='individual')
    other_session_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='Other Session Type')
    purpose = models.TextField(verbose_name='Purpose of Session')
    remarks = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Counseling Session Certificate'
        verbose_name_plural = 'Counseling Session Certificates'

    def __str__(self):
        return f"Certificate for {self.student.user.get_full_name()} - {self.date}"

    def save(self, *args, **kwargs):
        # Generate reference number if not provided
        if not self.reference_number:
            # Format: CSC-YYYYMMDD-XXX where XXX is a sequential number
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')

            # Count certificates created today and add 1
            count = CounselingSessionCertificate.objects.filter(
                created_at__date=today
            ).count() + 1

            self.reference_number = f"CSC-{date_str}-{count:03d}"

        super().save(*args, **kwargs)

class Report(models.Model):
    REPORT_TYPES = [
        ('student_summary', 'Student Summary Report'),
        ('session_analytics', 'Session Analytics Report'),
        ('counselor_performance', 'Counselor Performance Report'),
        ('case_management', 'Case Management Report'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to='reports/')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"

    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
