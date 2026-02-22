# models/producto.py
# Clase Producto: representa un servicio/producto tecnológico del catálogo

from datetime import datetime


class Producto:
    """
    Representa un servicio o producto tecnológico en el catálogo del CRM.

    Atributos:
        id (str):           Identificador único del producto.
        nombre (str):       Nombre del servicio/producto.
        categoria (str):    Categoría del servicio.
        descripcion (str):  Descripción detallada.
        precio_base (float): Precio base en MXN.
        unidad (str):       Unidad de medida (proyecto, mes, hora, etc.).
        activo (bool):      Si el producto está disponible para cotizar.
    """

    CATEGORIAS = [
        "desarrollo_web",
        "desarrollo_movil",
        "consultoria",
        "infraestructura",
        "soporte",
        "integracion",
        "analisis_datos",
        "otro",
    ]

    ETIQUETAS_CATEGORIA = {
        "desarrollo_web":   "Desarrollo Web",
        "desarrollo_movil": "Desarrollo Móvil",
        "consultoria":      "Consultoría IT",
        "infraestructura":  "Infraestructura",
        "soporte":          "Soporte Técnico",
        "integracion":      "Integración de Sistemas",
        "analisis_datos":   "Análisis de Datos",
        "otro":             "Otro",
    }

    UNIDADES = ["proyecto", "mes", "hora", "licencia", "usuario"]

    def __init__(self, id: str, nombre: str, categoria: str,
                 descripcion: str, precio_base: float,
                 unidad: str = "proyecto", activo: bool = True):
        """
        Constructor de la clase Producto.

        Args:
            id:          Identificador único.
            nombre:      Nombre del servicio.
            categoria:   Categoría (debe estar en CATEGORIAS).
            descripcion: Descripción del servicio.
            precio_base: Precio base en MXN (debe ser >= 0).
            unidad:      Unidad de cobro (proyecto, mes, hora…).
            activo:      Si está disponible para cotizar.
        """
        self.id = id
        self.nombre = nombre
        self.categoria = categoria if categoria in self.CATEGORIAS else "otro"
        self.descripcion = descripcion
        self.precio_base = max(0.0, float(precio_base))
        self.unidad = unidad if unidad in self.UNIDADES else "proyecto"
        self.activo = bool(activo)

    # ──────────────────────────────────────────
    # Métodos de instancia
    # ──────────────────────────────────────────

    def get_etiqueta_categoria(self) -> str:
        """Retorna la etiqueta legible de la categoría."""
        return self.ETIQUETAS_CATEGORIA.get(self.categoria, self.categoria)

    def get_precio_formateado(self) -> str:
        """Retorna el precio formateado en MXN."""
        return f"${self.precio_base:,.2f} / {self.unidad}"

    def aplicar_descuento(self, porcentaje: float) -> float:
        """
        Calcula el precio con un descuento aplicado.

        Args:
            porcentaje: Porcentaje de descuento (0–100).

        Returns:
            Precio con descuento aplicado.
        """
        descuento = max(0.0, min(100.0, porcentaje))
        return round(self.precio_base * (1 - descuento / 100), 2)

    def to_dict(self) -> dict:
        """Serializa el producto a un diccionario (para guardar en JSON)."""
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "categoria":   self.categoria,
            "descripcion": self.descripcion,
            "precio_base": self.precio_base,
            "unidad":      self.unidad,
            "activo":      self.activo,
        }

    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (f"Producto [{self.id}] {self.nombre} "
                f"| {self.get_etiqueta_categoria()} "
                f"| {self.get_precio_formateado()} | {estado}")

    def __repr__(self) -> str:
        return (f"Producto(id='{self.id}', nombre='{self.nombre}', "
                f"precio_base={self.precio_base})")

    # ──────────────────────────────────────────
    # Método de clase (factory)
    # ──────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        """
        Crea un objeto Producto a partir de un diccionario.

        Args:
            data: Diccionario con los datos del producto.

        Returns:
            Instancia de Producto.
        """
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            categoria=data.get("categoria", "otro"),
            descripcion=data.get("descripcion", ""),
            precio_base=data.get("precio_base", 0.0),
            unidad=data.get("unidad", "proyecto"),
            activo=data.get("activo", True),
        )
