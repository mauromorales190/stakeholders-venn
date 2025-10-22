from flask import Flask, request, send_file, jsonify
from matplotlib_venn import venn3, venn3_circles
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

@app.route('/stakeholder-venn', methods=['POST'])
def generate_stakeholder_venn():
    try:
        data = request.json
        categorias = data['categorias']
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Crear diagrama de Venn
        v = venn3(
            subsets=(
                len(categorias['inactivo']),
                len(categorias['discrecional']),
                len(categorias['dominante']),
                len(categorias['demandante']),
                len(categorias['peligroso']),
                len(categorias['dependiente']),
                len(categorias['criticos'])
            ),
            set_labels=('Poder', 'Legitimidad', 'Urgencia'),
            set_colors=('#ffcccc', '#ffcccc', '#ffcccc'),
            alpha=0.5
        )
        
        # Configurar bordes rojos
        venn3_circles(
            subsets=(
                len(categorias['inactivo']),
                len(categorias['discrecional']),
                len(categorias['dominante']),
                len(categorias['demandante']),
                len(categorias['peligroso']),
                len(categorias['dependiente']),
                len(categorias['criticos'])
            ),
            linewidth=2.5,
            linestyle='solid',
            color='darkred'
        )
        
        # Función para formatear nombres
        def format_names(names, max_names=8):
            if len(names) == 0:
                return ''
            if len(names) <= max_names:
                return '\n'.join(names)
            shown = '\n'.join(names[:max_names])
            return f"{shown}\n(+{len(names) - max_names} más)"
        
        # Añadir stakeholders en cada segmento
        segments = {
            '100': ('1', categorias['inactivo']),
            '010': ('2', categorias['discrecional']),
            '001': ('3', categorias['demandante']),
            '110': ('4', categorias['dominante']),
            '101': ('5', categorias['peligroso']),
            '011': ('6', categorias['dependiente']),
            '111': ('7', categorias['criticos'])
        }
        
        for segment_id, (num, names) in segments.items():
            label_obj = v.get_label_by_id(segment_id)
            if label_obj and len(names) > 0:
                text = f"{num}\n{format_names(names, 6)}"
                label_obj.set_text(text)
                label_obj.set_fontsize(9)
                label_obj.set_fontweight('bold')
            elif label_obj:
                label_obj.set_text(num)
                label_obj.set_fontsize(12)
                label_obj.set_fontweight('bold')
        
        # Colorear segmentos
        for patch_id in ['100', '010', '001', '110', '101', '011', '111']:
            patch = v.get_patch_by_id(patch_id)
            if patch:
                patch.set_color('#ffe6e6')
        
        # Añadir leyenda
        legend_text = (
            "Categorías:\n"
            "1: Inactivo - baja\n"
            "2: Discrecional - baja\n"
            "3: Demandante - baja\n"
            "4: Dominante - media\n"
            "5: Peligroso - media\n"
            "6: Dependiente - media\n"
            "7: Críticos - alta"
        )
        
        plt.text(1.3, 0.5, legend_text, 
                fontsize=11, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
                verticalalignment='center')
        
        plt.title('Análisis de Preponderancia de Stakeholders', 
                 fontsize=16, fontweight='bold', pad=20)
        
        # Guardar imagen
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Servicio activo',
        'endpoint': '/stakeholder-venn',
        'method': 'POST'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
