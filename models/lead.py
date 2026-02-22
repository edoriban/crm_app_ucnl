# models/lead.py
# Clase Lead: representa un prospecto/cliente potencial en el CRM

from datetime import datetime


class Lead:
    """
    Representa un lead (prospecto) en el sistema CRM.

    Un lead es un contacto o empresa que ha mostrado interés
    en los servicios tecnológicos de la empresa.

    Atributos:
        id (str):             Identificador único del lead.
        nombre (str):         Nombre completo del contacto.
        empresa (str):        Nombre de la empresa del prospecto.
        email (str):          Correo electrónico de contacto.
        telefono (str):       Teléfono de contacto.
        servicio_interes (str): Servicio tecnológico de interés.
        estado (str):         Estado actual del lead en el embudo.
        fecha_creacion (str): Fecha de creación en formato ISO.
        notas (str):          Notas adicionales del lead.
    """

    # Estados válidos del embudo de ventas
    ESTADOS = [
        "nuevo",
        "contactado",
        "calificado",
        "propuesta",
        "cerrado_ganado",
        "cerrado_perdido",
    ]

    ETIQUETAS_ESTADO = {
        "nuevo":          "Nuevo",
        "contactado":     "Contactado",
        "calificado":     "Calificado",
        "propuesta":      "Propuesta enviada",
        "cerrado_ganado": "Cerrado ✓ Ganado",
        "cerrado_perdido": "Cerrado ✗ Perdido",
    }

    # Clase Bootstrap para cada estado (usado en las vistas)
    BADGE_ESTADO = {
        "nuevo":          "secondary",
        "contactado":     "info",
        "calificado":     "primary",
        "propuesta":      "warning",
        "cerrado_ganado": "success",
        "cerrado_perdido": "danger",
    }

    def __init__(self, id: str, nombre: str, empresa: str,
                 email: str, telefono: str, servicio_interes: str,
                 estado: str = "nuevo", fecha_creacion: str = None,
                 notas: str = ""):
        """
        Constructor de la clase Lead.

        Args:
            id:               Identificador único.
            nombre:           Nombre del contacto.
            empresa:          Empresa del prospecto.
            email:            Email de contacto.
            telefono:         Teléfono de contacto.
            servicio_interes: Servicio de interés.
            estado:           Estado inicial (por defecto 'nuevo').
            fecha_creacion:   Fecha ISO; se asigna automáticamente si es None.
            notas:            Notas opcionales.
        """
        self.id = id
        self.nombre = nombre
        self.empresa = empresa
        self.email = email
        self.telefono = telefono
        self.servicio_interes = servicio_interes
        self.estado = estado if estado in self.ESTADOS else "nuevo"
        self.fecha_creacion = fecha_creacion or datetime.now().isoformat(timespec="seconds")
        self.notas = notas

    # ──────────────────────────────────────────
    # Métodos de instancia
    # ──────────────────────────────────────────

    def cambiar_estado(self, nuevo_estado: str) -> bool:
        """
        Cambia el estado del lead si el nuevo estado es válido.

        Args:
            nuevo_estado: Estado al que se quiere transicionar.

        Returns:
            True si el cambio fue exitoso, False si el estado es inválido.
        """
        if nuevo_estado in self.ESTADOS:
            self.estado = nuevo_estado
            return True
        return False

    def esta_activo(self) -> bool:
        """Retorna True si el lead no ha sido cerrado (ganado o perdido)."""
        return self.estado not in ("cerrado_ganado", "cerrado_perdido")

    def get_etiqueta_estado(self) -> str:
        """Retorna la etiqueta legible del estado actual."""
        return self.ETIQUETAS_ESTADO.get(self.estado, self.estado)

    def get_badge_estado(self) -> str:
        """Retorna la clase de color Bootstrap para el badge del estado."""
        return self.BADGE_ESTADO.get(self.estado, "secondary")

    def to_dict(self) -> dict:
        """Serializa el lead a un diccionario (para guardar en JSON)."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "empresa": self.empresa,
            "email": self.email,
            "telefono": self.telefono,
            "servicio_interes": self.servicio_interes,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
            "notas": self.notas,
        }

    def __str__(self) -> str:
        """Representación legible del lead."""
        return (f"Lead [{self.id}] {self.nombre} | {self.empresa} "
                f"| Estado: {self.get_etiqueta_estado()}")

    def __repr__(self) -> str:
        return f"Lead(id='{self.id}', nombre='{self.nombre}', estado='{self.estado}')"

    # ──────────────────────────────────────────
    # Método de clase (factory)
    # ──────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "Lead":
        """
        Crea un objeto Lead a partir de un diccionario.

        Args:
            data: Diccionario con los datos del lead.

        Returns:
            Instancia de Lead.
        """
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            empresa=data["empresa"],
            email=data["email"],
            telefono=data["telefono"],
            servicio_interes=data["servicio_interes"],
            estado=data.get("estado", "nuevo"),
            fecha_creacion=data.get("fecha_creacion"),
            notas=data.get("notas", ""),
        )
