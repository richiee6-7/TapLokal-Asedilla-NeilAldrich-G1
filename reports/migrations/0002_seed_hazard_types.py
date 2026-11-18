from django.db import migrations

HAZARD_TYPES = [
    ("Flooding", "Standing or rising floodwater in streets or homes.", 1),
    ("Fire", "Fire or fire risk that needs urgent attention.", 1),
    ("Downed Utility Wires", "Fallen or hanging electric, cable, or telephone wires.", 1),
    ("Fallen Tree", "Fallen tree or large branch blocking a road or structure.", 2),
    ("Road Damage", "Potholes, cracks, or sinkholes on barangay roads.", 2),
    ("Clogged Drainage", "Blocked canals or drains that may cause flooding.", 2),
    ("Uncollected Trash", "Garbage that has not been collected.", 3),
    ("Broken Streetlight", "Streetlight that is out or damaged.", 3),
]


def seed_hazard_types(apps, schema_editor):
    HazardType = apps.get_model("reports", "HazardType")
    for name, description, priority in HAZARD_TYPES:
        HazardType.objects.get_or_create(
            name=name, defaults={"description": description, "priority_level": priority}
        )


def remove_seeded_types(apps, schema_editor):
    HazardType = apps.get_model("reports", "HazardType")
    HazardType.objects.filter(name__in=[t[0] for t in HAZARD_TYPES], reports__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("reports", "0001_initial")]
    operations = [migrations.RunPython(seed_hazard_types, remove_seeded_types)]
