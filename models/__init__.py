# models/__init__.py
# Exporta las clases principales del módulo de modelos

from .lead import Lead
from .lead_empresarial import LeadEmpresarial
from .lead_individual import LeadIndividual
from .producto import Producto
from .cotizacion import ItemCotizacion, Cotizacion
from .gestor import GestorLeads, GestorCotizaciones, GestorProductos

__all__ = [
    "Lead",
    "LeadEmpresarial",
    "LeadIndividual",
    "Producto",
    "ItemCotizacion",
    "Cotizacion",
    "GestorLeads",
    "GestorCotizaciones",
    "GestorProductos",
]
