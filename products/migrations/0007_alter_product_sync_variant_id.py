# Generated by Django 5.0.6 on 2024-12-01 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_product_availability_remove_product_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sync_variant_id',
            field=models.BigIntegerField(),
        ),
    ]
