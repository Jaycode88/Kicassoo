# Generated by Django 5.0.6 on 2024-11-02 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('printful_id', 'variant_id')},
        ),
    ]
