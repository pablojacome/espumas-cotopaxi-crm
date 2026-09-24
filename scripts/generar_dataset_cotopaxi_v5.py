"""
Generador de dataset sintético — Espumas Cotopaxi (negocio ficticio B2B) — v5
v2 corrigió: empresas duplicadas, contactos inconsistentes, segmento
inconsistente, y agregó coherencia cruzada entre los 3 CSV (Contacto
asociado por email).
v3: "Propietario del negocio" ahora es SIEMPRE Pablo Jacome (único usuario
real de la cuenta gratuita de HubSpot). Se agrega "Vendedor asignado
(referencia interna)" con 10 personas (9 aleatorias + Pablo Jacome).
v5 corrige: (1) Segmento de cliente y Sub-línea de producto ahora también
viven en Empresas (antes solo estaban en Negocios, y son atributos del
cliente, no del pedido); (2) la Fecha de cierre ESPERADA de un negocio
abierto siempre queda en el futuro respecto a HOY (decisión confirmada:
sin automatización en el plan gratuito, un negocio vencido sin actualizar
no se corrige solo); (3) N.° de planchas y Espesor (cm) ya NO se exportan
a Negocios — quedan solo como variables internas de cálculo en Python,
porque son capa operativa/técnica de Producción, no propiedades de Ventas.

Modelo de datos correcto:
- Empresa: entidad ÚNICA. Nombre, Dominio, Industria, Ciudad, País, Sub-línea
  y Segmento quedan fijos para siempre (son atributos del cliente).
- Contacto: UNO solo por Empresa (mismo decisor para todas sus compras).
- Negocio: VARIOS por Empresa (una fila por cada compra/pedido). Densidad,
  Peso, Precio, Etapa y fechas SÍ varían pedido a pedido. Vendedor asignado
  y Fuente del negocio se fijan por empresa (un cliente tiene un solo
  encargado de cuenta y un solo canal de adquisición original). Propietario
  del negocio es constante en todo el dataset.
"""

import random
import unicodedata
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

HOY = datetime(2026, 9, 14)

# ---------------------------------------------------------------------------
# 1. Reglas de negocio fijas (de la ficha)
# ---------------------------------------------------------------------------

DENSIDADES_POR_SUBLINEA = {
    "Confort": [25, 28, 30],
    "Dormo": [30, 36, 40],
    "Auto": [36, 40],
    "Acústica": [18],
}
PRECIO_POR_KG = {18: 4.22, 25: 3.96, 28: 3.85, 30: 3.77, 36: 3.55, 40: 3.40}
ZONA_PAIS = {"Quito": "Ecuador", "Cuenca": "Ecuador", "Lima": "Perú", "Barranquilla": "Colombia"}
INDUSTRIA_POR_SUBLINEA = {
    "Confort": ["Muebles", "Tapicería"],
    "Dormo": ["Colchonería"],
    "Auto": ["Automotriz"],
    "Acústica": ["Construcción/Aislamiento"],
}
RANGO_KG_POR_SEGMENTO = {
    "Alto": (30000, 40000),
    "Mediano": (15000, 20000),
    "Bajo": (100, 2000),  # SUPUESTO: piso de 100 kg, la ficha solo da el techo (<2 ton)
}

# Confirmado por el usuario: pipeline personalizado de 6 etapas (no el default de HubSpot)
ETAPAS = ["Prospección", "Calificación", "Cotización Enviada", "Negociación",
          "Cerrado - Ganado", "Cerrado - Perdido"]

# ---------------------------------------------------------------------------
# 2. Cadencia de recompra por segmento — confirmado por el usuario
# ---------------------------------------------------------------------------

RANGO_NEGOCIOS_POR_SEGMENTO = {"Alto": (3, 6), "Mediano": (2, 4), "Bajo": (1, 1)}
PROB_BAJO_DOS_NEGOCIOS = 0.10  # "rara vez 2" -> 10% de las empresas Bajo tienen 2 en vez de 1

SEGMENTOS = ["Bajo", "Mediano", "Alto"]
PESO_SEGMENTOS = [0.45, 0.35, 0.20]

ZONAS = ["Quito", "Cuenca", "Lima", "Barranquilla"]
PESO_ZONAS = [0.35, 0.20, 0.25, 0.20]

