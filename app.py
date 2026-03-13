# app.py
# Aplicación Flask CRM — Gestión de Leads y Cotizaciones
# Empresa: Servicios Tecnológicos / Software

from flask import Flask, render_template, request, redirect, url_for, flash
from models import (GestorLeads, GestorCotizaciones, GestorProductos,
                    Lead, LeadEmpresarial, LeadIndividual)
from models.cotizacion import ItemCotizacion
import os

# ──────────────────────────────────────────────────────────────────
# Inicialización de la aplicación y gestores
# ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "crm_tech_secret_2024"   # Necesario para flash messages

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

gestor_leads      = GestorLeads(os.path.join(DATA_DIR, "leads.json"))
gestor_productos  = GestorProductos(os.path.join(DATA_DIR, "productos.json"))
gestor_cotizaciones = GestorCotizaciones(os.path.join(DATA_DIR, "cotizaciones.json"))

# ──────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Página principal: resumen del sistema CRM."""
    resumen_leads = gestor_leads.resumen()
    resumen_cots  = gestor_cotizaciones.resumen()
    leads_recientes = gestor_leads.listar()[:5]
    return render_template(
        "dashboard.html",
        resumen_leads=resumen_leads,
        resumen_cots=resumen_cots,
        leads_recientes=leads_recientes,
    )

# ──────────────────────────────────────────────────────────────────
# Rutas de Leads
# ──────────────────────────────────────────────────────────────────

@app.route("/leads")
def leads_lista():
    """Lista todos los leads con filtro opcional por estado."""
    estado_filtro = request.args.get("estado", "")
    busqueda      = request.args.get("q", "")
    if busqueda:
        leads = gestor_leads.buscar(busqueda)
    elif estado_filtro:
        leads = [l for l in gestor_leads.listar() if l.estado == estado_filtro]
    else:
        leads = gestor_leads.listar()

    return render_template(
        "leads/lista.html",
        leads=leads,
        estados=Lead.ESTADOS,
        etiquetas_estado=Lead.ETIQUETAS_ESTADO,
        estado_filtro=estado_filtro,
        busqueda=busqueda,
    )

@app.route("/leads/nuevo")
def leads_nuevo():
    """Página de selección de tipo de lead a crear."""
    return render_template("leads/nuevo.html")

@app.route("/leads/nuevo/empresarial", methods=["GET", "POST"])
def leads_nuevo_empresarial():
    """Formulario y acción para crear un lead empresarial (herencia)."""
    servicios = [p.nombre for p in gestor_productos.listar()]

    if request.method == "POST":
        nombre           = request.form.get("nombre", "").strip()
        empresa          = request.form.get("empresa", "").strip()
        email            = request.form.get("email", "").strip()
        telefono         = request.form.get("telefono", "").strip()
        servicio_interes = request.form.get("servicio_interes", "").strip()
        notas            = request.form.get("notas", "").strip()
        # Campos específicos de la subclase LeadEmpresarial
        rfc              = request.form.get("rfc", "").strip()
        num_empleados    = int(request.form.get("num_empleados", 0))
        presupuesto_anual = float(request.form.get("presupuesto_anual", 0))
        sector           = request.form.get("sector", "otro")

        if not nombre or not email:
            flash("Nombre y email son campos obligatorios.", "danger")
        else:
            lead = gestor_leads.crear_empresarial(
                nombre=nombre, empresa=empresa, email=email,
                telefono=telefono, servicio_interes=servicio_interes,
                notas=notas, rfc=rfc, num_empleados=num_empleados,
                presupuesto_anual=presupuesto_anual, sector=sector,
            )
            flash(f"Lead empresarial '{lead.nombre}' creado correctamente.", "success")
            return redirect(url_for("leads_detalle", lead_id=lead.id))

    return render_template(
        "leads/nuevo_empresarial.html",
        servicios=servicios,
        sectores=LeadEmpresarial.SECTORES,
        etiquetas_sector=LeadEmpresarial.ETIQUETAS_SECTOR,
    )

