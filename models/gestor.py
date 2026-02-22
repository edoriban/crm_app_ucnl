# models/gestor.py
# Clases Gestor*: CRUD y persistencia JSON para Lead, Cotizacion y Producto

import json
import os
import uuid
from datetime import datetime

from .lead import Lead
from .cotizacion import Cotizacion, ItemCotizacion
from .producto import Producto


# ──────────────────────────────────────────────────────────────────
# GestorLeads
# ──────────────────────────────────────────────────────────────────

class GestorLeads:
    """
    Gestiona el ciclo de vida de los leads: creación, consulta,
    actualización, borrado y persistencia en archivo JSON.

    Atributos:
        archivo_json (str): Ruta al archivo de persistencia.
        leads (dict):       Diccionario id → Lead cargados en memoria.
    """

    def __init__(self, archivo_json: str):
        """
        Constructor del gestor.

        Args:
            archivo_json: Ruta al archivo JSON de persistencia.
        """
        self.archivo_json = archivo_json
        self.leads: dict[str, Lead] = {}
        self._cargar()

    # ── Persistencia ──────────────────────────────────────────────

    def _cargar(self) -> None:
        """Carga los leads desde el archivo JSON (si existe)."""
        if os.path.exists(self.archivo_json):
            with open(self.archivo_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.leads = {d["id"]: Lead.from_dict(d) for d in datos}

    def guardar(self) -> None:
        """Persiste todos los leads en el archivo JSON."""
        os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
        with open(self.archivo_json, "w", encoding="utf-8") as f:
            json.dump([lead.to_dict() for lead in self.leads.values()],
                      f, ensure_ascii=False, indent=2)

    # ── CRUD ──────────────────────────────────────────────────────

    def crear(self, nombre: str, empresa: str, email: str,
              telefono: str, servicio_interes: str,
              notas: str = "") -> Lead:
        """
        Crea un nuevo lead y lo persiste.

        Args:
            nombre:           Nombre del contacto.
            empresa:          Empresa del prospecto.
            email:            Correo de contacto.
            telefono:         Teléfono de contacto.
            servicio_interes: Servicio de interés.
            notas:            Notas opcionales.

        Returns:
            El Lead recién creado.
        """
        nuevo_id = f"L{uuid.uuid4().hex[:6].upper()}"
        lead = Lead(
            id=nuevo_id,
            nombre=nombre,
            empresa=empresa,
            email=email,
            telefono=telefono,
            servicio_interes=servicio_interes,
            notas=notas,
        )
        self.leads[nuevo_id] = lead
        self.guardar()
        return lead

    def obtener(self, lead_id: str) -> Lead | None:
        """Retorna el Lead con el id dado, o None si no existe."""
        return self.leads.get(lead_id)

    def listar(self, solo_activos: bool = False) -> list[Lead]:
        """
        Retorna la lista de leads, ordenados por fecha de creación (desc).

        Args:
            solo_activos: Si True, excluye leads cerrados.
        """
        resultado = list(self.leads.values())
        if solo_activos:
            resultado = [l for l in resultado if l.esta_activo()]
        return sorted(resultado, key=lambda l: l.fecha_creacion, reverse=True)

    def actualizar(self, lead_id: str, **campos) -> bool:
        """
        Actualiza campos de un lead existente.

        Args:
            lead_id: ID del lead a modificar.
            **campos: Pares campo=valor a actualizar.

        Returns:
            True si se actualizó, False si el lead no existe.
        """
        lead = self.obtener(lead_id)
        if not lead:
            return False
        campos_validos = {"nombre", "empresa", "email", "telefono",
                          "servicio_interes", "notas"}
        for campo, valor in campos.items():
            if campo in campos_validos:
                setattr(lead, campo, valor)
        self.guardar()
        return True

    def cambiar_estado(self, lead_id: str, nuevo_estado: str) -> bool:
        """
        Cambia el estado de un lead.

        Returns:
            True si el cambio fue exitoso.
        """
        lead = self.obtener(lead_id)
        if not lead:
            return False
        ok = lead.cambiar_estado(nuevo_estado)
        if ok:
            self.guardar()
        return ok

    def eliminar(self, lead_id: str) -> bool:
        """
        Elimina un lead del gestor.

        Returns:
            True si se eliminó, False si no existía.
        """
        if lead_id in self.leads:
            del self.leads[lead_id]
            self.guardar()
            return True
        return False

    def buscar(self, texto: str) -> list[Lead]:
        """
        Busca leads cuyo nombre, empresa o email contengan el texto dado.

        Args:
            texto: Cadena de búsqueda (no sensible a mayúsculas).

        Returns:
            Lista de leads que coinciden.
        """
        texto = texto.lower()
        return [
            l for l in self.leads.values()
            if texto in l.nombre.lower()
            or texto in l.empresa.lower()
            or texto in l.email.lower()
        ]

    # ── Estadísticas ──────────────────────────────────────────────

    def resumen(self) -> dict:
        """
        Retorna un diccionario con conteos por estado.

        Returns:
            {estado: conteo, …, "total": n}
        """
        conteos = {estado: 0 for estado in Lead.ESTADOS}
        for lead in self.leads.values():
            conteos[lead.estado] += 1
        conteos["total"] = len(self.leads)
        return conteos


# ──────────────────────────────────────────────────────────────────
# GestorProductos
# ──────────────────────────────────────────────────────────────────

class GestorProductos:
    """
    Gestiona el catálogo de productos/servicios tecnológicos
    con persistencia en archivo JSON.
    """

    def __init__(self, archivo_json: str):
        """
        Constructor del gestor.

        Args:
            archivo_json: Ruta al archivo JSON del catálogo.
        """
        self.archivo_json = archivo_json
        self.productos: dict[str, Producto] = {}
        self._cargar()

    # ── Persistencia ──────────────────────────────────────────────

    def _cargar(self) -> None:
        """Carga los productos desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            with open(self.archivo_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.productos = {d["id"]: Producto.from_dict(d) for d in datos}

    def guardar(self) -> None:
        """Persiste todos los productos en el archivo JSON."""
        os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
        with open(self.archivo_json, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.productos.values()],
                      f, ensure_ascii=False, indent=2)

    # ── CRUD ──────────────────────────────────────────────────────

    def crear(self, nombre: str, categoria: str, descripcion: str,
              precio_base: float, unidad: str = "proyecto") -> Producto:
        """Crea un nuevo producto en el catálogo."""
        nuevo_id = f"P{uuid.uuid4().hex[:6].upper()}"
        prod = Producto(
            id=nuevo_id,
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion,
            precio_base=precio_base,
            unidad=unidad,
        )
        self.productos[nuevo_id] = prod
        self.guardar()
        return prod

    def obtener(self, producto_id: str) -> Producto | None:
        """Retorna el Producto con el id dado, o None si no existe."""
        return self.productos.get(producto_id)

    def listar(self, solo_activos: bool = True) -> list[Producto]:
        """Lista todos los productos, opcionalmente filtrando por activos."""
        resultado = list(self.productos.values())
        if solo_activos:
            resultado = [p for p in resultado if p.activo]
        return sorted(resultado, key=lambda p: p.nombre)

    def actualizar(self, producto_id: str, **campos) -> bool:
        """Actualiza campos de un producto existente."""
        prod = self.obtener(producto_id)
        if not prod:
            return False
        campos_validos = {"nombre", "categoria", "descripcion",
                          "precio_base", "unidad", "activo"}
        for campo, valor in campos.items():
            if campo in campos_validos:
                if campo == "precio_base":
                    valor = max(0.0, float(valor))
                setattr(prod, campo, valor)
        self.guardar()
        return True

    def eliminar(self, producto_id: str) -> bool:
        """Elimina un producto del catálogo."""
        if producto_id in self.productos:
            del self.productos[producto_id]
            self.guardar()
            return True
        return False


# ──────────────────────────────────────────────────────────────────
# GestorCotizaciones
# ──────────────────────────────────────────────────────────────────

class GestorCotizaciones:
    """
    Gestiona las cotizaciones/propuestas comerciales
    con persistencia en archivo JSON.
    """

    def __init__(self, archivo_json: str):
        """
        Constructor del gestor.

        Args:
            archivo_json: Ruta al archivo JSON de cotizaciones.
        """
        self.archivo_json = archivo_json
        self.cotizaciones: dict[str, Cotizacion] = {}
        self._cargar()

    # ── Persistencia ──────────────────────────────────────────────

    def _cargar(self) -> None:
        """Carga las cotizaciones desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            with open(self.archivo_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.cotizaciones = {d["id"]: Cotizacion.from_dict(d) for d in datos}

    def guardar(self) -> None:
        """Persiste todas las cotizaciones en el archivo JSON."""
        os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
        with open(self.archivo_json, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.cotizaciones.values()],
                      f, ensure_ascii=False, indent=2)

    # ── CRUD ──────────────────────────────────────────────────────

    def crear(self, lead_id: str, nombre_cliente: str,
              empresa: str, notas: str = "",
              fecha_vigencia: str = "") -> Cotizacion:
        """
        Crea una nueva cotización vacía asociada a un lead.

        Args:
            lead_id:        ID del lead.
            nombre_cliente: Nombre del contacto.
            empresa:        Empresa del cliente.
            notas:          Condiciones especiales.
            fecha_vigencia: Fecha de expiración ISO.

        Returns:
            La Cotizacion recién creada.
        """
        nuevo_id = f"C{uuid.uuid4().hex[:6].upper()}"
        cot = Cotizacion(
            id=nuevo_id,
            lead_id=lead_id,
            nombre_cliente=nombre_cliente,
            empresa=empresa,
            notas=notas,
            fecha_vigencia=fecha_vigencia,
        )
        self.cotizaciones[nuevo_id] = cot
        self.guardar()
        return cot

    def obtener(self, cot_id: str) -> Cotizacion | None:
        """Retorna la Cotizacion con el id dado, o None."""
        return self.cotizaciones.get(cot_id)

    def listar(self, lead_id: str = None) -> list[Cotizacion]:
        """
        Lista cotizaciones, opcionalmente filtradas por lead.

        Args:
            lead_id: Si se indica, devuelve solo las cotizaciones de ese lead.
        """
        resultado = list(self.cotizaciones.values())
        if lead_id:
            resultado = [c for c in resultado if c.lead_id == lead_id]
        return sorted(resultado, key=lambda c: c.fecha_creacion, reverse=True)

    def agregar_item(self, cot_id: str, item: ItemCotizacion) -> bool:
        """
        Agrega un ítem a una cotización existente.

        Returns:
            True si se agregó, False si la cotización no existe.
        """
        cot = self.obtener(cot_id)
        if not cot:
            return False
        cot.agregar_item(item)
        self.guardar()
        return True

    def cambiar_estado(self, cot_id: str, nuevo_estado: str) -> bool:
        """Cambia el estado de una cotización."""
        cot = self.obtener(cot_id)
        if not cot:
            return False
        ok = cot.cambiar_estado(nuevo_estado)
        if ok:
            self.guardar()
        return ok

    def eliminar(self, cot_id: str) -> bool:
        """Elimina una cotización."""
        if cot_id in self.cotizaciones:
            del self.cotizaciones[cot_id]
            self.guardar()
            return True
        return False

    def resumen(self) -> dict:
        """Retorna conteos de cotizaciones por estado."""
        conteos = {estado: 0 for estado in Cotizacion.ESTADOS}
        for cot in self.cotizaciones.values():
            conteos[cot.estado] += 1
        conteos["total"] = len(self.cotizaciones)
        return conteos
