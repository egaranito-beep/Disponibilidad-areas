import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# CONFIGURACIÓN DE LA PÁGINA MÓVIL
st.set_page_config(page_title="Club Residencial - Horarios", page_icon="🏡", layout="centered")

st.title("🏡 Disponibilidad Semanal")
st.write("Consulta las áreas ocupadas y disponibles para los próximos 7 días.")
st.info("⚠️ Esta plataforma es únicamente informativa. Para gestionar una reserva, contacte a la administración.")
st.write("---")

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
                id_area = area["ID_Espacio"]
                nombre_area = area["Nombre Area"]
                
                # 1. BUSCAMOS QUIÉN REGISTRÓ ESTE ESPACIO HOY
                # Primero buscamos el bloqueo exacto
                reserva_exacta = ocupado_ese_dia[ocupado_ese_dia["ID_Espacio"] == id_area]
                # También buscamos si hay un bloqueo total de parrillas
                reserva_total_parrillas = ocupado_ese_dia[ocupado_ese_dia["ID_Espacio"] == "PARR_TOT"]
                
                quien_alquilo = ""
                
                if id_area in lista_ocupados:
                    disponible = False
                    if not reserva_exacta.empty:
                        quien_alquilo = str(reserva_exacta.iloc[0]["Registrado_Por"])
                elif "PARR_TOT" in lista_ocupados and "PARR_" in str(id_area):
                    disponible = False
                    if not reserva_total_parrillas.empty:
                        quien_alquilo = str(reserva_total_parrillas.iloc[0]["Registrado_Por"]) + " (Área Total)"
                else:
                    disponible = True
                    
                # Diseño de tarjetas informativas actualizadas
                with st.container():
                    col1, col2 = st.columns()
                    with col1:
                        st.markdown(f"**{nombre_area}**")
                        # 2. MOSTRAR EL NOMBRE SI ESTÁ OCUPADO
                        if not disponible and quien_alquilo and quien_alquilo != "nan":
                            st.caption(f"👤 Reservado por: {quien_alquilo}")
                        else:
                            st.caption(f"Alquilado por día completo")
                    with col2:
                        if disponible:
                            st.success("🟢 Libre")
                        else:
                            st.error("🔴 Ocupado")
                    st.write("---")