# PROPIETARIO_HUBSPOT = único usuario real de la cuenta gratuita de HubSpot.
# Es el único valor que se puede importar de verdad al campo nativo "Propietario
# del negocio" (Deal Owner) sin crear correos ficticios que acepten invitación.
PROPIETARIO_HUBSPOT = "Pablo Jacome"

# VENDEDOR_ASIGNADO = columna de texto libre, NO nativa de HubSpot, solo para
# reportes internos de distribución. 10 personas: 9 aleatorias + Pablo Jacome
# (el mismo dueño de cuenta también lleva algunas empresas personalmente).
# Nombres y apellidos tomados de pools DISJUNTOS de los que usa Contactos
# (NOMBRES/APELLIDOS más abajo), para que nunca se confunda un vendedor
# interno con el contacto del cliente de una empresa.
VENDEDORES = [
    "Mariana Almeida", "Sebastián Fernández", "Renata Cevallos", "Iván Andrade",
    "Lucía Paredes", "Martín Cárdenas", "Ximena Salgado", "Gustavo Vega",
    "Beatriz Quintero", PROPIETARIO_HUBSPOT,
]
FUENTES = ["Referido", "Sitio web", "Feria comercial", "Llamada en frío"]
PESO_FUENTES = [0.35, 0.30, 0.20, 0.15]

# Etapa según antigüedad del pedido: uno reciente casi nunca está ya cerrado;
# uno de hace varios meses casi siempre ya se cerró (ganado o perdido).
UMBRAL_RECIENTE_DIAS = 45
PESOS_ETAPA_RECIENTE = [0.35, 0.25, 0.20, 0.12, 0.05, 0.03]
PESOS_ETAPA_ANTIGUO = [0.05, 0.10, 0.15, 0.15, 0.30, 0.25]

CARGOS_ALTO_MEDIANO = ["Jefe de Compras", "Gerente de Producción"]

# Pools ampliados (base x calificador) para evitar colisiones de nombre entre empresas
NOMBRES_EMPRESA = {
    "Muebles": (["Muebles", "Maderas", "Mobiliario"],
                ["Continental", "Real", "Moderno", "Clásico", "Premium", "Ejecutivo", "Nacional", "Total", "Estrella", "Prestige"]),
    "Tapicería": (["Tapicería", "Decoraciones", "Estilo"],
                  ["Fina", "Real", "Moderna", "Premium", "Clásica", "Ejecutiva", "Total", "Prestige", "Elegance", "Confort"]),
    "Colchonería": (["Colchones", "Descanso", "Sueño"],
                     ["Real", "Confort Plus", "Ideal", "Ejecutivo", "Premium", "Total", "Ámbar", "Estrella", "Relax", "Ensueño"]),
    "Automotriz": (["Autopartes", "Componentes", "Industrias"],
                    ["Continental", "Industrial", "Técnica", "Premium", "Nacional", "Total", "Prime", "Metalmecánica", "Confiable", "Central"]),
    "Construcción/Aislamiento": (["Aislamientos", "Construcciones", "Ingeniería"],
                                   ["Industrial", "Total", "Premium", "Nacional", "Continental", "Técnica", "Confiable", "Prime", "Estructural", "Central"]),
}
# NOTA: se eliminaron a propósito calificadores con carga geográfica (Quiteños,
# Lima, Barranquilla, del Pacífico, Costa Norte, del Caribe) porque generaban
# nombres incoherentes con la Zona real asignada a la empresa (ej. una empresa
# "Quiteños" terminando en Barranquilla). Todos los calificadores actuales son
# neutros y no chocan con ninguna de las 4 zonas.
SUFIJO_LEGAL = {"Ecuador": ["S.A.", "Cía. Ltda."], "Perú": ["S.A.C."], "Colombia": ["S.A.S."]}
NOMBRES = ["María", "José", "Carlos", "Ana", "Luis", "Gabriela", "Andrés", "Paola", "Diego", "Valeria",
           "Fernando", "Camila", "Jorge", "Daniela", "Ricardo", "Mónica", "Pablo", "Patricia", "Esteban", "Sofía"]
APELLIDOS = ["González", "Rodríguez", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Vargas",
             "Castro", "Ortiz", "Mendoza", "Chávez", "Silva", "Rojas", "Guerrero"]


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto.lower().replace(" ", "").replace(".", "").replace(",", "")


