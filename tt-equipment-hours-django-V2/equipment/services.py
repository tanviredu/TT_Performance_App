from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Equipment, EquipmentHourRecord, Operator

SHIFT_LIMIT = Decimal("8")


def display_hours(value: Decimal) -> str:
    return format(value.normalize(), "f")


@dataclass(frozen=True)
class ReadingBounds:
    previous: Decimal
    maximum: Decimal


def get_reading_bounds(equipment: Equipment) -> ReadingBounds:
    latest = (
        EquipmentHourRecord.objects.filter(equipment=equipment)
        .order_by("-created_at", "-id")
        .first()
    )
    if latest is not None:
        previous = latest.total_hours
    elif equipment.initial_hours is not None:
        previous = equipment.initial_hours
    else:
        raise ValidationError(
            "এই Equipment-এর প্রথম Cumulative Hours নেওয়ার আগে Admin থেকে Initial Hours সেট করুন।",
            code="initial_hours_missing",
        )
    return ReadingBounds(previous=previous, maximum=previous + SHIFT_LIMIT)


def validate_cumulative_hours(
    equipment: Equipment,
    new_hours: Decimal,
    operator: Operator | None = None,
) -> ReadingBounds:
    bounds = get_reading_bounds(equipment)
    current_date = timezone.localdate()

    if operator is not None and EquipmentHourRecord.objects.filter(
        operator=operator,
        equipment=equipment,
        date=current_date,
        total_hours=new_hours,
    ).exists():
        raise ValidationError(
            "এই Equipment-এর জন্য একই Cumulative Hours ইতোমধ্যে জমা দেওয়া হয়েছে। অনুগ্রহ করে তথ্য যাচাই করুন।",
            code="duplicate",
        )

    if new_hours < bounds.previous:
        raise ValidationError(
            f"ভুল তথ্য! পূর্ববর্তী মোট সময় ছিল {display_hours(bounds.previous)} ঘণ্টা। বর্তমান সময় এর চেয়ে কম হতে পারবে না।",
            code="below_previous",
        )
    if new_hours > bounds.maximum:
        raise ValidationError(
            f"ভুল তথ্য! বর্তমান শিফটে সর্বোচ্চ 8 ঘণ্টা যোগ করা যাবে। সর্বোচ্চ গ্রহণযোগ্য সময় {display_hours(bounds.maximum)} ঘণ্টা।",
            code="above_shift_limit",
        )
    return bounds


@transaction.atomic
def create_hour_record(
    *,
    operator: Operator,
    equipment_id: int,
    total_hours: Decimal,
) -> EquipmentHourRecord:
    # The equipment row is locked while the latest reading is checked and saved.
    equipment = Equipment.objects.select_for_update().get(
        pk=equipment_id, is_active=True
    )
    bounds = validate_cumulative_hours(equipment, total_hours, operator)
    return EquipmentHourRecord.objects.create(
        operator=operator,
        equipment=equipment,
        previous_hours=bounds.previous,
        total_hours=total_hours,
        shift_hours=total_hours - bounds.previous,
    )