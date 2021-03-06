# Generated by Django 3.1.3 on 2020-12-10 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201208_0355'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='products',
            field=models.ManyToManyField(to='core.OrderProducts'),
        ),
        migrations.AlterField(
            model_name='orderprocess',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.payment'),
        ),
    ]
