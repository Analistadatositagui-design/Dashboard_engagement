import pandas as pd
import json
import numpy as np

# Mapeo de preguntas a dimensiones
Q2DIM = {
    'Me siento orgulloso(a) de trabajar en la compañía': 'Orgullo & Compromiso',
    'Me siento motivado(a) a buscar mejores formas de hacer las cosas': 'Orgullo & Compromiso',
    'Tengo impacto directo en el logro de mis objetivos': 'Orgullo & Compromiso',
    'Tengo la intención de permanecer en mi empresa durante al menos los próximos 12 meses': 'Orgullo & Compromiso',
    'Me siento reconocido(a) por mi trabajo': 'Reconocimiento',
    'Considero que existe una cultura de reconocimiento entre mi equipo, compañeros y líder': 'Reconocimiento',
    'Tengo suficientes oportunidades para aprender nuevas habilidades y crecer como profesional': 'Desarrollo Profesional',
    'Mi jefe directo me proporciona retroalimentación periódica que me ayuda a desarrollarme': 'Desarrollo Profesional',
    'Mi jefe inmediato crea un entorno seguro donde puedo expresar mis ideas libremente y con respeto': 'Liderazgo',
    'Recomendaría a mi jefe directo a otras personas': 'Liderazgo',
    'Mi jefe directo vive los 10 principios de la compañía en todo momento': 'Liderazgo',
    'Todos los empleados, independientemente de sus diferencias, reciben un trato justo': 'Cultura e Inclusión',
    'Puedo ser yo mismo(a) en el trabajo': 'Cultura e Inclusión',
    'Puedo denunciar prácticas poco éticas sin temor a represalias': 'Cultura e Inclusión',
    'La comunicación en mi empresa es abierta y transparente, con diálogo bidireccional': 'Comunicación',
    'Los líderes de mi empresa comunican claramente el propósito y los objetivos a largo plazo': 'Comunicación',
    'Estoy satisfecho(a) con la compañía como lugar de trabajo': 'Satisfacción & eNPS',
    'Recomendaría mi empresa como un excelente lugar para trabajar': 'Satisfacción & eNPS',
    'El personal de Logística del Centro de Distribución sigue todas las reglas y procedimientos de seguridad': 'Seguridad & Recursos',
    'Cuenta con todos los recursos necesarios (ejem: capacitación, EPP´s, tiempo,etc) para realizar el trabajo': 'Seguridad & Recursos',
    'Mi jefe directo refuerza el uso de prácticas de trabajo seguro': 'Seguridad & Recursos',
    'Considera que este es un lugar seguro para trabajar': 'Seguridad & Recursos'
}

DIMS = list(set(Q2DIM.values()))
QCOLS = list(Q2DIM.keys())
QSHORT = [
    'Orgullo en la compañía', 'Motivación / Mejora', 'Impacto en objetivos', 'Intención permanencia',
    'Reconocimiento personal', 'Cultura de reconocimiento',
    'Oportunidades aprendizaje', 'Retroalimentación líder',
    'Entorno seguro / ideas', 'Recomendaría al jefe', 'Jefe vive los 10 principios',
    'Trato justo / inclusión', 'Autenticidad en trabajo', 'Denuncia sin represalias',
    'Comunicación abierta', 'Líderes comunican propósito',
    'Satisfacción general', 'Recomendaría empresa (eNPS)',
    'Seguridad / procedimientos', 'Recursos disponibles', 'Jefe refuerza seguridad', 'Lugar seguro'
]

THR = 80  # Umbral para apto (8 de 10)

