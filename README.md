# README · Dashboard Muestras 2026

## Descripción

**Dashboard Muestras 2026** es una aplicación web interactiva desarrollada en HTML + JavaScript para analizar procesos de estampación a partir de archivos Excel (`.xlsx` / `.xls`).

El sistema permite visualizar indicadores operativos relacionados con:

* Muestras en proceso
* Distribución por tecnología y máquina
* Lead time promedio
* Pendientes por diseñador
* Indicadores de cumplimiento

El dashboard procesa automáticamente la información desde una hoja de cálculo y genera visualizaciones dinámicas utilizando Chart.js. 

---

# Características principales

## 1. Carga dinámica de archivos Excel

* Soporte para archivos:

  * `.xlsx`
  * `.xls`
* Drag & Drop
* Selector manual de archivos
* Validación automática de estructura

La hoja principal esperada debe llamarse:

```txt
2026
```

Si no existe, el sistema utilizará la primera hoja disponible. 

---

# Métricas y análisis incluidos

## Muestras en proceso

Visualiza:

* Total general
* Total digital
* Total convencional
* Distribución por máquina

### Máquinas digitales soportadas

* ATEXCO
* REGGIANI
* MIMAKI

### Máquinas convencionales soportadas

* ROTATIVA
* PLANA

---

## Lead Time Promedio

Calcula automáticamente:

```txt
Fecha entrega muestra - Fecha ingreso
```

Separado por:

* Tecnología digital
* Tecnología convencional

---

## Pendientes por diseñador

Identifica:

* Diseñadores con muestras sin fecha de entrega
* Cantidad de pendientes
* Ranking descendente

---

## Cumplimiento por diseñador

Calcula:

```txt
Cumplidas / Total
```

Criterio:

* Cumplida:

  * Fecha entrega <= Fecha trabajo
* Incumplida:

  * Fecha entrega > Fecha trabajo

Incluye:

* Cantidad cumplidas
* Cantidad incumplidas
* Total evaluado
* Porcentaje de cumplimiento
* Barra visual de progreso

---

# Estructura esperada del archivo Excel

El sistema busca automáticamente columnas similares a:

| Campo requerido | Ejemplo esperado |
| --------------- | ---------------- |
| Diseñador       | DISEÑADOR        |
| Tecnología      | TECNOLOGIA       |
| Máquina         | MAQUINA          |
| Estado muestra  | ESTADO MUESTRA   |
| Fecha ingreso   | FECHA INGRESO    |
| Fecha trabajo   | FECHA TRABAJO    |
| Fecha entrega   | FECHA ENTREGA    |
| Entrega muestra | ENTREGA MUESTRA  |

La detección es flexible y tolera:

* Mayúsculas/minúsculas
* Tildes
* Espacios
* Guiones bajos



---

# Tecnologías utilizadas

## Frontend

* HTML5
* CSS3
* JavaScript Vanilla

## Librerías externas

### SheetJS (XLSX)

Para lectura de archivos Excel:

```html
https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js
```

### Chart.js

Para visualización de gráficos:

```html
https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js
```



---

# Visualizaciones incluidas

## Gráficos Doughnut

* Distribución digital
* Distribución convencional

## Gráfico de barras

Comparativa total por máquina.

## Tarjetas KPI

Indicadores rápidos de producción y operación.

---

# Diseño UI/UX

El dashboard utiliza una estética tipo:

* Dark UI
* Industrial / Tech
* Dashboard premium
* Visualización minimalista

Características visuales:

* Tipografía Syne + DM Mono
* Sistema cromático segmentado por tecnología
* Overlay tipo grain texture
* Animaciones suaves
* Responsive Design



---

# Flujo de funcionamiento

## 1. Cargar archivo

El usuario arrastra o selecciona un archivo Excel.

## 2. Procesamiento

El sistema:

* Lee la hoja
* Detecta columnas
* Normaliza datos
* Calcula métricas

## 3. Render dinámico

Se generan:

* KPIs
* Tablas
* Gráficos
* Rankings

---

# Validaciones implementadas

## Validación de formato

Solo se aceptan:

```txt
.xlsx
.xls
```

## Validación de columnas

Si faltan columnas críticas:

```txt
No se encontraron las columnas...
```

## Validación de hoja vacía

```txt
La hoja está vacía.
```



---

# Funciones principales del código

| Función             | Descripción                      |
| ------------------- | -------------------------------- |
| `normalizar()`      | Limpia y estandariza texto       |
| `buscarCol()`       | Detecta columnas automáticamente |
| `toDate()`          | Convierte fechas Excel           |
| `promedio()`        | Calcula promedios                |
| `procesarDatos()`   | Procesamiento central            |
| `renderDashboard()` | Renderiza toda la interfaz       |
| `handleFile()`      | Maneja carga de archivos         |
| `resetDashboard()`  | Reinicia el sistema              |



---

# Compatibilidad

Compatible con:

* Google Chrome
* Microsoft Edge
* Safari
* Firefox

Recomendado:

* Resolución mínima: 1366px
* Uso desktop

---

# Posibles mejoras futuras

## Analítica avanzada

* Lead time por diseñador
* Lead time por máquina
* SLA por tecnología
* Tendencias históricas

## Filtros

* Por diseñador
* Por máquina
* Por estado
* Por rango de fechas

## Exportación

* PDF
* PNG
* Excel procesado

## Persistencia

* Base de datos
* Backend API
* Históricos automáticos

---

# Autor / Proyecto

Dashboard desarrollado para análisis operativo de muestras y procesos de estampación textil 2026. 
