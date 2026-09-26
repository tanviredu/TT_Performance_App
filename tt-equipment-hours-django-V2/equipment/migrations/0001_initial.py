from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Equipment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("equipment_id", models.CharField(max_length=10, unique=True, verbose_name="Equipment ID")),
                (
                    "initial_hours",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Required before the first reading can be submitted.",
                        max_digits=10,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Initial cumulative hours",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
            ],
            options={
                "verbose_name": "Equipment",
                "verbose_name_plural": "Equipment",
                "ordering": ["equipment_id"],
            },
        ),
        migrations.CreateModel(
            name="Operator",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("operator_id", models.CharField(max_length=50, unique=True, verbose_name="Operator ID")),
                ("name", models.CharField(blank=True, max_length=100, verbose_name="Name")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
            ],
            options={
                "verbose_name": "Operator",
                "verbose_name_plural": "Operators",
                "ordering": ["operator_id"],
            },
        ),
        migrations.CreateModel(
            name="EquipmentHourRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate, editable=False, verbose_name="Date")),
                ("previous_hours", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Previous cumulative hours")),
                (
                    "total_hours",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Total cumulative hours",
                    ),
                ),
                ("shift_hours", models.DecimalField(decimal_places=2, max_digits=6, verbose_name="Shift hours")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created at")),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hour_records",
                        to="equipment.equipment",
                        verbose_name="Equipment",
                    ),
                ),
                (
                    "operator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hour_records",
                        to="equipment.operator",
                        verbose_name="Operator",
                    ),
                ),
            ],
            options={
                "verbose_name": "Equipment hour record",
                "verbose_name_plural": "Equipment hour records",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="equipmenthourrecord",
            constraint=models.UniqueConstraint(
                fields=("operator", "equipment", "date", "total_hours"),
                name="unique_operator_equipment_day_total",
            ),
        ),
    ]