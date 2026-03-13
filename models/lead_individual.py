# models/lead_individual.py
# Clase LeadIndividual: hereda de Lead, representa un prospecto particular/freelancer

from .lead import Lead


class LeadIndividual(Lead):
    """
    Representa un lead de tipo individual/particular en el CRM.

    Hereda todos los atributos y métodos de la clase base Lead,
    y agrega información específica de personas independientes:
    ocupación, quién lo refirió y presupuesto estimado.

    Atributos heredados de Lead:
        id, nombre, empresa, email, telefono, servicio_interes,
        estado, fecha_creacion, notas

    Atributos propios:
        ocupacion (str):            Ocupación o profesión del contacto.
        referido_por (str):         Nombre de quien refirió al lead.
        presupuesto_estimado (float): Presupuesto aproximado en MXN.
        es_freelancer (bool):       Si el contacto es freelancer o independiente.
    """

    OCUPACIONES = [
        "empresario_independiente",
        "freelancer",
        "profesionista",
        "emprendedor",
        "estudiante",
        "otro",
    ]

    ETIQUETAS_OCUPACION = {
        "empresario_independiente": "Empresario Independiente",
        "freelancer":              "Freelancer",
        "profesionista":           "Profesionista",
        "emprendedor":             "Emprendedor",
        "estudiante":              "Estudiante",
        "otro":                    "Otro",
    }

    def __init__(self, id: str, nombre: str, empresa: str,
                 email: str, telefono: str, servicio_interes: str,
                 ocupacion: str = "otro", referido_por: str = "",
                 presupuesto_estimado: float = 0.0,
                 es_freelancer: bool = False,
                 estado: str = "nuevo", fecha_creacion: str = None,
                 notas: str = ""):
        """
        Constructor de LeadIndividual.

        Llama al constructor de la clase base (Lead) con super() para
        inicializar los atributos heredados, y luego inicializa los
        atributos propios de la subclase.

        Args:
            (heredados de Lead): id, nombre, empresa, email, telefono,
                                 servicio_interes, estado, fecha_creacion, notas
            ocupacion:           Ocupación del contacto.
            referido_por:        Quién refirió al lead (cadena vacía si nadie).
            presupuesto_estimado: Presupuesto estimado en MXN (>= 0).
            es_freelancer:       True si el contacto es freelancer.
        """
        # Llamada al constructor de la clase base (herencia)
        super().__init__(
            id=id,
            nombre=nombre,
            empresa=empresa,
            email=email,
            telefono=telefono,
            servicio_interes=servicio_interes,
            estado=estado,
            fecha_creacion=fecha_creacion,
            notas=notas,
        )
        # Atributos propios de la subclase
        self.ocupacion = ocupacion if ocupacion in self.OCUPACIONES else "otro"
        self.referido_por = referido_por
        self.presupuesto_estimado = max(0.0, float(presupuesto_estimado))
        self.es_freelancer = bool(es_freelancer)

    # ──────────────────────────────────────────
    # Métodos propios de LeadIndividual
    # ──────────────────────────────────────────

    def tiene_referencia(self) -> bool:
        """
        Verifica si el lead fue referido por alguien.

        Returns:
            True si tiene un referente registrado.
        """
        return bool(self.referido_por.strip())

    def get_etiqueta_ocupacion(self) -> str:
        """Retorna la etiqueta legible de la ocupación."""
        return self.ETIQUETAS_OCUPACION.get(self.ocupacion, self.ocupacion)

    def get_presupuesto_formateado(self) -> str:
        """Retorna el presupuesto estimado formateado en MXN."""
        return f"${self.presupuesto_estimado:,.2f} MXN"

    def calcular_prioridad(self) -> str:
        """
        Calcula la prioridad de atención basada en referencia y presupuesto.

        Criterios:
        - Alta: tiene referencia y presupuesto >= $50,000
        - Media: tiene referencia o presupuesto >= $20,000
        - Baja: no tiene referencia y presupuesto < $20,000

        Returns:
            Cadena con el nivel de prioridad ("Alta", "Media", "Baja").
        """
        if self.tiene_referencia() and self.presupuesto_estimado >= 50_000:
            return "Alta"
        elif self.tiene_referencia() or self.presupuesto_estimado >= 20_000:
            return "Media"
        return "Baja"

    def get_resumen_corto(self) -> str:
        """
        Genera un resumen corto del lead para listados rápidos.

        Returns:
            Cadena con nombre, ocupación y prioridad.
        """
        ref = f" (Ref: {self.referido_por})" if self.tiene_referencia() else ""
        return (f"{self.nombre} — {self.get_etiqueta_ocupacion()}"
                f"{ref} | Prioridad: {self.calcular_prioridad()}")

    # ──────────────────────────────────────────
    # Métodos sobrescritos (@Override)
    # ──────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Sobrescribe to_dict() de Lead para incluir los campos individuales.

        Reutiliza el diccionario base de la clase padre y lo extiende
        con los atributos propios de LeadIndividual.

        Returns:
            Diccionario con todos los campos (base + individuales).
        """
        # Reutiliza el método de la clase base
        data = super().to_dict()
        # Agrega el tipo para poder reconstruir la subclase correcta
        data["tipo"] = "individual"
        # Extiende con los atributos propios
        data["ocupacion"] = self.ocupacion
        data["referido_por"] = self.referido_por
        data["presupuesto_estimado"] = self.presupuesto_estimado
        data["es_freelancer"] = self.es_freelancer
        return data

    def __str__(self) -> str:
        """
        Sobrescribe __str__() para incluir info del individuo.

        Returns:
            Representación legible con datos personales.
        """
        base = super().__str__()
        ref = f" | Referido por: {self.referido_por}" if self.tiene_referencia() else ""
        return (f"{base} | {self.get_etiqueta_ocupacion()}"
                f"{ref} | Prioridad: {self.calcular_prioridad()}")

    def __repr__(self) -> str:
        return (f"LeadIndividual(id='{self.id}', nombre='{self.nombre}', "
                f"ocupacion='{self.ocupacion}')")

    # ──────────────────────────────────────────
    # Método de clase (factory) — sobrescrito
    # ──────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "LeadIndividual":
        """
        Crea un LeadIndividual a partir de un diccionario.

        Sobrescribe el factory method de Lead para manejar
        los campos adicionales de la subclase.

        Args:
            data: Diccionario con los datos del lead individual.

        Returns:
            Instancia de LeadIndividual.
        """
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            empresa=data.get("empresa", ""),
            email=data["email"],
            telefono=data["telefono"],
            servicio_interes=data["servicio_interes"],
            ocupacion=data.get("ocupacion", "otro"),
            referido_por=data.get("referido_por", ""),
            presupuesto_estimado=data.get("presupuesto_estimado", 0.0),
            es_freelancer=data.get("es_freelancer", False),
            estado=data.get("estado", "nuevo"),
            fecha_creacion=data.get("fecha_creacion"),
            notas=data.get("notas", ""),
        )