def lista_estratificada(etiquetas, pesos, total):
    """Reparte 'total' elementos EXACTAMENTE según 'pesos' (no por sorteo
    independiente), y baraja el orden. Con pocas empresas, un sorteo
    independiente por fila puede alejarse mucho del peso pedido (ej. terminar
    con más Mediano que Bajo); esto lo evita."""
    counts = [round(p * total) for p in pesos]
    diff = total - sum(counts)
    counts[counts.index(max(counts))] += diff  # ajusta el redondeo en la categoría mayor
    lista = []
    for etiqueta, c in zip(etiquetas, counts):
        lista.extend([etiqueta] * c)
    random.shuffle(lista)
    return lista


def generar_dataset(n_empresas: int, semilla: int):
    random.seed(semilla)
    np.random.seed(semilla)

    segmento_list = lista_estratificada(SEGMENTOS, PESO_SEGMENTOS, n_empresas)
    zona_list = lista_estratificada(ZONAS, PESO_ZONAS, n_empresas)

    empresas, contactos, negocios = [], [], []
    dominios_usados = set()
    nombres_completos_usados = set()
    nombres_base_usados = set()

    for idx in range(n_empresas):
        # --- Atributos FIJOS de la empresa (no cambian entre negocios) ---
        segmento = segmento_list[idx]
        sub_linea = random.choice(list(DENSIDADES_POR_SUBLINEA.keys()))
        industria = random.choice(INDUSTRIA_POR_SUBLINEA[sub_linea])
        zona = zona_list[idx]
        pais = ZONA_PAIS[zona]
        vendedor_cuenta = random.choice(VENDEDORES)
        fuente_cuenta = random.choices(FUENTES, weights=PESO_FUENTES)[0]

        bases, calificadores = NOMBRES_EMPRESA[industria]
        while True:
            nombre_base = f"{random.choice(bases)} {random.choice(calificadores)}"
            if nombre_base not in nombres_base_usados:
                nombres_base_usados.add(nombre_base)
                break
        sufijo = random.choice(SUFIJO_LEGAL[pais])
        nombre_empresa = f"{nombre_base} {sufijo}"

        dominio_base = slugify(nombre_base)
        dominio = f"{dominio_base}.com"
        contador = 1
        while dominio in dominios_usados:
            contador += 1
            dominio = f"{dominio_base}{contador}.com"
        dominios_usados.add(dominio)

        empresas.append({
            "Nombre de la empresa": nombre_empresa,
            "Dominio del sitio web": dominio,
            "Industria del cliente": industria,
            "Ciudad": zona,
            "País": pais,
            "Segmento de cliente": segmento,
            "Sub-línea de producto": sub_linea,
        })

        # --- Contacto ÚNICO para esta empresa (nombre completo no repetido entre empresas) ---
        nombre, apellido = random.choice(NOMBRES), random.choice(APELLIDOS)
        while f"{nombre} {apellido}" in nombres_completos_usados:
            nombre, apellido = random.choice(NOMBRES), random.choice(APELLIDOS)
        nombres_completos_usados.add(f"{nombre} {apellido}")
        email = f"{slugify(nombre)}.{slugify(apellido)}@{dominio}"
        cargo = "Dueño" if segmento == "Bajo" else random.choice(CARGOS_ALTO_MEDIANO)
        if pais == "Ecuador":
            telefono = f"+593 9{random.randint(10000000, 99999999)}"
        elif pais == "Perú":
            telefono = f"+51 9{random.randint(10000000, 99999999)}"
        else:
            telefono = f"+57 3{random.randint(100000000, 999999999)}"

        contactos.append({
            "Nombre": nombre, "Apellido": apellido, "Email": email,
            "Teléfono": telefono, "Cargo": cargo, "Empresa asociada": dominio,
        })

        # --- N.° de Negocios de esta empresa, según cadencia de recompra ---
        if segmento == "Bajo":
            n_negocios = 2 if random.random() < PROB_BAJO_DOS_NEGOCIOS else 1
        else:
            lo, hi = RANGO_NEGOCIOS_POR_SEGMENTO[segmento]
            n_negocios = random.randint(lo, hi)

        # --- Fechas de creación espaciadas a lo largo de los últimos 12 meses ---
        if n_negocios == 1:
            dias_atras_list = [random.randint(0, 365)]
        else:
            anclas = np.linspace(15, 365, n_negocios)
            dias_atras_list = [int(min(365, max(1, a + random.randint(-15, 15)))) for a in anclas]

        for dias_atras in dias_atras_list:
            fecha_creacion = HOY - timedelta(days=dias_atras)

            densidad = random.choice(DENSIDADES_POR_SUBLINEA[sub_linea])
            espesor_cm = random.randint(1, 20)
            volumen_m3 = 1.00 * 2.00 * (espesor_cm / 100)
            peso_por_plancha_kg = volumen_m3 * densidad
            peso_min, peso_max = RANGO_KG_POR_SEGMENTO[segmento]
            peso_objetivo_kg = random.uniform(peso_min, peso_max)
            n_planchas = max(1, round(peso_objetivo_kg / peso_por_plancha_kg))
            peso_total_kg = round(peso_por_plancha_kg * n_planchas, 2)
            precio_total_usd = round(peso_total_kg * PRECIO_POR_KG[densidad], 2)

            if dias_atras <= UMBRAL_RECIENTE_DIAS:
                etapa = random.choices(ETAPAS, weights=PESOS_ETAPA_RECIENTE)[0]
            else:
                etapa = random.choices(ETAPAS, weights=PESOS_ETAPA_ANTIGUO)[0]

            if etapa in ("Cerrado - Ganado", "Cerrado - Perdido"):
                max_offset = min(120, (HOY - fecha_creacion).days)
                fecha_cierre = fecha_creacion + timedelta(days=random.randint(10, max(10, max_offset)))
                fecha_cierre = min(fecha_cierre, HOY)
            else:
                # Fecha de cierre ESPERADA: siempre en el futuro respecto a HOY
                # (decisión confirmada por el usuario — evita 43 negocios abiertos
                # con fecha esperada ya vencida sin actualizar).
                fecha_cierre = HOY + timedelta(days=random.randint(15, 120))

            negocios.append({
                "Nombre del negocio": f"{nombre_empresa} — Pedido Cotopaxi {sub_linea} ({fecha_creacion:%b %Y})",
                "Segmento de cliente": segmento,
                "Sub-línea de producto": sub_linea,
                "Densidad (kg/m³)": densidad,
                # N.° de planchas y Espesor (cm) se calculan arriba pero NO se
                # exportan a Negocios: por decisión confirmada, son capa
                # operativa/técnica de Producción, no propiedades de HubSpot.
                # Quedan disponibles como espesor_cm / n_planchas si se
                # necesitan para otro análisis fuera de HubSpot.
                "Peso total (kg)": peso_total_kg,
                "Precio total (USD)": precio_total_usd,
                "Etapa del pipeline": etapa,
                "Propietario del negocio": PROPIETARIO_HUBSPOT,
                "Vendedor asignado (referencia interna)": vendedor_cuenta,
                "Fecha de creación": fecha_creacion.strftime("%Y-%m-%d"),
                "Fecha de cierre": fecha_cierre.strftime("%Y-%m-%d"),
                "Fuente del negocio": fuente_cuenta,
                "Empresa asociada": dominio,
                "Contacto asociado (email)": email,
            })

    return pd.DataFrame(empresas), pd.DataFrame(contactos), pd.DataFrame(negocios)


