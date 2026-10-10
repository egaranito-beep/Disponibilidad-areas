import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from html import escape

# CONFIGURACIÓN DE LA PÁGINA MÓVIL
st.set_page_config(page_title="Areas Sociales Mirador - Disponibilidad", page_icon="🏡", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #00172b;
    }
    .area-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.6rem;
        width: 100%;
        box-sizing: border-box;
        padding: 0.35rem 0;
    }
    .area-info {
        flex: 1 1 auto;
        min-width: 0;
    }
    .area-caption {
        margin-top: 0.25rem;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.8rem;
    }
    .status-libre, .status-ocupado {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 7.5rem;
        width: 7.5rem;
        box-sizing: border-box;
        color: #ffffff;
        font-weight: 700;
        text-align: center;
        white-space: nowrap;
        font-size: 0.85rem;
        padding: 0.4rem 0.5rem;
        border-radius: 0.5rem;
    }
    .status-libre {
        background-color: #00a83b;
    }
    .status-ocupado {
        background-color: #d50000;
    }
    .tarifas {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    .tarifa-card {
        flex: 1 1 12rem;
        box-sizing: border-box;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 0.8rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.10), rgba(255, 255, 255, 0.04));
    }
    .tarifa-nombre {
        color: rgba(255, 255, 255, 0.82);
        font-size: 0.95rem;
        font-weight: 600;
    }
    .tarifa-precio {
        margin: 0.35rem 0 0.15rem;
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .tarifa-detalle {
        color: rgba(255, 255, 255, 0.68);
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏡 Disponibilidad Semanal")
st.write("Consulta las áreas ocupadas y disponibles para los próximos 7 días.")
st.info("⚠️ Esta plataforma es únicamente informativa. Para gestionar una Reserva, Contacte a la Administradora a los teléfonos 0412-0000000.")
st.markdown(
    """
    <div class="tarifas">
        <div class="tarifa-card">
            <div class="tarifa-nombre">🛝 Parque Infantil</div>
            <div class="tarifa-precio">$100</div>
            <div class="tarifa-detalle">Toda el área · por uso</div>
        </div>
        <div class="tarifa-card">
            <div class="tarifa-nombre">🔥 Parrilleras</div>
            <div class="tarifa-precio">$40</div>
            <div class="tarifa-detalle">Cada una · por uso</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# 🔗 ENLACES DE TU GOOGLE SHEETS
URL_AREAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaoZDeovX4F5ZJCQ54nXJhEykWgtcVRPlgJ8EmywqyBClzGvybN-fKUvbGTKkrxVuHcT5oL9xlBsok/pub?gid=0&single=true&output=csv"
URL_DISPONIBILIDAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaoZDeovX4F5ZJCQ54nXJhEykWgtcVRPlgJ8EmywqyBClzGvybN-fKUvbGTKkrxVuHcT5oL9xlBsok/pub?gid=787051184&single=true&output=csv"

@st.cache_data(ttl=10) # Sincronización en tiempo real (cada 10 segundos)
def cargar_datos():
    try:
        areas = pd.read_csv(URL_AREAS)
        ocupaciones = pd.read_csv(URL_DISPONIBILIDAD)
        ocupaciones['Fecha'] = ocupaciones['Fecha'].astype(str).str.strip()
        ocupaciones['ID_Espacio'] = ocupaciones['ID_Espacio'].astype(str).str.strip()
        return areas, ocupaciones
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

areas_df, ocupaciones_df = cargar_datos()

if not areas_df.empty and not ocupaciones_df.empty:
    
    # 📅 GENERACIÓN AUTOMÁTICA DEL RANGO DE 7 DÍAS (A partir de hoy)
    hoy = datetime.today()
    proximos_7_dias = [hoy + timedelta(days=i) for i in range(7)]
    
    # Creamos pestañas (Tabs) en la app, una para cada día de la semana
    nombres_pestañas = [dia.strftime("%a %d/%m") for dia in proximos_7_dias]
    pestañas = st.tabs(nombres_pestañas)
    
    # Iteramos por cada uno de los 7 días
    for i, dia in enumerate(proximos_7_dias):
        fecha_str = dia.strftime("%Y-%m-%d")
        
        with pestañas[i]:
            st.write(f"### Estado para el {dia.strftime('%A, %d de %B de %Y')}")
            st.write("---")
            
            # Filtramos las ocupaciones de este día específico
            ocupado_ese_dia = ocupaciones_df[ocupaciones_df["Fecha"] == fecha_str]
            lista_ocupados = ocupado_ese_dia["ID_Espacio"].tolist()            
            
            # Dibujamos las áreas disponibles/ocupadas
            for _, area in areas_df.iterrows():
                id_area = str(area["ID_Espacio"]).strip()
                nombre_area = str(area["Nombre Area"]).strip()

                # 1. BUSCAMOS QUIÉN REGISTRÓ ESTE ESPACIO HOY
                # Primero buscamos el bloqueo exacto
                reserva_exacta = ocupado_ese_dia[
                    ocupado_ese_dia["ID_Espacio"].astype(str).str.strip() == id_area
                ]
                # También buscamos si hay un bloqueo total de parrillas
                reserva_total_parrillas = ocupado_ese_dia[
                    ocupado_ese_dia["ID_Espacio"].astype(str).str.strip() == "PARR_TOT"
                ]

                lista_ocupados_str = ocupado_ese_dia["ID_Espacio"].astype(str).str.strip().tolist()
                quien_alquilo = ""

                if id_area in lista_ocupados_str:
                    disponible = False
                    if not reserva_exacta.empty:
                        quien_alquilo = str(reserva_exacta.iloc[0].get("Registrado_por", ""))
                elif "PARR_TOT" in lista_ocupados_str and str(id_area).startswith("PARR_"):
                    disponible = False
                    if not reserva_total_parrillas.empty:
                        quien_alquilo = str(reserva_total_parrillas.iloc[0].get("Registrado_por", "")) 
                else:
                    disponible = True

                if not disponible and quien_alquilo and str(quien_alquilo).strip().lower() != "nan":
                    detalle = f"👤 Reservado por: {escape(quien_alquilo)}"
                elif not disponible:
                    detalle = "👤 Reservado"
                else:
                    detalle = "Disponible"

                if disponible:
                    estado = '<div class="status-libre">🟢 Libre</div>'
                else:
                    estado = '<div class="status-ocupado">🔴 Ocupado</div>'

                st.markdown(
                    f'<div class="area-card">'
                    f'<div class="area-info">'
                    f'<div><strong>{escape(nombre_area)}</strong></div>'
                    f'<div class="area-caption">{detalle}</div>'
                    f'</div>{estado}</div>',
                    unsafe_allow_html=True,
                )
                st.write("---")
