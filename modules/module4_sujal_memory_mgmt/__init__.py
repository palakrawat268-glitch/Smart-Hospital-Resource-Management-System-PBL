# modules/module4_sujal_memory_mgmt/__init__.py
# Author: Sujal Kumar
# OS Concept: Memory Management / Dynamic Partitioning

from .models import Ward, Bed
from .routes import bed_bp, recalc_ward_occupancy

__all__ = ['Ward', 'Bed', 'bed_bp', 'recalc_ward_occupancy']
