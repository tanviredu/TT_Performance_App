from django.core.management.base import BaseCommand

from equipment.models import Equipment


class Command(BaseCommand):
    help = "Create or restore the fixed TT01-TT18 equipment list."

    def handle(self, *args, **options):
        equipment_ids = [f"TT{number:02d}" for number in range(1, 19)]
        for equipment_id in equipment_ids:
            Equipment.objects.get_or_create(equipment_id=equipment_id)
        self.stdout.write(
            self.style.SUCCESS(f"Equipment seed complete: {len(equipment_ids)} records checked.")
        )