@app.route("/leads/nuevo/individual", methods=["GET", "POST"])
def leads_nuevo_individual():
    """Formulario y acción para crear un lead individual (herencia)."""
    servicios = [p.nombre for p in gestor_productos.listar()]

    if request.method == "POST":
        nombre           = request.form.get("nombre", "").strip()
        empresa          = request.form.get("empresa", "").strip()
        email            = request.form.get("email", "").strip()
        telefono         = request.form.get("telefono", "").strip()
        servicio_interes = request.form.get("servicio_interes", "").strip()
        notas            = request.form.get("notas", "").strip()
        # Campos específicos de la subclase LeadIndividual
        ocupacion            = request.form.get("ocupacion", "otro")
        referido_por         = request.form.get("referido_por", "").strip()
        presupuesto_estimado = float(request.form.get("presupuesto_estimado", 0))
        es_freelancer        = request.form.get("es_freelancer") == "on"

        if not nombre or not email:
            flash("Nombre y email son campos obligatorios.", "danger")
        else:
            lead = gestor_leads.crear_individual(
                nombre=nombre, empresa=empresa, email=email,
                telefono=telefono, servicio_interes=servicio_interes,
                notas=notas, ocupacion=ocupacion, referido_por=referido_por,
                presupuesto_estimado=presupuesto_estimado,
                es_freelancer=es_freelancer,
            )
            flash(f"Lead individual '{lead.nombre}' creado correctamente.", "success")
            return redirect(url_for("leads_detalle", lead_id=lead.id))

    return render_template(
        "leads/nuevo_individual.html",
        servicios=servicios,
        ocupaciones=LeadIndividual.OCUPACIONES,
        etiquetas_ocupacion=LeadIndividual.ETIQUETAS_OCUPACION,
    )

@app.route("/leads/<lead_id>")
def leads_detalle(lead_id):
    """Detalle de un lead: info, estado y cotizaciones asociadas."""
    lead = gestor_leads.obtener(lead_id)
    if not lead:
        flash("Lead no encontrado.", "danger")
        return redirect(url_for("leads_lista"))

    cotizaciones = gestor_cotizaciones.listar(lead_id=lead_id)
    # Determinar el tipo de lead para mostrar campos específicos
    tipo_lead = "base"
    if isinstance(lead, LeadEmpresarial):
        tipo_lead = "empresarial"
    elif isinstance(lead, LeadIndividual):
        tipo_lead = "individual"

    return render_template(
        "leads/detalle.html",
        lead=lead,
        cotizaciones=cotizaciones,
        estados=Lead.ESTADOS,
        etiquetas_estado=Lead.ETIQUETAS_ESTADO,
        tipo_lead=tipo_lead,
    )

@app.route("/leads/<lead_id>/editar", methods=["GET", "POST"])
def leads_editar(lead_id):
    """Formulario y acción para editar un lead."""
    lead = gestor_leads.obtener(lead_id)
    if not lead:
        flash("Lead no encontrado.", "danger")
        return redirect(url_for("leads_lista"))

    servicios = [p.nombre for p in gestor_productos.listar()]

    if request.method == "POST":
        campos = {
            "nombre":           request.form.get("nombre", "").strip(),
            "empresa":          request.form.get("empresa", "").strip(),
            "email":            request.form.get("email", "").strip(),
            "telefono":         request.form.get("telefono", "").strip(),
            "servicio_interes": request.form.get("servicio_interes", "").strip(),
            "notas":            request.form.get("notas", "").strip(),
        }
        # Campos adicionales según el tipo de lead (polimorfismo)
        if isinstance(lead, LeadEmpresarial):
            campos["rfc"]               = request.form.get("rfc", "").strip()
            campos["num_empleados"]     = int(request.form.get("num_empleados", 0))
            campos["presupuesto_anual"] = float(request.form.get("presupuesto_anual", 0))
            campos["sector"]            = request.form.get("sector", "otro")
        elif isinstance(lead, LeadIndividual):
            campos["ocupacion"]            = request.form.get("ocupacion", "otro")
            campos["referido_por"]         = request.form.get("referido_por", "").strip()
            campos["presupuesto_estimado"] = float(request.form.get("presupuesto_estimado", 0))
            campos["es_freelancer"]        = request.form.get("es_freelancer") == "on"

        gestor_leads.actualizar(lead_id, **campos)
        flash("Lead actualizado correctamente.", "success")
        return redirect(url_for("leads_detalle", lead_id=lead_id))

    # Determinar tipo para la vista
    tipo_lead = "base"
    if isinstance(lead, LeadEmpresarial):
        tipo_lead = "empresarial"
    elif isinstance(lead, LeadIndividual):
        tipo_lead = "individual"

    return render_template(
        "leads/editar.html", lead=lead, servicios=servicios,
        tipo_lead=tipo_lead,
        sectores=LeadEmpresarial.SECTORES,
        etiquetas_sector=LeadEmpresarial.ETIQUETAS_SECTOR,
        ocupaciones=LeadIndividual.OCUPACIONES,
        etiquetas_ocupacion=LeadIndividual.ETIQUETAS_OCUPACION,
    )

