# Generated by Django 5.2.3 on 2025-07-07 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0006_offerdetail_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to='offer_pictures/'),
        ),
    ]
