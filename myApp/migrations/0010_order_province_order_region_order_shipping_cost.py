# Generated by Django 5.1.2 on 2025-06-19 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0009_remove_order_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='region',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
