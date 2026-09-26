from django.db import migrations


EQUIPMENT_IDS = [f"TT{number:02d}" for number in range(1, 19)]
OPERATOR_IDS = [f"OP{number:03d}" for number in range(1, 6)]


def seed_defaults(apps, schema_editor):
    Equipment = apps.get_model("equipment", "Equipment")
    Operator = apps.get_model("equipment", "Operator")
    for equipment_id in EQUIPMENT_IDS:
        Equipment.objects.get_or_create(equipment_id=equipment_id)
    for operator_id in OPERATOR_IDS:
        Operator.objects.get_or_create(operator_id=operator_id)


def remove_defaults(apps, schema_editor):
    Equipment = apps.get_model("equipment", "Equipment")
    Operator = apps.get_model("equipment", "Operator")
    Equipment.objects.filter(equipment_id__in=EQUIPMENT_IDS).delete()
    Operator.objects.filter(operator_id__in=OPERATOR_IDS).delete()


class Migration(migrations.Migration):
    dependencies = [("equipment", "0001_initial")]
    operations = [migrations.RunPython(seed_defaults, remove_defaults)]