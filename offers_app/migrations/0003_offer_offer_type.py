# Generated by Django 5.2.3 on 2025-06-23 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0002_remove_offerdetail_delivery_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='offer_type',
            field=models.CharField(choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')], default='basic', max_length=20),
        ),
    ]
