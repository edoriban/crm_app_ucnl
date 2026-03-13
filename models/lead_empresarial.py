# models/lead_empresarial.py
# Clase LeadEmpresarial: hereda de Lead, representa un prospecto corporativo

from .lead import Lead


class LeadEmpresarial(Lead):
    """
    Representa un lead de tipo empresarial/corporativo en el CRM.

    Hereda todos los atributos y métodos de la clase base Lead,
    y agrega información específica de empresas: RFC, número de
    empleados, presupuesto anual y sector industrial.

    Atributos heredados de Lead:
        id, nombre, empresa, email, telefono, servicio_interes,
        estado, fecha_creacion, notas

    Atributos propios:
        rfc (str):               RFC de la empresa (Registro Federal de Contribuyentes).
        num_empleados (int):     Número aproximado de empleados.
        presupuesto_anual (float): Presupuesto anual disponible en MXN.
        sector (str):            Sector industrial de la empresa.
    """

    SECTORES = [
        "tecnologia",
        "salud",
        "educacion",
        "manufactura",
        "comercio",
        "servicios_financieros",
        "logistica",
        "construccion",
        "gobierno",
        "otro",
    ]

    ETIQUETAS_SECTOR = {
        "tecnologia":            "Tecnologia",
        "salud":                 "Salud",
        "educacion":             "Educacion",
        "manufactura":           "Manufactura",
        "comercio":              "Comercio",
        "servicios_financieros": "Servicios Financieros",
        "logistica":             "Logistica",
        "construccion":          "Construccion",
        "gobierno":              "Gobierno",
        "otro":                  "Otro",
    }

    def __init__(self, id: str, nombre: str, empresa: str,
                 email: str, telefono: str, servicio_interes: str,
                 rfc: str = "", num_empleados: int = 0,
                 presupuesto_anual: float = 0.0, sector: str = "otro",
                 estado: str = "nuevo", fecha_creacion: str = None,
                 notas: str = ""):
        """
        Constructor de LeadEmpresarial.

        Llama al constructor de la clase base (Lead) con super() para
        inicializar los atributos heredados, y luego inicializa los
        atributos propios de la subclase.

        Args:
            (heredados de Lead): id, nombre, empresa, email, telefono,
                                 servicio_interes, estado, fecha_creacion, notas
            rfc:                 RFC de la empresa.
            num_empleados:       Cantidad de empleados (>= 0).
            presupuesto_anual:   Presupuesto en MXN (>= 0).
            sector:              Sector industrial.
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
        self.rfc = rfc
        self.num_empleados = max(0, int(num_empleados))
        self.presupuesto_anual = max(0.0, float(presupuesto_anual))
        self.sector = sector if sector in self.SECTORES else "otro"

    # ──────────────────────────────────────────
    # Métodos propios de LeadEmpresarial
    # ──────────────────────────────────────────

    def es_empresa_grande(self) -> bool:
        """
        Determina si la empresa es grande (>= 100 empleados).

        Returns:
            True si tiene 100 o más empleados.
        """
        return self.num_empleados >= 100

    def calcular_potencial(self) -> str:
        """
        Calcula el potencial de negocio basado en presupuesto y tamaño.

        El potencial se clasifica en tres niveles:
        - Alto: presupuesto >= $500,000 MXN y empresa grande
        - Medio: presupuesto >= $100,000 MXN
        - Bajo: presupuesto < $100,000 MXN

        Returns:
            Cadena con el nivel de potencial ("Alto", "Medio", "Bajo").
        """
        if self.presupuesto_anual >= 500_000 and self.es_empresa_grande():
            return "Alto"
        elif self.presupuesto_anual >= 100_000:
            return "Medio"
        return "Bajo"

    def get_etiqueta_sector(self) -> str:
        """Retorna la etiqueta legible del sector."""
        return self.ETIQUETAS_SECTOR.get(self.sector, self.sector)

    def get_presupuesto_formateado(self) -> str:
        """Retorna el presupuesto anual formateado en MXN."""
        return f"${self.presupuesto_anual:,.2f} MXN"

    def get_clasificacion_tamano(self) -> str:
        """
        Clasifica la empresa por número de empleados.

        Returns:
            "Micro" (<10), "Pequeña" (10-49), "Mediana" (50-249) o "Grande" (250+).
        """
        if self.num_empleados < 10:
            return "Micro"
        elif self.num_empleados < 50:
            return "Pequena"
        elif self.num_empleados < 250:
            return "Mediana"
        return "Grande"

    # ──────────────────────────────────────────
    # Métodos sobrescritos (@Override)
    # ──────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Sobrescribe to_dict() de Lead para incluir los campos empresariales.

        Reutiliza el diccionario base de la clase padre y lo extiende
        con los atributos propios de LeadEmpresarial.

        Returns:
            Diccionario con todos los campos (base + empresariales).
        """
        # Reutiliza el método de la clase base
        data = super().to_dict()
        # Agrega el tipo para poder reconstruir la subclase correcta
        data["tipo"] = "empresarial"
        # Extiende con los atributos propios
        data["rfc"] = self.rfc
        data["num_empleados"] = self.num_empleados
        data["presupuesto_anual"] = self.presupuesto_anual
        data["sector"] = self.sector
        return data

    def __str__(self) -> str:
        """
        Sobrescribe __str__() para incluir info empresarial.

        Returns:
            Representación legible con datos corporativos.
        """
        base = super().__str__()
        return (f"{base} | RFC: {self.rfc or 'N/A'} "
                f"| {self.num_empleados} empleados "
                f"| Potencial: {self.calcular_potencial()}")

    def __repr__(self) -> str:
        return (f"LeadEmpresarial(id='{self.id}', nombre='{self.nombre}', "
                f"empresa='{self.empresa}', sector='{self.sector}')")

    # ──────────────────────────────────────────
    # Método de clase (factory) — sobrescrito
    # ──────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "LeadEmpresarial":
        """
        Crea un LeadEmpresarial a partir de un diccionario.

        Sobrescribe el factory method de Lead para manejar
        los campos adicionales de la subclase.

        Args:
            data: Diccionario con los datos del lead empresarial.

        Returns:
            Instancia de LeadEmpresarial.
        """
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            empresa=data["empresa"],
            email=data["email"],
            telefono=data["telefono"],
            servicio_interes=data["servicio_interes"],
            rfc=data.get("rfc", ""),
            num_empleados=data.get("num_empleados", 0),
            presupuesto_anual=data.get("presupuesto_anual", 0.0),
            sector=data.get("sector", "otro"),
            estado=data.get("estado", "nuevo"),
            fecha_creacion=data.get("fecha_creacion"),
            notas=data.get("notas", ""),
        )
