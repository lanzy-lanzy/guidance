from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Student, Counselor
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial data for the application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up initial data...')

        # Create counselor account
        counselor_user = User.objects.create_user(
            username='wella',
            password='counselor123',
            first_name='Wella',
            last_name='Dela Cruz',
            role='counselor',
            approval_status='approved',
            is_active=True
        )
        
        Counselor.objects.create(
            user=counselor_user,
            email='wella.delacruz@jhcsc.edu.ph'
        )
        
        self.stdout.write(self.style.SUCCESS('Created counselor account: Wella Dela Cruz'))

        # Create example student accounts
        # Student 1: John Doe
        john_user = User.objects.create_user(
            username='john.doe',
            password='student123',
            first_name='John',
            last_name='Doe',
            role='student',
            approval_status='approved',
            is_active=True
        )
        
        Student.objects.create(
            user=john_user,
            course='Bachelor of Science in Information Technology',
            year='1',
            gender='M',
            contact_number='09123456789',
            address='123 Main St., Dumingag, Zamboanga del Sur',
            birth_date=datetime.strptime('2003-05-15', '%Y-%m-%d').date(),
            birth_place='Dumingag, Zamboanga del Sur',
            civil_status='Single',
            religion='Catholic',
            father_name='Robert Doe',
            father_occupation='Farmer',
            father_education='High School Graduate',
            mother_name='Mary Doe',
            mother_occupation='Teacher',
            mother_education='College Graduate',
            parents_marital_status='Married',
            elementary_school='Dumingag Central Elementary School',
            elementary_year_graduated='2015',
            high_school='Dumingag National High School',
            high_school_year_graduated='2021',
            reason_for_referral='Academic consultation'
        )
        
        self.stdout.write(self.style.SUCCESS('Created student account: John Doe'))

        # Student 2: Jane Smith
        jane_user = User.objects.create_user(
            username='jane.smith',
            password='student123',
            first_name='Jane',
            last_name='Smith',
            role='student',
            approval_status='approved',
            is_active=True
        )
        
        Student.objects.create(
            user=jane_user,
            course='Bachelor of Science in Education',
            year='2',
            gender='F',
            contact_number='09187654321',
            address='456 Oak St., Dumingag, Zamboanga del Sur',
            birth_date=datetime.strptime('2002-08-20', '%Y-%m-%d').date(),
            birth_place='Pagadian City, Zamboanga del Sur',
            civil_status='Single',
            religion='Protestant',
            father_name='William Smith',
            father_occupation='Business Owner',
            father_education='College Graduate',
            mother_name='Sarah Smith',
            mother_occupation='Nurse',
            mother_education='College Graduate',
            parents_marital_status='Married',
            elementary_school='St. Paul\'s Elementary School',
            elementary_year_graduated='2014',
            high_school='St. Paul\'s Academy',
            high_school_year_graduated='2020',
            reason_for_referral='Career guidance'
        )
        
        self.stdout.write(self.style.SUCCESS('Created student account: Jane Smith'))
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
