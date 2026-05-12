import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# =====================================================
# BASE DE DATOS
# =====================================================

conexion = sqlite3.connect("residuos.db")
cursor = conexion.cursor()

# Tabla rutas
cursor.execute('''
CREATE TABLE IF NOT EXISTS rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
)
''')

# Tabla registros
cursor.execute('''
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_id INTEGER,
    cantidad REAL,
    fecha TEXT
)
''')

conexion.commit()

# =====================================================
# FUNCIONES
# =====================================================

# Cambiar entre vistas
def cambiar_vista(frame):
    for f in contenedor.winfo_children():
        f.pack_forget()
    frame.pack(fill="both", expand=True)

# -----------------------------------------------------

# Agregar nueva ruta
def agregar_ruta():
    nombre = entry_ruta.get().strip()

    if nombre == "":
        messagebox.showwarning("Error", "Ingrese el nombre de la ruta")
        return

    cursor.execute(
        "INSERT INTO rutas (nombre) VALUES (?)",
        (nombre,)
    )

    conexion.commit()

    messagebox.showinfo("Éxito", "Ruta agregada correctamente")

    entry_ruta.delete(0, tk.END)

    cargar_rutas()
    actualizar_dashboard()

# -----------------------------------------------------

# Cargar rutas en combobox
def cargar_rutas():
    cursor.execute("SELECT id, nombre FROM rutas")

    rutas = cursor.fetchall()

    combo_rutas['values'] = [
        f"{r[0]} - {r[1]}"
        for r in rutas
    ]

# -----------------------------------------------------

# Registrar residuos
def registrar_residuo():

    # Validar ruta
    if not combo_rutas.get():
        messagebox.showwarning("Error", "Seleccione una ruta")
        return

    # Validar cantidad
    cantidad = entry_cantidad.get().strip()

    try:
        cantidad = float(cantidad)

        if cantidad <= 0:
            messagebox.showwarning(
                "Error",
                "La cantidad debe ser mayor a 0"
            )
            return

    except:
        messagebox.showwarning(
            "Error",
            "Ingrese una cantidad válida"
        )
        return

    # Validar fecha
    fecha = entry_fecha.get().strip()

    try:
        datetime.strptime(fecha, "%Y-%m-%d")

    except:
        messagebox.showwarning(
            "Error",
            "Formato de fecha inválido\nUse YYYY-MM-DD"
        )
        return

    # Obtener ID ruta
    ruta_id = combo_rutas.get().split(" - ")[0]

    # Insertar registro
    cursor.execute(
        '''
        INSERT INTO registros (ruta_id, cantidad, fecha)
        VALUES (?, ?, ?)
        ''',
        (ruta_id, cantidad, fecha)
    )

    conexion.commit()

    messagebox.showinfo(
        "Éxito",
        "Registro guardado correctamente"
    )

    # Limpiar campos
    entry_cantidad.delete(0, tk.END)
    entry_fecha.delete(0, tk.END)

    mostrar_registros()
    actualizar_dashboard()

# -----------------------------------------------------

# Mostrar registros
def mostrar_registros():

    for fila in tabla.get_children():
        tabla.delete(fila)

    cursor.execute('''
    SELECT registros.id,
           rutas.nombre,
           registros.cantidad,
           registros.fecha

    FROM registros

    JOIN rutas
    ON registros.ruta_id = rutas.id
    ''')

    datos = cursor.fetchall()

    for row in datos:
        tabla.insert("", tk.END, values=row)

# -----------------------------------------------------

# Eliminar registro
def eliminar_registro():

    seleccion = tabla.selection()

    if not seleccion:
        messagebox.showwarning(
            "Error",
            "Seleccione un registro"
        )
        return

    item = tabla.item(seleccion)

    registro_id = item['values'][0]

    confirmar = messagebox.askyesno(
        "Confirmar",
        "¿Desea eliminar el registro?"
    )

    if confirmar:

        cursor.execute(
            "DELETE FROM registros WHERE id=?",
            (registro_id,)
        )

        conexion.commit()

        mostrar_registros()
        actualizar_dashboard()

        messagebox.showinfo(
            "Éxito",
            "Registro eliminado"
        )

# -----------------------------------------------------

# Dashboard
def actualizar_dashboard():

    # Total residuos
    cursor.execute(
        "SELECT SUM(cantidad) FROM registros"
    )

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    # Total rutas
    cursor.execute(
        "SELECT COUNT(*) FROM rutas"
    )

    rutas = cursor.fetchone()[0]

    # Total registros
    cursor.execute(
        "SELECT COUNT(*) FROM registros"
    )

    registros = cursor.fetchone()[0]

    # Actualizar labels
    label_total.config(
        text=f"Total recolectado: {total} kg"
    )

    label_rutas.config(
        text=f"Rutas registradas: {rutas}"
    )

    label_registros.config(
        text=f"Registros almacenados: {registros}"
    )

# =====================================================
# INTERFAZ
# =====================================================

ventana = tk.Tk()

ventana.title(
    "Sistema Inteligente de Gestión de Residuos"
)

ventana.geometry("1100x650")

ventana.config(bg="#ecf0f1")

# =====================================================
# SIDEBAR
# =====================================================

