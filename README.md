# 📊 Dashboard de Engagement - Actualización de Datos desde Excel

## 🎯 Cómo Funciona

El dashboard ahora se alimenta **dinámicamente** desde un Excel. El proceso es:

```
Excel → Python → data.js → HTML Dashboard
```

### Archivos Clave:
- **`Encuesta Engagement Data.xlsx`** - Fuente de datos (respuestas de la encuesta)
- **`process_excel.py`** - Script que procesa el Excel y genera `data.js`
- **`data.js`** - Datos en formato JavaScript (generado automáticamente)
- **`engagement prueba.html`** - Dashboard que carga `data.js`

---

## 🔄 Cómo Actualizar los Dashboards

### Opción 1: Actualización Manual (Recomendado)

1. **Actualiza el Excel** con nuevas respuestas:
   - Abre `Encuesta Engagement Data.xlsx`
   - Verifica que tenga las columnas correctas (regionales, operadores, preguntas de 1-10)
   - Guarda

2. **Ejecuta el script de procesamiento**:
   ```bash
   python process_excel.py
   ```
   
   Esto genera/actualiza `data.js` automáticamente

3. **Abre el dashboard**:
   - Abre `engagement prueba.html` en el navegador
   - Los datos se cargarán automáticamente desde `data.js`
   - ¡Hecho!

### Opción 2: Automatización (Programación)

Puedes programar el script para que se ejecute automáticamente:

**Windows (Tareas Programadas):**
```batch
@echo off
cd /d "C:\Users\nicop\OneDrive\Escritorio\Dashboard para engagement"
python process_excel.py
REM Copiar a servidor si es necesario
REM copy data.js "\\servidor\compartida\"
```

---

## 📋 Estructura del Datos

### Excel Esperado
- **Columnas de región**: `¿A qué regional pertenece?`, `Norte`, `Andes`, `Centro`, `Sur`
- **Columnas de operador**: `¿A qué operador pertenece?`, `Transporte`, `Almacén`
- **Columnas de preguntas**: Respuestas 1-10 para cada pregunta (ej. "Me siento orgulloso...")
- **Filtros**: Se extraen automáticamente desde los valores únicos

### Mapeo de Preguntas → Dimensiones
```javascript
{
  "Me siento orgulloso(a) de trabajar en la compañía": "Orgullo & Compromiso",
  "Me siento motivado(a) a buscar mejores formas de hacer las cosas": "Orgullo & Compromiso",
  "Tengo impacto directo en el logro de mis objetivos": "Orgullo & Compromiso",
  // ... más preguntas
}
```

---

## 📊 Datos Generados

El script calcula automáticamente:

- **Por DC (Centro de Distribución)**:
  - N (muestra), Avg (score promedio), Fav (tasa favorable)
  - Apto/Reforzar (clasificación)
  - Scores por dimensión
  - Scores por pregunta
  - Desglose por cargo

- **Regional**:
  - Totales por región (Norte, Andes, Centro, Sur)

- **Global**:
  - Totales generales
  - Margen de error ±1.7% (IC 95%)

---

## 🛠️ Personalización

### Cambiar Umbral (Threshold)
En `process_excel.py`, línea ~37:
```python
THR = 80  # 80% = 8 de 10
```

### Cambiar Mapeo de Preguntas
En `process_excel.py`, línea ~7-28, actualiza el diccionario `Q2DIM`

### Agregar/Eliminar Preguntas
1. Actualiza `Q2DIM`
2. Actualiza `QSHORT` con abreviaturas
3. Ejecuta `python process_excel.py`

---

## ✅ Verificación

Después de ejecutar el script, verifica:

```bash
# Debería mostrar algo como:
# ✓ Datos generados exitosamente
#   - Respondentes globales: 4152
#   - Score promedio: 89.2%
#   - Centros de distribución: 43
```

Si el HTML se carga pero el dashboard está vacío, verifica:
1. `data.js` existe en la misma carpeta que el HTML
2. Abre la consola del navegador (F12) para errores
3. Verifica que `data.js` tenga contenido válido

---

## 📝 Notas Técnicas

### Cálculos
- **Avg (Average)**: Promedio normalizado de 0-100
- **Fav (Favorable)**: % de respuestas ≥ 80/100
- **Apto**: Personas con score ≥ 80%
- **Reforzar**: Personas con score < 80%
- **Promedios ponderados**: Calculados por N (tamaño del grupo)

### Archivos Generados
- `data.js`: ~50-100 KB (variable según número de respuestas)
- HTML final después de actualización: ~600 KB (comprimido del 656 KB original)

---

## 🔗 Integración Futura

Si deseas:
- **API**: Exponer los datos en JSON desde un servidor
- **Base de datos**: Guardar en SQL/PostgreSQL
- **Auto-refresh**: Que el dashboard se actualice automáticamente
- **Reportes**: Generar PDFs automáticos

Avísame y lo configuramos 👍