@app.route("/leads/<lead_id>/estado", methods=["POST"])
def leads_cambiar_estado(lead_id):
    """Acción para cambiar el estado de un lead."""
    nuevo_estado = request.form.get("estado", "")
    ok = gestor_leads.cambiar_estado(lead_id, nuevo_estado)
    if ok:
        flash("Estado actualizado.", "success")
    else:
        flash("Estado inválido.", "danger")
    return redirect(url_for("leads_detalle", lead_id=lead_id))

@app.route("/leads/<lead_id>/eliminar", methods=["POST"])
def leads_eliminar(lead_id):
    """Elimina un lead del sistema."""
    lead = gestor_leads.obtener(lead_id)
    if lead:
        gestor_leads.eliminar(lead_id)
        flash(f"Lead '{lead.nombre}' eliminado.", "warning")
    return redirect(url_for("leads_lista"))

# ──────────────────────────────────────────────────────────────────
# Rutas de Cotizaciones
# ──────────────────────────────────────────────────────────────────

@app.route("/cotizaciones")
def cotizaciones_lista():
    """Lista todas las cotizaciones."""
    cotizaciones = gestor_cotizaciones.listar()
    return render_template("cotizaciones/lista.html", cotizaciones=cotizaciones)

@app.route("/cotizaciones/nueva/<lead_id>", methods=["GET", "POST"])
def cotizaciones_nueva(lead_id):
    """Crea una nueva cotización para un lead."""
    lead = gestor_leads.obtener(lead_id)
    if not lead:
        flash("Lead no encontrado.", "danger")
        return redirect(url_for("leads_lista"))

    if request.method == "POST":
        notas          = request.form.get("notas", "").strip()
        fecha_vigencia = request.form.get("fecha_vigencia", "").strip()
        cot = gestor_cotizaciones.crear(
            lead_id=lead_id,
            nombre_cliente=lead.nombre,
            empresa=lead.empresa,
            notas=notas,
            fecha_vigencia=fecha_vigencia,
        )
        flash(f"Cotización {cot.id} creada.", "success")
        return redirect(url_for("cotizaciones_detalle", cot_id=cot.id))

    return render_template("cotizaciones/nueva.html", lead=lead)

@app.route("/cotizaciones/<cot_id>")
def cotizaciones_detalle(cot_id):
    """Detalle de una cotización."""
    cot = gestor_cotizaciones.obtener(cot_id)
    if not cot:
        flash("Cotización no encontrada.", "danger")
        return redirect(url_for("cotizaciones_lista"))

    lead      = gestor_leads.obtener(cot.lead_id)
    productos = gestor_productos.listar()
    from models.cotizacion import Cotizacion as CotModel
    return render_template(
        "cotizaciones/detalle.html",
        cot=cot,
        lead=lead,
        productos=productos,
        estados=CotModel.ESTADOS,
        etiquetas_estado=CotModel.ETIQUETAS_ESTADO,
    )

