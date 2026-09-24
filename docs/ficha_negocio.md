# Espumas Cotopaxi — Ficha de Negocio (Ficticio)

*Fábrica de espumas de poliuretano industrial B2B — documento de referencia para proyecto de portafolio*

---

## 1\. Perfil de Cliente Ideal (ICP)

| Segmento | Cantidad de compra (peso) | Tipo de empresa compradora | Industria | Frecuencia típica |
| :---- | :---- | :---- | :---- | :---- |
| **Cliente Alto** | 30–40 toneladas | Fabricante mediano-grande con planta propia | Muebles, colchones, automotriz (Tier 1/2) | Recurrente, contrato o pedido mensual |
| **Cliente Mediano** | 15–20 toneladas | Fabricante pequeño-mediano o distribuidor regional | Muebles, tapicería, colchonería regional | Recurrente, pedido bimensual/trimestral |
| **Cliente Bajo** | \< 2 toneladas | Taller artesanal, tapicero independiente, constructora pequeña | Tapicería local, remodelación, aislamiento puntual | Esporádico, pedido spot |

**Características comunes del comprador B2B:**

- Empresa con planta de producción o taller de transformación (no consumidor final).  
- Decisor de compra: Jefe de Compras o Gerente de Producción (empresas medianas/grandes) o el propio dueño (talleres pequeños).  
- Sensible a: consistencia de densidad/dureza entre lotes, tiempo de entrega, condiciones de crédito.  
- Ciclo de venta: corto en clientes bajos (días), más largo en clientes altos (semanas, por homologación de material).

> **Nota de terminología:** se usa "Cantidad de compra" y no "Volumen de compra", porque comercialmente la espuma se mide y se factura por **peso** (kg / toneladas), no por volumen. El volumen es solo un paso intermedio del cálculo (ver sección 4).

---

## 2\. Sub-líneas de Producto (4)

| Sub-línea | Uso principal | Densidades que maneja | Nota técnica |
| :---- | :---- | :---- | :---- |
| **Cotopaxi Confort** | Muebles y tapicería | D25, D28, D30 | Balance entre suavidad y resiliencia; espuma flexible convencional |
| **Cotopaxi Dormo** | Colchonería | D30, D36, D40 | Mayor densidad para durabilidad y soporte; menor fatiga del material en uso continuo (8h/día) |
| **Cotopaxi Auto** | Automotriz (asientos, paneles) | D36, D40 | Requiere mayor resistencia a compresión y estabilidad dimensional por exigencias de homologación del cliente |
| **Cotopaxi Acústica** | Aislamiento acústico | D18 | Espuma de celda abierta, prioriza absorción de sonido sobre soporte estructural |

*(D30 es compartida entre Confort y Dormo; D36 y D40 son compartidas entre Dormo y Auto — un mismo nivel de densidad puede servir a más de un uso final.)*

*(Nota: se descarta la línea de esponjas para lavavajillas del alcance del proyecto — es un proceso y mercado de consumo masivo/retail, distinto al perfil B2B industrial que define este ICP.)*

---

## 3\. Zonas de Venta (4)

| Zona | País | Rol en el negocio simulado |
| :---- | :---- | :---- |
| **Quito** | Ecuador | Zona matriz — mayor concentración de fabricantes de muebles y colchones |
| **Cuenca** | Ecuador | Zona secundaria — clúster artesanal/tapicero, tickets más más altos y de lujo |
| **Lima** | Perú | Expansión regional — mercado automotriz y colchonería industrial |
| **Barranquilla** | Colombia | Expansión regional — acceso a industria de aislamiento por corredor caribeño |

---

## 4\. Lógica de Conversión: Plancha → Peso → Precio

Las espumas se venden en **planchas** de superficie fija y espesor variable, no en unidades de volumen o peso directamente pedidas por el cliente.

**Dimensiones de plancha:**

- Largo × Ancho fijos: **100 cm × 200 cm**  
- Espesor variable: **1 a 20 cm**, según pedido

**Fórmulas de conversión (uso interno):**

1. Volumen de la plancha (m³) \= Largo (m) × Ancho (m) × Espesor (m)  
2. Peso de la plancha (kg) \= Volumen (m³) × Densidad (kg/m³)  
3. Peso total de la línea de pedido (kg) \= Peso por plancha × N.° de planchas  
4. Peso total del pedido (ton) \= Suma de todas las líneas de pedido ÷ 1000

**Ejemplo de verificación** (10 planchas de 100×200×10 cm, D18):

- Volumen \= 1,00 m × 2,00 m × 0,10 m \= 0,2 m³  
- Peso por plancha \= 0,2 m³ × 18 kg/m³ \= 3,6 kg  
- Peso total \= 3,6 kg × 10 planchas \= 36 kg  
- Al cliente se le comunica el precio de dos maneras: 1 plancha de D18 100x200x10 cm le cuesta $3,60 o las 10 planchas por $36,00.

**Tres capas de lenguaje para el mismo pedido:**

| Capa | Audiencia | Unidad |
| :---- | :---- | :---- |
| Operativa/técnica | Producción / planta | Planchas (dimensión \+ espesor \+ densidad) |
| Interna de negocio | Gerencia / ventas (vs. presupuesto y capacidad) | Peso (kg → toneladas) |
| Comercial | Cliente final | Precio (USD) |

El peso es siempre un paso de cálculo interno; al cliente se le comunica únicamente el **precio en USD**, nunca el peso o el volumen — el lenguaje se adapta a alguien que no necesariamente entiende términos técnicos de espumas.

---

## 5\. Precio de Referencia por Densidad (simulado)

Precio por kg, con tendencia lineal inversa a la densidad (a menor densidad, mayor costo de fabricación por kg — más químico reactivo por unidad de peso; a mayor densidad, menor precio por kg, aunque el precio total de la plancha sí es mayor por el mayor peso).

| Densidad (kg/m³) | Precio por kg (USD) |
| :---- | :---- |
| D18 | 4.22 |
| D25 | 3.96 |
| D28 | 3.85 |
| D30 | 3.77 |
| D36 | 3.55 |
| D40 | 3.40 |

**Fórmula usada:** Precio/kg \= 4.22 − 0.03727 × (Densidad − 18), donde 0.03727 \= (4.22 − 3.40) / (40 − 18\)

**Ejemplo completo** (10 planchas de 100×200×10 cm, D18):

- Peso total \= 36 kg (ver sección 4\)  
- Precio total \= 36 kg × 4.22 USD/kg \= **151.92 USD**

---

**Uso de este documento:** referencia fija para crear Empresas, Contactos y Negocios en HubSpot en los siguientes pasos del proyecto. Todos los nombres de empresas, contactos y cifras que se generen de aquí en adelante serán ficticios y deben ser consistentes con esta ficha.

&nbsp;