sidebar = tk.Frame(
    ventana,
    bg="#2c3e50",
    width=220
)

sidebar.pack(
    side="left",
    fill="y"
)

# Título sidebar
tk.Label(
    sidebar,
    text="SGRS",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#2c3e50"
).pack(pady=20)

# =====================================================
# CONTENEDOR PRINCIPAL
# =====================================================

contenedor = tk.Frame(
    ventana,
    bg="#ecf0f1"
)

contenedor.pack(
    side="right",
    fill="both",
    expand=True
)

# =====================================================
# VISTA INICIO
# =====================================================

frame_inicio = tk.Frame(
    contenedor,
    bg="#ecf0f1"
)

tk.Label(
    frame_inicio,
    text="Sistema Inteligente de Gestión de Residuos",
    font=("Arial", 20, "bold"),
    bg="#ecf0f1",
    fg="#2c3e50"
).pack(pady=20)

label_total = tk.Label(
    frame_inicio,
    text="Total recolectado: 0 kg",
    font=("Arial", 14),
    bg="#ecf0f1"
)

label_total.pack(pady=10)

label_rutas = tk.Label(
    frame_inicio,
    text="Rutas registradas: 0",
    font=("Arial", 14),
    bg="#ecf0f1"
)

label_rutas.pack(pady=10)

label_registros = tk.Label(
    frame_inicio,
    text="Registros almacenados: 0",
    font=("Arial", 14),
    bg="#ecf0f1"
)

label_registros.pack(pady=10)

# =====================================================
# VISTA RUTAS
# =====================================================

frame_rutas = tk.Frame(
    contenedor,
    bg="#ecf0f1"
)

tk.Label(
    frame_rutas,
    text="Gestión de Rutas",
    font=("Arial", 18, "bold"),
    bg="#ecf0f1"
).pack(pady=15)

entry_ruta = tk.Entry(
    frame_rutas,
    width=40
)

entry_ruta.pack(pady=10)

tk.Button(
    frame_rutas,
    text="Agregar Ruta",
    command=agregar_ruta,
    bg="#27ae60",
    fg="white",
    font=("Arial", 11, "bold")
).pack(pady=5)

# =====================================================
# VISTA REGISTROS
# =====================================================

frame_registros = tk.Frame(
    contenedor,
    bg="#ecf0f1"
)

tk.Label(
    frame_registros,
    text="Registro de Residuos",
    font=("Arial", 18, "bold"),
    bg="#ecf0f1"
).pack(pady=15)

# Combobox rutas
combo_rutas = ttk.Combobox(
    frame_registros,
    width=40
)

combo_rutas.pack(pady=5)

# Cantidad
entry_cantidad = tk.Entry(
    frame_registros,
    width=42
)

entry_cantidad.pack(pady=5)

# Fecha
entry_fecha = tk.Entry(
    frame_registros,
    width=42
)

entry_fecha.pack(pady=5)

# Botón registrar
tk.Button(
    frame_registros,
    text="Registrar Residuos",
    command=registrar_residuo,
    bg="#2980b9",
    fg="white",
    font=("Arial", 11, "bold")
).pack(pady=10)

# Tabla
tabla = ttk.Treeview(
    frame_registros,
    columns=("ID", "Ruta", "Cantidad", "Fecha"),
    show="headings",
    height=12
)

tabla.heading("ID", text="ID")
tabla.heading("Ruta", text="Ruta")
tabla.heading("Cantidad", text="Cantidad")
tabla.heading("Fecha", text="Fecha")

tabla.column("ID", width=50, anchor="center")
tabla.column("Ruta", width=250, anchor="center")
tabla.column("Cantidad", width=150, anchor="center")
tabla.column("Fecha", width=150, anchor="center")

tabla.pack(
    pady=15,
    fill="x"
)

# Botón eliminar
tk.Button(
    frame_registros,
    text="Eliminar Registro",
    command=eliminar_registro,
    bg="#c0392b",
    fg="white",
    font=("Arial", 11, "bold")
).pack(pady=5)

# =====================================================
# BOTONES SIDEBAR
# =====================================================

tk.Button(
    sidebar,
    text="Inicio",
    fg="white",
    bg="#34495e",
    font=("Arial", 11, "bold"),
    command=lambda:
    cambiar_vista(frame_inicio)
).pack(fill="x", pady=5)

tk.Button(
    sidebar,
    text="Gestión de Rutas",
    fg="white",
    bg="#34495e",
    font=("Arial", 11, "bold"),
    command=lambda:
    cambiar_vista(frame_rutas)
).pack(fill="x", pady=5)

tk.Button(
    sidebar,
    text="Registro de Residuos",
    fg="white",
    bg="#34495e",
    font=("Arial", 11, "bold"),
    command=lambda:
    cambiar_vista(frame_registros)
).pack(fill="x", pady=5)

# =====================================================
# INICIALIZACIÓN
# =====================================================

cargar_rutas()

mostrar_registros()

actualizar_dashboard()

cambiar_vista(frame_inicio)

# =====================================================
# EJECUTAR
# =====================================================

ventana.mainloop()

# =====================================================
# CERRAR BASE DE DATOS
# =====================================================

conexion.close()