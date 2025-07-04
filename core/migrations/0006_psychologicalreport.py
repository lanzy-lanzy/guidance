# Generated by Django 5.1.1 on 2025-03-31 14:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_appointment_is_rescheduled'),
    ]

    operations = [
        migrations.CreateModel(
            name='PsychologicalReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('mental_ability', models.CharField(blank=True, max_length=255, null=True)),
                ('raw_score', models.CharField(blank=True, max_length=10, null=True)),
                ('percentile_rank', models.CharField(blank=True, max_length=10, null=True)),
                ('ability_description', models.CharField(blank=True, choices=[('Very Superior', 'Very Superior'), ('Superior', 'Superior'), ('Above Average', 'Above Average'), ('Average', 'Average'), ('Below Average', 'Below Average'), ('Borderline', 'Borderline'), ('Intellectually Deficient', 'Intellectually Deficient')], max_length=50, null=True)),
                ('personality_assessment', models.TextField(blank=True, null=True)),
                ('personality_scales', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(default="The results reflect the student's performance at the time of the assessment.")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('counselor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conducted_psychological_reports', to='core.counselor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='psychological_reports', to='core.student')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