@app.route("/cotizaciones/<cot_id>/agregar_item", methods=["POST"])
def cotizaciones_agregar_item(cot_id):
    """Agrega un ítem/servicio a la cotización."""
    cot = gestor_cotizaciones.obtener(cot_id)
    if not cot:
        flash("Cotización no encontrada.", "danger")
        return redirect(url_for("cotizaciones_lista"))

    producto_id    = request.form.get("producto_id", "")
    cantidad       = int(request.form.get("cantidad", 1))
    descuento      = float(request.form.get("descuento", 0))
    producto       = gestor_productos.obtener(producto_id)

    if not producto:
        flash("Servicio no encontrado.", "danger")
    else:
        item = ItemCotizacion(
            producto_id=producto.id,
            nombre=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio_base,
            descuento=descuento,
        )
        gestor_cotizaciones.agregar_item(cot_id, item)
        flash(f"Servicio '{producto.nombre}' agregado.", "success")

    return redirect(url_for("cotizaciones_detalle", cot_id=cot_id))

@app.route("/cotizaciones/<cot_id>/estado", methods=["POST"])
def cotizaciones_cambiar_estado(cot_id):
    """Cambia el estado de una cotización."""
    nuevo_estado = request.form.get("estado", "")
    ok = gestor_cotizaciones.cambiar_estado(cot_id, nuevo_estado)
    flash("Estado actualizado." if ok else "Estado inválido.", "success" if ok else "danger")
    return redirect(url_for("cotizaciones_detalle", cot_id=cot_id))

@app.route("/cotizaciones/<cot_id>/eliminar", methods=["POST"])
def cotizaciones_eliminar(cot_id):
    """Elimina una cotización."""
    gestor_cotizaciones.eliminar(cot_id)
    flash("Cotización eliminada.", "warning")
    return redirect(url_for("cotizaciones_lista"))

# ──────────────────────────────────────────────────────────────────
# Rutas de Servicios (Catálogo de Productos)
# ──────────────────────────────────────────────────────────────────

@app.route("/servicios")
def servicios_lista():
    """Lista el catálogo de servicios tecnológicos."""
    productos = gestor_productos.listar(solo_activos=False)
    from models.producto import Producto
    return render_template(
        "servicios/lista.html",
        productos=productos,
        categorias=Producto.CATEGORIAS,
        etiquetas_categoria=Producto.ETIQUETAS_CATEGORIA,
    )

@app.route("/servicios/nuevo", methods=["GET", "POST"])
def servicios_nuevo():
    """Formulario y acción para añadir un nuevo servicio."""
    from models.producto import Producto
    if request.method == "POST":
        nombre      = request.form.get("nombre", "").strip()
        categoria   = request.form.get("categoria", "otro")
        descripcion = request.form.get("descripcion", "").strip()
        precio_base = float(request.form.get("precio_base", 0))
        unidad      = request.form.get("unidad", "proyecto")

        if not nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            prod = gestor_productos.crear(
                nombre=nombre,
                categoria=categoria,
                descripcion=descripcion,
                precio_base=precio_base,
                unidad=unidad,
            )
            flash(f"Servicio '{prod.nombre}' creado.", "success")
            return redirect(url_for("servicios_lista"))

    return render_template(
        "servicios/nuevo.html",
        categorias=Producto.CATEGORIAS,
        etiquetas_categoria=Producto.ETIQUETAS_CATEGORIA,
        unidades=Producto.UNIDADES,
    )

@app.route("/servicios/<producto_id>/toggle", methods=["POST"])
def servicios_toggle(producto_id):
    """Activa/desactiva un servicio del catálogo."""
    prod = gestor_productos.obtener(producto_id)
    if prod:
        gestor_productos.actualizar(producto_id, activo=not prod.activo)
        estado = "activado" if not prod.activo else "desactivado"
        flash(f"Servicio '{prod.nombre}' {estado}.", "info")
    return redirect(url_for("servicios_lista"))

# ──────────────────────────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
