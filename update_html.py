#!/usr/bin/env python3
"""Actualizar el HTML para usar data.js externo"""

import re

# Leer el HTML
with open('engagement prueba.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón: desde <!-- ═══ JAVASCRIPT ═══ --> hasta const THR    = DATA.threshold;
pattern = r'(<!-- ═══ JAVASCRIPT ═══ -->.*?const THR\s*=\s*DATA\.threshold;)'

replacement = '''<!-- ═══ JAVASCRIPT ═══ -->
<!-- Datos dinámicos desde Excel (generado por process_excel.py) -->
<script src="data.js"></script>

<script>
// ═══════════════════════════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════════════════════════
// Los datos se cargan desde data.js
// Variables disponibles: DATA, DIMS, QCOLS, QSHORT, Q2DIM, GLB, DCS, THR
const THR    = DATA.threshold;'''

# Reemplazar (DOTALL para que . coincida con saltos de línea)
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Verificar si se realizó el reemplazo
if new_content != content:
    # Guardar
    with open('engagement prueba.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ HTML actualizado correctamente")
    print("  - Removida la sección DATA embebida (656 KB)")
    print("  - Agregada referencia a data.js")
else:
    print("✗ No se encontró el patrón a reemplazar")
