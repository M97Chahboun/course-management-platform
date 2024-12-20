# Generated by Django 4.2.14 on 2024-12-03 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0018_course_finished"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="instructor",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courses_teaching",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
