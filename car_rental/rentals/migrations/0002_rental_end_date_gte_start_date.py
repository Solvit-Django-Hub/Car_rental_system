from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='rental',
            constraint=models.CheckConstraint(
                condition=Q(end_date__gte=F('start_date')),
                name='rental_end_date_gte_start_date',
            ),
        ),
    ]
