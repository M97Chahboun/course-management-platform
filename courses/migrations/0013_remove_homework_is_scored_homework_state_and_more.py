# Generated by Django 4.2.11 on 2024-05-08 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0012_project_points_for_peer_review_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homework",
            name="is_scored",
        ),
        migrations.AddField(
            model_name="homework",
            name="state",
            field=models.CharField(
                choices=[("CL", "CLOSED"), ("OP", "OPEN"), ("SC", "SCORED")],
                default="OP",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="state",
            field=models.CharField(
                choices=[
                    ("CL", "CLOSED"),
                    ("CS", "COLLECTING_SUBMISSIONS"),
                    ("PR", "PEER_REVIEWING"),
                    ("CO", "COMPLETED"),
                ],
                default="CS",
                max_length=2,
            ),
        ),
    ]
