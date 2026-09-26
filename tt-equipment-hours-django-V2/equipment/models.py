from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Operator(models.Model):
    operator_id = models.CharField("Operator ID", max_length=50, unique=True)
    name = models.CharField("Name", max_length=100, blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ["operator_id"]
        verbose_name = "Operator"
        verbose_name_plural = "Operators"

    def __str__(self) -> str:
        return f"{self.operator_id} — {self.name}" if self.name else self.operator_id


class Equipment(models.Model):
    equipment_id = models.CharField("Equipment ID", max_length=10, unique=True)
    initial_hours = models.DecimalField(
        "Initial cumulative hours",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Required before the first reading can be submitted.",
    )
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ["equipment_id"]
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"

    def __str__(self) -> str:
        return self.equipment_id


class EquipmentHourRecord(models.Model):
    operator = models.ForeignKey(
        Operator,
        on_delete=models.PROTECT,
        related_name="hour_records",
        verbose_name="Operator",
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="hour_records",
        verbose_name="Equipment",
    )
    date = models.DateField("Date", default=timezone.localdate, editable=False)
    previous_hours = models.DecimalField(
        "Previous cumulative hours", max_digits=10, decimal_places=2
    )
    total_hours = models.DecimalField(
        "Total cumulative hours",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    shift_hours = models.DecimalField("Shift hours", max_digits=6, decimal_places=2)
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Equipment hour record"
        verbose_name_plural = "Equipment hour records"
        constraints = [
            models.UniqueConstraint(
                fields=["operator", "equipment", "date", "total_hours"],
                name="unique_operator_equipment_day_total",
            )
        ]

    def __str__(self) -> str:
        return f"{self.equipment.equipment_id} — {self.total_hours}"