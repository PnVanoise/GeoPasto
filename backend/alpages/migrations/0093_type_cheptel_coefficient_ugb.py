from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0092_fix_exploiter_cheptel_nullable"),
    ]

    operations = [
        migrations.AddField(
            model_name="type_cheptel",
            name="coefficient_UGB",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=3,
                validators=[MinValueValidator(0), MaxValueValidator(1)],
            ),
        ),
    ]
