import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Ayarları
st.set_page_config(page_title="Fibabanka Consumer Tribe Dashboard", layout="wide")

st.title("🚀 Consumer Tribe - Stratejik Büyüme Dashboard")
st.markdown("Dijital alışveriş kredisi hunisindeki **refleksleri** ve **darboğazları** simüle eden canlı analiz aracı.")

# --- VERİ ÜRETİMİ ---
@st.cache_data
def load_data():
    np.random.seed(42)
    N_USERS = 6000 
    STEPS = ['1_Giriş', '2_Ürün_Seçimi', '3_Faiz_Görüntüleme', '4_Belge_Yükleme', '5_Onay_ve_Kullanım']
    data = []
    for user_id in range(1, N_USERS + 1):
        device = np.random.choice(['iOS', 'Android'], p=[0.40, 0.60])
        day_of_month = np.random.randint(1, 31)
        is_salary_day = day_of_month in [1, 15, 30]
        for i, step in enumerate(STEPS):
            drop_prob = 0.10
            if step == '3_Faiz_Görüntüleme':
                drop_prob = 0.40
                if is_salary_day: drop_prob *= 0.5
            if step == '4_Belge_Yükleme' and device == 'Android':
                drop_prob += 0.15
            is_dropped = np.random.random() < drop_prob
            data.append({'user_id': user_id, 'step': step, 'device': device, 'day': day_of_month, 'is_salary_day': is_salary_day, 'is_dropped': is_dropped})
            if is_dropped: break
    return pd.DataFrame(data), STEPS

df, STEPS = load_data()

# --- ANALİZLER ---
funnel_stats = df['step'].value_counts().reindex(STEPS)
overall_conv_rate = (funnel_stats.iloc[-1] / funnel_stats.iloc[0])
salary_summary = df[df['step'] == '3_Faiz_Görüntüleme'].groupby('is_salary_day')['is_dropped'].mean() * 100
daily_drops = df[df['step'] == '3_Faiz_Görüntüleme'].groupby('day')['is_dropped'].mean() * 100

# --- DASHBOARD ---
col1, col2 = st.columns([3, 1])

with col1:
    fig = make_subplots(rows=3, cols=1, vertical_spacing=0.1,
                        subplot_titles=("Platform Bazlı Huni", "Maaş Günü Etkisi", "Günlük Terk Trendi"),
                        specs=[[{"type": "funnel"}], [{"type": "bar"}], [{"type": "scatter"}]])
    for dev in ['iOS', 'Android']:
        counts = df[df['device'] == dev]['step'].value_counts().reindex(STEPS)
        fig.add_trace(go.Funnel(name=dev, y=STEPS, x=counts.values, 
                                texttemplate="%{value}<br>%{percentPrevious} of prev<br><b>%{percentInitial} of total</b>"), row=1, col=1)
    fig.add_trace(go.Bar(x=['Normal Gün', 'Maaş Günü'], y=salary_summary.values, marker_color=['#EF553B', '#00CC96']), row=2, col=1)
    fig.add_trace(go.Scatter(x=daily_drops.index, y=daily_drops.values, mode='lines+markers'), row=3, col=1)
    fig.update_layout(height=1000, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Hedef Aylık Trafik", f"{int(30000 / overall_conv_rate):,}")
    st.metric("Maaş Günü Avantajı", f"%{salary_summary.iloc[0] - salary_summary.iloc[1]:.2f}")
    st.info("Bu model, 30.000 kredi hedefi için gereken kullanıcı akışını hesaplar.")