# ---------------------------------------------------------------------------
# 3. Buscar un N.° de empresas que deje el total de Negocios lo más cerca
#    posible de 125 (con ~2.45 negocios/empresa en promedio, esto ronda
#    las 50-52 empresas; se prueba un rango amplio y se toma la mejor)
# ---------------------------------------------------------------------------

TARGET_NEGOCIOS = 125
mejor = None  # (diferencia_absoluta, n_empresas, df_e, df_c, df_n)

for n_empresas in range(40, 66):
    df_e, df_c, df_n = generar_dataset(n_empresas, semilla=42)
    diff = abs(len(df_n) - TARGET_NEGOCIOS)
    if mejor is None or diff < mejor[0]:
        mejor = (diff, n_empresas, df_e, df_c, df_n)
    if diff == 0:
        break

_, n_empresas_final, df_empresas, df_contactos, df_negocios = mejor

df_empresas.to_csv("empresas_cotopaxi.csv", index=False, encoding="utf-8-sig")
df_contactos.to_csv("contactos_cotopaxi.csv", index=False, encoding="utf-8-sig")
df_negocios.to_csv("negocios_cotopaxi.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 4. Verificación
# ---------------------------------------------------------------------------

print("=== VERIFICACIÓN DE COHERENCIA CRUZADA ENTRE LOS 3 CSV ===\n")

print("¿Todo dominio de Negocios existe en Empresas?",
      set(df_negocios["Empresa asociada"]).issubset(set(df_empresas["Dominio del sitio web"])))
print("¿Todo dominio de Contactos existe en Empresas?",
      set(df_contactos["Empresa asociada"]).issubset(set(df_empresas["Dominio del sitio web"])))
print("¿Cada Empresa tiene exactamente 1 Contacto?",
      (df_contactos["Empresa asociada"].value_counts() == 1).all())

email_por_dominio = df_contactos.set_index("Empresa asociada")["Email"]
chk_email = df_negocios["Empresa asociada"].map(email_por_dominio) == df_negocios["Contacto asociado (email)"]
print("¿El email del Negocio siempre coincide con el Contacto real de esa Empresa?", chk_email.all())

nombre_por_dominio = df_empresas.set_index("Dominio del sitio web")["Nombre de la empresa"]
chk_nombre = df_negocios.apply(
    lambda r: nombre_por_dominio[r["Empresa asociada"]] in r["Nombre del negocio"], axis=1
)
print("¿El nombre de Empresa aparece correctamente en el Nombre del negocio?", chk_nombre.all())
print("¿Hay nombres de Empresa duplicados (base idéntica)?", df_empresas["Nombre de la empresa"].duplicated().any())

merge_seg = df_negocios.merge(df_empresas, left_on="Empresa asociada", right_on="Dominio del sitio web", suffixes=("_negocio", "_empresa"))
print("¿Segmento y Sub-línea de Negocios siempre coinciden con los de Empresas?",
      (merge_seg["Segmento de cliente_negocio"] == merge_seg["Segmento de cliente_empresa"]).all() and
      (merge_seg["Sub-línea de producto_negocio"] == merge_seg["Sub-línea de producto_empresa"]).all())

abiertos = ~df_negocios["Etapa del pipeline"].isin(["Cerrado - Ganado", "Cerrado - Perdido"])
vencidos = (pd.to_datetime(df_negocios.loc[abiertos, "Fecha de cierre"]) < HOY).sum()
print(f"¿Negocios abiertos con Fecha de cierre esperada ya vencida? {vencidos} de {abiertos.sum()}")
print()

print(f"Contactos: {len(df_contactos)}")
print(f"Negocios: {len(df_negocios)}\n")

print("--- Negocios por empresa (debe variar 1-6, según segmento) ---")
print(df_negocios.groupby("Empresa asociada").size().describe(), "\n")

print("--- Verificación de consistencia: 1 dominio = 1 nombre de empresa ---")
print("¿Duplicados?", df_empresas["Dominio del sitio web"].duplicated().any(), "\n")

print("--- Verificación: cada empresa tiene 1 solo Segmento en todos sus Negocios ---")
chk_segmento = df_negocios.groupby("Empresa asociada")["Segmento de cliente"].nunique()
print("¿Alguna empresa con >1 segmento?", (chk_segmento > 1).any(), "\n")

print("--- Verificación: cada empresa tiene 1 solo Vendedor asignado y 1 sola Fuente ---")
chk_vend = df_negocios.groupby("Empresa asociada")["Vendedor asignado (referencia interna)"].nunique()
chk_fuente = df_negocios.groupby("Empresa asociada")["Fuente del negocio"].nunique()
print("¿Alguna empresa con >1 Vendedor asignado?", (chk_vend > 1).any())
print("¿Alguna empresa con >1 fuente?", (chk_fuente > 1).any(), "\n")

print("--- Propietario del negocio (debe ser 100% Pablo Jacome, único usuario real de HubSpot) ---")
print(df_negocios["Propietario del negocio"].value_counts(), "\n")

print("--- Segmento a nivel EMPRESA (debe respetar 45/35/20 aprox.) ---")
seg_por_empresa = df_negocios.groupby("Empresa asociada")["Segmento de cliente"].first()
print(seg_por_empresa.value_counts(), "\n")

print("--- Segmento a nivel NEGOCIO (mezcla real del pipeline, no tiene por qué ser 45/35/20) ---")
print(df_negocios["Segmento de cliente"].value_counts(), "\n")

print("--- Etapa del pipeline ---")
print(df_negocios["Etapa del pipeline"].value_counts(), "\n")

print("--- Vendedor asignado (referencia interna) — a nivel de empresas, no de negocios ---")
print(df_empresas.assign(vendedor=df_negocios.groupby("Empresa asociada")["Vendedor asignado (referencia interna)"].first().values)["vendedor"].value_counts())
