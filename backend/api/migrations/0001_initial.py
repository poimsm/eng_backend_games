# Generated by Django 4.0.6 on 2024-03-09 03:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(max_length=50)),
                ('notes', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'devices',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('question', models.TextField()),
                ('difficulty', models.PositiveSmallIntegerField(choices=[(0, 'Easy'), (1, 'Moderate'), (2, 'Complex')])),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'Quiz question'), (1, 'Describe the picture'), (2, 'Build a story'), (3, 'Scenario')])),
                ('code', models.TextField(blank=True, null=True)),
                ('translations', models.JSONField(blank=True, null=True)),
                ('image_url', models.TextField(blank=True, null=True)),
                ('voice_url', models.TextField(blank=True, null=True)),
                ('category', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('scenario', models.JSONField(blank=True, null=True)),
                ('example', models.JSONField(blank=True, null=True)),
                ('style', models.JSONField(blank=True, null=True)),
                ('ranking', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('questions_type', models.TextField(default='random')),
                ('questions_search', models.TextField(default='random')),
                ('hardcoded_ids', models.TextField(blank=True, null=True)),
                ('starting_questions', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'question_config',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('verified', models.BooleanField(default=False)),
                ('screen_flow', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=150)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profiles',
            },
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('total_uses', models.PositiveSmallIntegerField(default=0)),
                ('last_time_used', models.DateTimeField()),
                ('question_id', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_history',
            },
        ),
        migrations.CreateModel(
            name='ScreenFlow',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(blank=True, max_length=50, null=True)),
                ('time', models.CharField(blank=True, max_length=50, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.device')),
            ],
            options={
                'db_table': 'screenflow',
            },
        ),
    ]
