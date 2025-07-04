# Generated by Django 5.1.4 on 2025-01-24 10:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_student_address_student_birth_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='counselor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to='core.counselor'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('counselor', 'Counselor'), ('student', 'Student')], default='student', max_length=20),
        ),
    ]
