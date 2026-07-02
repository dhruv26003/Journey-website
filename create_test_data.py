#!/usr/bin/env python
"""Create test memories for testing the gallery"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from memories.models import Memory
from datetime import date, timedelta

# Create test memories if none exist
if Memory.objects.count() == 0:
    memories_data = [
        {"caption": "Our first adventure together", "date": date(2024, 1, 15), "display_order": 1},
        {"caption": "Beautiful sunset at the beach", "date": date(2024, 2, 20), "display_order": 2},
        {"caption": "The day we laughed so hard", "date": date(2024, 3, 10), "display_order": 3},
        {"caption": "Making memories in the city", "date": date(2024, 4, 5), "display_order": 4},
        {"caption": "A quiet moment together", "date": date(2024, 5, 12), "display_order": 5},
    ]
    
    for data in memories_data:
        Memory.objects.create(
            caption=data["caption"],
            date=data["date"],
            display_order=data["display_order"],
            alt_text=data["caption"],
            photo='memories/placeholder.jpg'  # Using placeholder since we don't have real images
        )
    
    print(f"Created {len(memories_data)} test memories")
else:
    print(f"Database already has {Memory.objects.count()} memories")
