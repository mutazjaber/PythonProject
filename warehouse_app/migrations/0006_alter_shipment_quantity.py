# Generated by Django 4.2.7 on 2023-12-09 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_app', '0005_shipment_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]