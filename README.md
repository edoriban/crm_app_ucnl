# VanDev CRM — Gestión de Leads y Cotizaciones

Aplicación web desarrollada en Python con Flask para gestionar leads (prospectos) y cotizaciones de servicios tecnológicos.

**Curso:** ID0303 — Programación Orientada a Objetos
**Alumno:** Edgar
**Actividad:** Actividad Formativa 2

---

## Características

- CRUD completo de **Leads** con embudo de ventas (6 estados)
- CRUD completo de **Cotizaciones** con cálculo automático de subtotal, IVA y total
- **Catálogo de Servicios** tecnológicos
- Interfaz web responsiva con **Bootstrap 5**
- Persistencia en archivos **JSON**
- Dashboard con resumen estadístico

## Estructura del proyecto

```
crm_app/
├── app.py                  # Aplicación Flask (rutas y controladores)
├── requirements.txt        # Dependencias
├── models/
│   ├── __init__.py
│   ├── lead.py             # Clase Lead
│   ├── producto.py         # Clase Producto
│   ├── cotizacion.py       # Clases ItemCotizacion y Cotizacion
│   └── gestor.py           # Clases GestorLeads, GestorProductos, GestorCotizaciones
├── templates/
│   ├── base.html           # Plantilla base con sidebar
│   ├── dashboard.html      # Dashboard principal
│   ├── leads/
│   │   ├── lista.html
│   │   ├── detalle.html
│   │   ├── nuevo.html
│   │   └── editar.html
│   ├── cotizaciones/
│   │   ├── lista.html
│   │   ├── detalle.html
│   │   └── nueva.html
│   └── servicios/
│       ├── lista.html
│       └── nuevo.html
└── data/
    ├── leads.json
    ├── productos.json
    └── cotizaciones.json
```

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/crm_app.git
cd crm_app

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python app.py

# 4. Abrir en el navegador
# http://localhost:5000
```

## Conceptos de POO aplicados

| Concepto | Dónde se aplica |
|---|---|
| Clases y atributos | `Lead`, `Producto`, `ItemCotizacion`, `Cotizacion`, `Gestor*` |
| Constructor `__init__` | Todas las clases |
| Métodos de instancia | `cambiar_estado()`, `esta_activo()`, `subtotal()`, `total()`, etc. |
| Método de clase (`@classmethod`) | `Lead.from_dict()`, `Cotizacion.from_dict()`, `Producto.from_dict()` |
| Atributos de clase | `Lead.ESTADOS`, `Cotizacion.BADGE_ESTADO`, etc. |
| Encapsulamiento | Datos JSON gestionados solo a través de los Gestores |
| `__str__` / `__repr__` | Todas las clases modelo |
