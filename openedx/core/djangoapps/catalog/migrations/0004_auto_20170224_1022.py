# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_catalogintegration_page_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogintegration',
            name='page_size',
            field=models.PositiveIntegerField(default=100, help_text='Maximum number of records in paginated response of a single request to catalog service.', verbose_name='Page Size'),
        ),
    ]
