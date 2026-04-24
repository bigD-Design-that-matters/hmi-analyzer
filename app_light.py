import streamlit as st
from openai import OpenAI
import base64
import os

# =========================
# CONFIGURACIÓN OPENAI
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="HMI Analyzer – 8 Puentes",
    layout="centered"
)

# =========================
# ESTILO BOTÓN
# =========================
st.markdown(
    """
    <style>
    /* Botón principal (Analizar HMI) */
    div.stButton > button {
        background-color: #1e88e5;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.6em 1.2em;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #1565c0;
        color: white;
    }

    /* CTA gris oscuro – Análisis en profundidad */
    a.cta-dark {
        display: block;
        text-align: center;
        background-color: #424242;
        color: white !important;
        padding: 0.6em 1.2em;
        border-radius: 6px;
        font-weight: 600;
        text-decoration: none;
    }

    a.cta-dark:hover {
        background-color: #2f2f2f;
        color: white !important;
    }

    /* CTA azul – Conocer el proyecto */
    a.cta-blue {
        display: block;
        text-align: center;
        background-color: #1e88e5;
        color: white !important;
        padding: 0.6em 1.2em;
        border-radius: 6px;
        font-weight: 600;
        text-decoration: none;
    }

    a.cta-blue:hover {
        background-color: #1565c0;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# CARGA DE ICONOS SVG
# =========================
def load_svg_icon(filename):
    base_dir = os.path.dirname(__file__)
    icon_path = os.path.join(base_dir, "icons", filename)
    with open(icon_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

icons = {
    "PUENTE 01 – ORIENTAR": load_svg_icon("puente_01_orientar.svg"),
    "PUENTE 02 – ENFOCAR": load_svg_icon("puente_02_enfocar.svg"),
    "PUENTE 03 – ADVERTIR": load_svg_icon("puente_03_advertir.svg"),
    "PUENTE 04 – ENTENDER": load_svg_icon("puente_04_entender.svg"),
    "PUENTE 05 – PROYECTAR": load_svg_icon("puente_05_proyectar.svg"),
    "PUENTE 06 – GUIAR": load_svg_icon("puente_06_guiar.svg"),
    "PUENTE 07 – ACCEDER": load_svg_icon("puente_07_acceder.svg"),
    "PUENTE 08 – APRENDER": load_svg_icon("puente_08_aprender.svg"),
}

# =========================
# HEADER (TÍTULO + LOGO)
# =========================
col_title, col_logo = st.columns([5, 1])

with col_title:
    st.title("HMI Analyzer")

    st.markdown(
        """
        <div style="font-size:32px; font-weight:600; line-height:1.3; margin-bottom:24px;">
            Evaluación cognitiva basada en los 8 puentes de
            <span style="font-weight:700;">The Cognitive Joint™</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_logo:
    st.image("logo.svg", width=90)

# =========================
# TEXTO INTRODUCTORIO
# =========================
st.markdown(
    "Sube una imagen de una interfaz HMI y obtén una evaluación clara, crítica y orientativa "
    "sobre la calidad de su diseño desde un punto de vista cognitivo y operativo."
)

# =========================
# BANNER HORIZONTAL (SVG)
# =========================
st.image("banner_hmi.svg", width=900)

# =========================
# UPLOAD DE IMAGEN
# =========================
uploaded_file = st.file_uploader(
    "Sube una imagen de tu HMI",
    type=["png", "jpg", "jpeg"]
)
st.markdown(
    """
    <div style="
        background-color:rgba(153,169,201,0.1);
        border-left:4px solid #1e88e5;
        padding:14px 16px;
        margin-top:10px;
        margin-bottom:10px;
        border-radius:6px;
        font-size:15px;
    ">
        🔒 <strong> Privacidad de los datos</strong><br>
        Las imágenes que se suben no son almacenadas por bigD.<br>
        Los resultados del análisis no se vinculan con el usuario registrado.
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="font-size:22px; font-weight:600; margin-top:20px; margin-bottom:10px;">
        Contexto de uso
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "Estos parámetros ajustan el nivel de exigencia del análisis según cómo se usa esta pantalla en la realidad."
)

# 1. CONTEXTO DE USO
contexto_uso = st.selectbox(
    "1. ¿Para qué se usa esta pantalla?",
    [
        "Operación normal (control del proceso en funcionamiento habitual)",
        "Mantenimiento o diagnóstico (revisar fallos, hacer ajustes o comprobar el sistema)",
        "Situación crítica (cuando hay riesgo, alarmas o necesidad de actuar rápido)"
    ]
)

# 2. CONSECUENCIAS
impacto_error = st.selectbox(
    "2. ¿Qué tipo de consecuencias están asociadas a esta pantalla?",
    [
        "Errores fácilmente corregibles (se pueden deshacer sin afectar al sistema)",
        "Errores que afectan a la operación (pueden provocar paradas, fallos o pérdida de producción)",
        "Errores con riesgo o impacto grave (pueden afectar a seguridad, personas o costes importantes)"
    ]
)
# =========================
# PREVIEW + BOTÓN
# =========================
if uploaded_file:
    st.image(uploaded_file, caption="HMI cargado", width=700)

    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    col_spacer, col_button = st.columns([3, 1])
    with col_button:
        analizar = st.button("Analizar HMI")

    # =========================
    # ANÁLISIS
    # =========================
    if analizar:
        with st.spinner("Analizando interfaz según los 8 Puentes Cognitivos..."):

            bridges = [
                ("PUENTE 01 – ORIENTAR", """
                El usuario debe entender rápidamente dónde está, qué está viendo y cómo se organiza el sistema.

                Evalúa si:
                - El estado del sistema es visible y claro
                - Existe estructura (overview → detalle)
                - La navegación es coherente y predecible
                
                Penaliza si:
                - No se entiende el contexto general
                - La información está desordenada o fragmentada
                - El usuario necesita interpretar demasiado
                """),
                ("PUENTE 02 – ENFOCAR", """
                La interfaz debe dirigir la atención hacia lo importante sin esfuerzo.
                
                Evalúa si:
                - Lo crítico destaca visualmente
                - Existe jerarquía clara (tamaño, color, posición)
                - El ruido visual está controlado
                
                Penaliza si:
                - Todo tiene el mismo peso visual
                - Hay exceso de información o elementos
                - Lo importante no destaca claramente
                """),
                ("PUENTE 03 – ADVERTIR", """
                Las anomalías deben detectarse de forma inmediata y sin ambigüedad.

                Evalúa si:
                - Las alertas son visibles y diferenciadas
                - Se indica gravedad y prioridad
                - Se sugiere o facilita acción
                
                Penaliza si:
                - Las alertas se confunden con información normal
                - No queda clara la gravedad
                - Hay exceso o ausencia de alertas
                """),
                ("PUENTE 04 – ENTENDER", """
                La interfaz debe ayudar a comprender qué está pasando y por qué.
                
                Evalúa si:
                - Se entienden relaciones causa–efecto
                - Los datos tienen contexto (rangos, límites, referencias)
                - La información permite interpretar la situación
                
                Penaliza si:
                - Solo hay datos sin contexto
                - No se entienden relaciones entre variables
                - Requiere conocimiento previo elevado
                """),
                ("PUENTE 05 – PROYECTAR", """
                La interfaz debe permitir anticipar el comportamiento del sistema.
                
                Evalúa si:
                - Hay tendencias o evolución temporal
                - Se pueden detectar problemas futuros
                - Se facilita una visión preventiva
                
                Penaliza si:
                - Solo muestra estado actual
                - No permite anticipar nada
                - Obliga a reaccionar en lugar de prever
                """),
                ("PUENTE 06 – GUIAR", """
                La interfaz debe indicar qué hacer y en qué orden.
                
                Evalúa si:
                - Las acciones están estructuradas en pasos claros
                - Se reduce la incertidumbre del usuario
                - Hay ayuda contextual o instrucciones
                
                Penaliza si:
                - El usuario tiene que decidir sin guía
                - No hay secuencia clara
                - No se previenen errores
                """),
                ("PUENTE 07 – ACCEDER", """
                La interacción debe ser fácil, rápida y segura en condiciones reales.
                
                Evalúa si:
                - Los controles son accesibles y usables
                - Hay buen tamaño, posición y feedback
                - Se previenen errores de interacción
                
                Penaliza si:
                - Botones pequeños o mal ubicados
                - Riesgo de error en acciones
                - Mala ergonomía digital
                """),
                (""PUENTE 08 – APRENDER", """
                La interfaz debe facilitar el aprendizaje y mejora continua.

                Evalúa si:
                - Hay acceso a histórico o datos pasados
                - Se pueden identificar patrones
                - El sistema ayuda a evitar errores futuros

                Penaliza si:
                - No hay memoria del sistema
                - No se aprende del uso
                - Falta transparencia
                """)
            ]

            scores = []
            global_inputs = []

            contexto_estructurado = f"""
            Contexto de uso de la interfaz:
            - Uso principal: {contexto_uso}
            - Consecuencias de error: {impacto_error}
            """


            
            for title, criteria in bridges:

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Eres un auditor UX industrial muy exigente. "
                                "Evalúas interfaces HMI comparándolas con estándares profesionales. "
                                "Utiliza una escala estricta y sé crítico."
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text":
                                    f"Evalúa la interfaz HMI según {title}.\n\n"
                                    f"{criteria}\n\n"
                                    "Instrucciones adicionales:\n"
                                    "- Ajusta el nivel de exigencia según el contexto de uso y las consecuencias de error.\n"
                                    "- Si la pantalla se usa en una situación crítica, sé especialmente estricto.\n"
                                    "- Si los errores pueden tener impacto grave, penaliza ambigüedades, falta de claridad o riesgo de error.\n"
                                    "- Si los errores son fácilmente corregibles, puedes ser ligeramente más tolerante.\n"
                                    "Formato obligatorio:\n"
                                    "PUNTUACIÓN: X/10\n"
                                    "RESUMEN: una única frase clara basada en elementos visibles concretos de la imagen. "
                                    "Evita frases genéricas que podrían aplicarse a cualquier HMI. "
                                    "Si no puedes identificar elementos claros en la imagen relacionados con este puente, baja la puntuación."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                import re

                score = None
                summary = ""

                content = response.choices[0].message.content

                match = re.search(r'(?<!\d)(\d{1,2})(?:\.\d+)?\s*/\s*10', content)

                if match:
                    score = round(float(match.group(1)))

                # Extraer resumen
                for line in content.splitlines():
                    if "RESUMEN" in line.upper():
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            summary = parts[1].strip()

                # ⚠️ SOLO añadir score válido
                if score is None:
                    st.warning(f"No se pudo extraer puntuación en {title}")
                    continue

                scores.append(score)
                
                global_inputs.append(f"{title}: {summary}")

                if score >= 7:
                    label, color = "Sólida", "#2e7d32"
                elif score >= 5:
                    label, color = "Mejorable", "#f9a825"
                else:
                    label, color = "Crítica", "#c62828"

                puente_num = title.split("–")[0].title()
                puente_name = title.split("–")[1].strip().capitalize()

                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:8px;">
                        <img src="data:image/svg+xml;base64,{icons[title]}" style="width:80px; height:80px;" />
                        <div>
                            <span style="font-size:20px; color:#666;">{puente_num}</span><br/>
                            <span style="font-size:32px; font-weight:700;">{puente_name}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div style="display:flex; align-items:baseline; gap:14px; margin-top:4px;">
                        <span style="font-size:24px; font-weight:700; color:#000;">{score}/10</span>
                        <span style="font-size:16px; font-weight:600; color:{color};">— {label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div style="background:#eee; border-radius:4px; height:10px; width:100%; margin:6px 0 8px 0;">
                        <div style="background:{color}; width:{score*10}%; height:10px; border-radius:4px;"></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(summary)

                st.markdown(
                    "<hr style='border:none;border-top:1px solid #ddd;margin:24px 0 32px 0;'>",
                    unsafe_allow_html=True
                )

            # =========================
            # RESULTADO GLOBAL
            # =========================

            st.subheader("Resultado global")

            if scores:
                    average_score = round(sum(scores) / len(scores), 1)
            else:
                average_score = 0
                st.error("No se pudieron calcular puntuaciones.")
    
            st.metric("Calidad UX HMI", f"{average_score} / 10")

            # =========================
            # SÍNTESIS FINAL
            # =========================
            summary_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un experto en UX industrial que sintetiza evaluaciones "
                            "para público no experto de forma clara, crítica y directa."
                        )
                    },
                    {
                        "role": "user",
                        "content":
                        "A partir de los siguientes resultados por puente:\n\n"
                        + "\n".join(global_inputs)
                        + "\n\nGenera un resumen FINAL con esta estructura:\n\n"
                          "**OBSERVACIONES CLAVE:**\n"
                          "- Máximo 3 bullets\n\n"
                          "**IMPACTO OPERATIVO:**\n"
                          "- Máximo 3 bullets\n\n"
                          "**OPORTUNIDADES DE MEJORA:**\n"
                          "- Máximo 3 bullets\n\n"
                          "Lenguaje claro, directo y no técnico."
                    }
                ]
            )

            st.write(summary_response.choices[0].message.content)
            import requests

            data = {
                "score_global": average_score,
                "scores": scores,
                "summary": summary_response.choices[0].message.content,
                "contexto_uso": contexto_uso,
                "impacto_error": impacto_error
            }

            try:
                requests.post(
                    "https://script.google.com/macros/s/AKfycbwgowPNFGeBzYGbD2UNLgKlghrgN9KTHuhzVKB2ym-_GL67nSRx9BQD85R0PpR5WMgC/exec",
                    json=data
                )
            except:
                pass

# =========================
# CTA FINAL – SOLO TRAS ANÁLISIS
# =========================
            st.markdown("---")

            st.markdown(
                """
                <div style="font-size:22px; font-weight:600; margin-bottom:12px;">
                    ¿Quieres ir más allá?
                </div>
                <div style="font-size:16px; color:#444; max-width:720px; margin-bottom:28px;">
                    Este análisis es una evaluación rápida basada en una única imagen.
                    Si necesitas un diagnóstico más profundo —con contexto de uso real,
                    flujos operativos y criterios industriales— podemos ayudarte.
                    <br><br>
                    También puedes conocer más sobre HMI Design Observatory, nuestros informes
                    y otras herramientas de diseño HMI industrial.
                </div>
                """,
                unsafe_allow_html=True
            )

            col_left_cta, col_spacer, col_right_cta = st.columns([2, 1, 2])

            with col_left_cta:
                st.markdown(
                    """
                    <a class="cta-dark" href="https://bigd.es/contacto/" target="_blank">
                        Solicitar análisis en profundidad
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            with col_right_cta:
                st.markdown(
                    """
                    <a class="cta-blue" href="https://hmidesign.es/" target="_blank">
                        HMI Design Observatory
                    </a>
                    """,
                    unsafe_allow_html=True
                )

