# models/cotizacion.py
# Clases ItemCotizacion y Cotizacion: representan una cotización/propuesta

from datetime import datetime


class ItemCotizacion:
    """
    Representa un ítem (renglón) dentro de una cotización.

    Atributos:
        producto_id (str):   ID del producto/servicio cotizado.
        nombre (str):        Nombre del servicio (copiado al momento de cotizar).
        cantidad (int):      Cantidad de unidades.
        precio_unitario (float): Precio unitario al momento de la cotización.
        descuento (float):   Porcentaje de descuento aplicado (0–100).
    """

    def __init__(self, producto_id: str, nombre: str,
                 cantidad: int, precio_unitario: float,
                 descuento: float = 0.0):
        """
        Constructor de ItemCotizacion.

        Args:
            producto_id:     ID del producto/servicio.
            nombre:          Nombre descriptivo del servicio.
            cantidad:        Número de unidades (>= 1).
            precio_unitario: Precio por unidad en MXN.
            descuento:       Descuento en porcentaje (0–100).
        """
        self.producto_id = producto_id
        self.nombre = nombre
        self.cantidad = max(1, int(cantidad))
        self.precio_unitario = max(0.0, float(precio_unitario))
        self.descuento = max(0.0, min(100.0, float(descuento)))

    # ──────────────────────────────────────────
    # Cálculos del ítem
    # ──────────────────────────────────────────

    def subtotal_bruto(self) -> float:
        """Subtotal sin descuento: cantidad × precio_unitario."""
        return round(self.cantidad * self.precio_unitario, 2)

    def monto_descuento(self) -> float:
        """Monto del descuento aplicado al subtotal bruto."""
        return round(self.subtotal_bruto() * self.descuento / 100, 2)

    def subtotal_neto(self) -> float:
        """Subtotal con descuento: subtotal_bruto − monto_descuento."""
        return round(self.subtotal_bruto() - self.monto_descuento(), 2)

    def to_dict(self) -> dict:
        """Serializa el ítem a diccionario."""
        return {
            "producto_id":     self.producto_id,
            "nombre":          self.nombre,
            "cantidad":        self.cantidad,
            "precio_unitario": self.precio_unitario,
            "descuento":       self.descuento,
        }

    def __str__(self) -> str:
        return (f"  [{self.producto_id}] {self.nombre} "
                f"× {self.cantidad} "
                f"@ ${self.precio_unitario:,.2f} "
                f"(−{self.descuento:.0f}%) = ${self.subtotal_neto():,.2f}")

    @classmethod
    def from_dict(cls, data: dict) -> "ItemCotizacion":
        """Crea un ItemCotizacion a partir de un diccionario."""
        return cls(
            producto_id=data["producto_id"],
            nombre=data["nombre"],
            cantidad=data.get("cantidad", 1),
            precio_unitario=data.get("precio_unitario", 0.0),
            descuento=data.get("descuento", 0.0),
        )