def normalize_json(obj):
    """Convertir tipos numpy a tipos nativos de Python"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: normalize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_json(v) for v in obj]
    return obj

def normalize_score(val):
    """Normalizar valor 1-10 a 0-100"""
    if pd.isna(val):
        return np.nan
    return (val / 10.0) * 100

def process_excel_to_js(excel_path, output_js_path):
    df = pd.read_excel(excel_path)
    
    # Las respuestas están en las columnas sin "Puntos:"
    # Convertir 1-10 a 0-100
    norm_data = {}
    for q in QCOLS:
        if q in df.columns:
            norm_data[f'__{q}__norm'] = df[q].apply(normalize_score)
    
    # Agregar columnas normalizadas
    norm_df = pd.DataFrame(norm_data)
    df = pd.concat([df, norm_df], axis=1)
    
    # Calcular total normalizado
    norm_cols = list(norm_df.columns)
    df['score_total'] = df[norm_cols].mean(axis=1)
    
    # Filtrar filas con al menos una respuesta
    df = df.dropna(subset=['score_total'])
    
    region_col = '¿A qué regional pertenece?'
    operator_col = '¿A qué operador pertenece?'
    
    def get_dc(row):
        """Extraer DC del valor de región"""
        for region in ['Norte', 'Andes', 'Centro', 'Sur']:
            if region in df.columns and pd.notna(row.get(region)):
                return row[region]
        return 'Desconocido'
    
    def get_cargo(row):
        """Extraer cargo"""
        if pd.notna(row.get('Transporte')):
            return row['Transporte']
        elif pd.notna(row.get('Almacén')):
            return row['Almacén']
        return 'Otro'
    
    df['DC'] = df.apply(get_dc, axis=1)
    df['Cargo'] = df.apply(get_cargo, axis=1)
    
    def calc_stats(scores):
        """Calcular avg, fav, apto, reforzar desde scores 0-100"""
        if len(scores) == 0:
            return {'avg': 0, 'fav': 0, 'n': 0, 'apto': 0, 'reforzar': 0}
        scores = scores.dropna()
        if len(scores) == 0:
            return {'avg': 0, 'fav': 0, 'n': 0, 'apto': 0, 'reforzar': 0}
        avg = float(scores.mean())
        fav = float((scores >= THR).sum() / len(scores) * 100)
        n = int(len(scores))
        apto = int((scores >= THR).sum())
        reforzar = n - apto
        return {'avg': avg, 'fav': fav, 'n': n, 'apto': apto, 'reforzar': reforzar}
    
    # GLB
    glb_scores = df['score_total'].dropna()
    glb = calc_stats(glb_scores)
    
    # Regional
    regional = {}
    for region in ['Norte', 'Andes', 'Centro', 'Sur']:
        if region in df.columns:
            r_df = df[df[region].notna()]
            if len(r_df) > 0:
                r_scores = r_df['score_total'].dropna()
                if len(r_scores) > 0:
                    regional[region] = calc_stats(r_scores)
    
    glb['regional'] = regional
    glb['moe'] = 1.7  # Margen de error
    
    # Global dimensions
    glb_dims = {}
    for dim in DIMS:
        dim_qs = [q for q, d in Q2DIM.items() if d == dim and f'__{q}__norm' in df.columns]
        if dim_qs:
            all_scores = []
            for q in dim_qs:
                col = f'__{q}__norm'
                all_scores.extend(df[col].dropna().values.tolist())
            if all_scores:
                arr = np.array(all_scores)
                glb_dims[dim] = {
                    'avg': float(arr.mean()),
                    'fav': float((arr >= THR).sum() / len(arr) * 100)
                }
    glb['dims'] = glb_dims
    
    # Global questions
    glb_questions = {}
    for q in QCOLS:
        norm_col = f'__{q}__norm'
        if norm_col in df.columns:
            q_scores = df[norm_col].dropna()
            if len(q_scores) > 0:
                glb_questions[q] = {
                    'avg': float(q_scores.mean()),
                    'fav': float((q_scores >= THR).sum() / len(q_scores) * 100)
                }
    glb['questions'] = glb_questions
    
    # Global operators
    operator_col = '¿A qué operador pertenece?'
    glb_operators = {}
    for op, op_group in df.groupby(operator_col):
        if pd.notna(op):
            op_scores = op_group['score_total'].dropna()
            if len(op_scores) > 0:
                glb_operators[op] = {
                    'n': int(len(op_scores)),
                    'avg': float(op_scores.mean())
                }
    glb['operators'] = glb_operators
    
    # Global cargos
    glb_cargos = {}
    for cargo, c_group in df.groupby('Cargo'):
        if pd.notna(cargo):
            c_scores = c_group['score_total'].dropna()
            glb_cargos[cargo] = calc_stats(c_scores)
    glb['cargos'] = glb_cargos
    
    # DCS
    dcs = {}
    for dc, dc_group in df.groupby('DC'):
        if pd.isna(dc) or dc == 'Desconocido':
            continue
        
        dc_scores = dc_group['score_total'].dropna()
        stats = calc_stats(dc_scores)
        region = dc_group[region_col].mode()[0] if len(dc_group[region_col].mode()) > 0 else 'Desconocido'
        operator = dc_group[operator_col].mode()[0] if len(dc_group[operator_col].mode()) > 0 else 'Operador'
        
        # Dimensiones
        dims = {}
        for dim in DIMS:
            dim_qs = [q for q, d in Q2DIM.items() if d == dim and f'__{q}__norm' in df.columns]
            if dim_qs:
                dim_scores_list = []
                for q in dim_qs:
                    col = f'__{q}__norm'
                    dim_scores_list.extend(dc_group[col].dropna().values.tolist())
                if dim_scores_list:
                    dim_scores = np.array(dim_scores_list)
                    dims[dim] = {
                        'avg': float(dim_scores.mean()),
                        'fav': float((dim_scores >= THR).sum() / len(dim_scores) * 100)
                    }
        
        # Questions
        questions = {}
        for i, q in enumerate(QCOLS):
            norm_col = f'__{q}__norm'
            if norm_col in dc_group.columns:
                q_scores = dc_group[norm_col].dropna()
                if len(q_scores) > 0:
                    questions[q] = {
                        'avg': float(q_scores.mean()),
                        'fav': float((q_scores >= THR).sum() / len(q_scores) * 100)
                    }
        
        # Operators
        operators = {operator: {'n': stats['n'], 'avg': stats['avg']}}
        
        # Cargos
        cargos = {}
        for cargo, c_group in dc_group.groupby('Cargo'):
            if pd.notna(cargo):
                c_scores = c_group['score_total'].dropna()
                cargos[cargo] = calc_stats(c_scores)
        
        # Cargo questions — compute per-cargo question stats
        cargo_questions = {}
        for cargo, c_group in dc_group.groupby('Cargo'):
            if pd.notna(cargo):
                cq = {}
                for i, q in enumerate(QCOLS):
                    norm_col = f'__{q}__norm'
                    if norm_col in c_group.columns:
                        q_scores = c_group[norm_col].dropna()
                        if len(q_scores) > 0:
                            cq[q] = {
                                'avg': float(q_scores.mean()),
                                'fav': float((q_scores >= THR).sum() / len(q_scores) * 100)
                            }
                cargo_questions[cargo] = cq
        
        dcs[dc] = {
            'region': region,
            **stats,
            'dims': dims,
            'questions': questions,
            'operators': operators,
            'cargos': cargos,
            'cargo_questions': cargo_questions
        }
    
    # Generar JS con estructura DATA
    data_obj = {
        'global': glb,
        'dcs': dcs,
        'dims': DIMS,
        'qcols': QCOLS,
        'qshort': QSHORT,
        'q2dim': Q2DIM,
        'threshold': THR
    }
    
    # Convertir tipos numpy
    data_obj = normalize_json(data_obj)
    
    js_code = f"""const DATA = {json.dumps(data_obj, indent=2, ensure_ascii=False)};
const DIMS   = DATA.dims;
const QCOLS  = DATA.qcols;
const QSHORT = DATA.qshort;
const Q2DIM  = DATA.q2dim;
const GLB    = DATA.global;
const DCS    = DATA.dcs;
const THR    = DATA.threshold;
"""
    
    with open(output_js_path, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"✓ Datos generados exitosamente")
    print(f"  - Respondentes globales: {int(glb['n'])}")
    print(f"  - Score promedio: {glb['avg']:.1f}%")
    print(f"  - Centros de distribución: {len(dcs)}")


if __name__ == "__main__":
    excel_path = "Encuesta Engagement Data.xlsx"
    output_js_path = "data.js"
    process_excel_to_js(excel_path, output_js_path)