class Cotizacion:
    """
    Representa una cotización/propuesta comercial asociada a un Lead.

    Atributos:
        id (str):            Identificador único de la cotización.
        lead_id (str):       ID del lead al que pertenece.
        nombre_cliente (str): Nombre del contacto (copiado del lead).
        empresa (str):       Empresa del cliente.
        items (list):        Lista de ItemCotizacion.
        estado (str):        Estado de la cotización.
        fecha_creacion (str): Fecha de creación ISO.
        fecha_vigencia (str): Fecha hasta la que es válida.
        notas (str):         Notas o condiciones especiales.
        iva_porcentaje (float): IVA aplicado (por defecto 16%).
    """

    ESTADOS = [
        "borrador",
        "enviada",
        "aceptada",
        "rechazada",
        "vencida",
    ]

    ETIQUETAS_ESTADO = {
        "borrador":  "Borrador",
        "enviada":   "Enviada al cliente",
        "aceptada":  "Aceptada ✓",
        "rechazada": "Rechazada ✗",
        "vencida":   "Vencida",
    }

    BADGE_ESTADO = {
        "borrador":  "secondary",
        "enviada":   "info",
        "aceptada":  "success",
        "rechazada": "danger",
        "vencida":   "warning",
    }

    def __init__(self, id: str, lead_id: str,
                 nombre_cliente: str, empresa: str,
                 items: list = None,
                 estado: str = "borrador",
                 fecha_creacion: str = None,
                 fecha_vigencia: str = None,
                 notas: str = "",
                 iva_porcentaje: float = 16.0):
        """
        Constructor de la clase Cotizacion.

        Args:
            id:              Identificador único.
            lead_id:         ID del lead asociado.
            nombre_cliente:  Nombre del contacto.
            empresa:         Empresa del cliente.
            items:           Lista de ItemCotizacion.
            estado:          Estado inicial (por defecto 'borrador').
            fecha_creacion:  Fecha ISO; se asigna automáticamente si es None.
            fecha_vigencia:  Fecha de vigencia ISO.
            notas:           Notas o condiciones especiales.
            iva_porcentaje:  Tasa de IVA en % (por defecto 16.0).
        """
        self.id = id
        self.lead_id = lead_id
        self.nombre_cliente = nombre_cliente
        self.empresa = empresa
        self.items = items if items is not None else []
        self.estado = estado if estado in self.ESTADOS else "borrador"
        self.fecha_creacion = fecha_creacion or datetime.now().isoformat(timespec="seconds")
        self.fecha_vigencia = fecha_vigencia or ""
        self.notas = notas
        self.iva_porcentaje = max(0.0, float(iva_porcentaje))

    # ──────────────────────────────────────────
    # Gestión de ítems
    # ──────────────────────────────────────────

    def agregar_item(self, item: ItemCotizacion) -> None:
        """Agrega un ítem a la cotización."""
        self.items.append(item)

    def eliminar_item(self, producto_id: str) -> bool:
        """
        Elimina el primer ítem con el producto_id dado.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        for i, item in enumerate(self.items):
            if item.producto_id == producto_id:
                self.items.pop(i)
                return True
        return False

    # ──────────────────────────────────────────
    # Cálculos financieros
    # ──────────────────────────────────────────

    def subtotal(self) -> float:
        """Suma de subtotales netos de todos los ítems (sin IVA)."""
        return round(sum(item.subtotal_neto() for item in self.items), 2)

    def iva(self) -> float:
        """Monto del IVA sobre el subtotal."""
        return round(self.subtotal() * self.iva_porcentaje / 100, 2)

    def total(self) -> float:
        """Total a pagar: subtotal + IVA."""
        return round(self.subtotal() + self.iva(), 2)

    # ──────────────────────────────────────────
    # Estado
    # ──────────────────────────────────────────

    def cambiar_estado(self, nuevo_estado: str) -> bool:
        """
        Cambia el estado de la cotización.

        Returns:
            True si el cambio fue exitoso, False si el estado es inválido.
        """
        if nuevo_estado in self.ESTADOS:
            self.estado = nuevo_estado
            return True
        return False

    def get_etiqueta_estado(self) -> str:
        """Retorna la etiqueta legible del estado actual."""
        return self.ETIQUETAS_ESTADO.get(self.estado, self.estado)

    def get_badge_estado(self) -> str:
        """Retorna la clase de color Bootstrap para el badge del estado."""
        return self.BADGE_ESTADO.get(self.estado, "secondary")

    def esta_activa(self) -> bool:
        """True si la cotización no ha sido aceptada, rechazada ni vencida."""
        return self.estado in ("borrador", "enviada")

    # ──────────────────────────────────────────
    # Serialización
    # ──────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serializa la cotización a diccionario (para guardar en JSON)."""
        return {
            "id":              self.id,
            "lead_id":         self.lead_id,
            "nombre_cliente":  self.nombre_cliente,
            "empresa":         self.empresa,
            "items":           [item.to_dict() for item in self.items],
            "estado":          self.estado,
            "fecha_creacion":  self.fecha_creacion,
            "fecha_vigencia":  self.fecha_vigencia,
            "notas":           self.notas,
            "iva_porcentaje":  self.iva_porcentaje,
        }

    def __str__(self) -> str:
        return (f"Cotizacion [{self.id}] {self.empresa} "
                f"| {len(self.items)} ítem(s) "
                f"| Total: ${self.total():,.2f} MXN "
                f"| {self.get_etiqueta_estado()}")

    def __repr__(self) -> str:
        return (f"Cotizacion(id='{self.id}', lead_id='{self.lead_id}', "
                f"estado='{self.estado}')")

    @classmethod
    def from_dict(cls, data: dict) -> "Cotizacion":
        """
        Crea una Cotizacion a partir de un diccionario.

        Args:
            data: Diccionario con los datos de la cotización.

        Returns:
            Instancia de Cotizacion con sus ítems reconstruidos.
        """
        items = [ItemCotizacion.from_dict(i) for i in data.get("items", [])]
        return cls(
            id=data["id"],
            lead_id=data["lead_id"],
            nombre_cliente=data.get("nombre_cliente", ""),
            empresa=data.get("empresa", ""),
            items=items,
            estado=data.get("estado", "borrador"),
            fecha_creacion=data.get("fecha_creacion"),
            fecha_vigencia=data.get("fecha_vigencia", ""),
            notas=data.get("notas", ""),
            iva_porcentaje=data.get("iva_porcentaje", 16.0),
        )
