import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime

# Page config
st.set_page_config(page_title="Graduate Analytics Dashboard", layout="wide", page_icon="🎓")

# Custom styling
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #1f77b4; font-weight: 700;}
    h2 {color: #2c3e50; margin-top: 30px;}
    .plot-container {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 10px 0;}
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"] > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    div[data-testid="metric-container"] > div {
        color: #1f77b4 !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Set seaborn style for better aesthetics
sns.set_style("whitegrid")
sns.set_palette("husl")

st.title("🎓 Graduate Data Analytics Dashboard")
st.markdown("---")

uploaded = st.file_uploader("📁 Upload your Excel/CSV file", type=["xlsx", "csv"])

if uploaded is not None:
    # Load Data
    if uploaded.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded)
    else:
        df = pd.read_csv(uploaded)

    # Data Cleaning
    df[['University', 'Country']] = df['University/Country'].str.split('/', expand=True)
    df[['Zone', 'District', 'City']] = df['Address'].str.split(',', expand=True)
    df = df.drop(columns=['Address', 'University/Country'])

    def remove_spaces(text):
        return re.sub(r'\s+', '', str(text))

    df['District'] = df["District"].apply(remove_spaces)

    replacements = {'NP': 'Nepal', 'IN': 'India', 'US': 'United States'}
    df['Country'] = df['Country'].replace(replacements)
    df['University'] = df['University'].str.split(',', expand=True)[0]

    add_replacements = {
        'Vel Tech Dr RR & SR Technical University': 'Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology',
        'Vel Tech Rangarajan Dr.Sagunthala R&D Institute of Science and Technology': 'Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology'
    }
    df['University'] = df['University'].map(add_replacements).fillna(df['University'])

    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Graduates", f"{len(df):,}")
    with col2:
        st.metric("Universities", df['University'].nunique())
    with col3:
        st.metric("Countries", df['Country'].nunique())
    with col4:
        male_pct = (df['Gender'] == 'Male').sum() / len(df) * 100 if len(df) > 0 else 0
        st.metric("Male %", f"{male_pct:.1f}%")
    with col5:
        year_range = f"{int(df['Passout Year'].min())}-{int(df['Passout Year'].max())}" if len(df) > 0 else "N/A"
        st.metric("Year Range", year_range)

    st.markdown("---")

    # Tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎯 Demographics", "🏫 Universities", "📍 Geographic"])

    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.subheader("Graduation Trends Over Time")
            fig, ax = plt.subplots(figsize=(10, 5))
            counts = df['Passout Year'].value_counts().sort_index()
            ax.plot(counts.index, counts.values, marker='o', linewidth=2.5, markersize=8, color='#1f77b4')
            ax.fill_between(counts.index, counts.values, alpha=0.3)
            ax.set_xlabel("Passout Year", fontsize=12, fontweight='bold')
            ax.set_ylabel("Number of Graduates", fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.subheader("Gender Distribution")
            fig, ax = plt.subplots(figsize=(8, 5))
            counts = df['Gender'].value_counts()
            colors = ['#ff6b6b', '#4ecdc4', '#95e1d3']
            wedges, texts, autotexts = ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%', 
                                               startangle=90, colors=colors[:len(counts)],
                                               textprops={'fontsize': 12, 'fontweight': 'bold'})
            for autotext in autotexts:
                autotext.set_color('white')
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("Gender Trends by Year")
        fig, ax = plt.subplots(figsize=(14, 6))
        pivot = df.pivot_table(index='Passout Year', columns='Gender', aggfunc='size', fill_value=0)
        pivot.plot(kind='bar', ax=ax, width=0.8, color=['#ff6b6b', '#4ecdc4', '#95e1d3'])
        ax.set_xlabel("Passout Year", fontsize=12, fontweight='bold')
        ax.set_ylabel("Number of Graduates", fontsize=12, fontweight='bold')
        ax.legend(title="Gender", title_fontsize=11, fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.subheader("Gender by Zone")
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot = df.pivot_table(index='Zone', columns='Gender', aggfunc='size', fill_value=0)
            pivot.plot(kind='barh', ax=ax, stacked=True, color=['#ff6b6b', '#4ecdc4', '#95e1d3'])
            ax.set_xlabel("Count", fontsize=12, fontweight='bold')
            ax.set_ylabel("Zone", fontsize=12, fontweight='bold')
            ax.legend(title="Gender", title_fontsize=11)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.subheader("Country Distribution")
            fig, ax = plt.subplots(figsize=(10, 6))
            counts = df['Country'].value_counts()
            ax.barh(counts.index, counts.values, color=sns.color_palette("viridis", len(counts)))
            ax.set_xlabel("Count", fontsize=12, fontweight='bold')
            ax.set_ylabel("Country", fontsize=12, fontweight='bold')
            for i, v in enumerate(counts.values):
                ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("Top Universities")
        fig, ax = plt.subplots(figsize=(12, 8))
        counts = df['University'].value_counts().head(15)
        colors = sns.color_palette("rocket", len(counts))
        bars = ax.barh(range(len(counts)), counts.values, color=colors)
        ax.set_yticks(range(len(counts)))
        ax.set_yticklabels(counts.index)
        ax.invert_yaxis()
        ax.set_xlabel("Number of Graduates", fontsize=12, fontweight='bold')
        for i, (bar, val) in enumerate(zip(bars, counts.values)):
            ax.text(val + 0.5, i, str(val), va='center', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("University Enrollment Trends")
        fig, ax = plt.subplots(figsize=(14, 7))
        top_unis = df['University'].value_counts().head(10).index
        temp = df[df['University'].isin(top_unis)]
        pivot = temp.pivot_table(index='Passout Year', columns='University', aggfunc='size', fill_value=0)
        pivot.plot(ax=ax, marker='o', linewidth=2)
        ax.set_xlabel("Passout Year", fontsize=12, fontweight='bold')
        ax.set_ylabel("Number of Graduates", fontsize=12, fontweight='bold')
        ax.legend(title="University", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.subheader("Top 15 Districts")
            fig, ax = plt.subplots(figsize=(10, 7))
            counts = df['District'].value_counts().head(15)
            colors = sns.color_palette("mako", len(counts))
            bars = ax.barh(range(len(counts)), counts.values, color=colors)
            ax.set_yticks(range(len(counts)))
            ax.set_yticklabels(counts.index)
            ax.invert_yaxis()
            ax.set_xlabel("Count", fontsize=12, fontweight='bold')
            for i, (bar, val) in enumerate(zip(bars, counts.values)):
                ax.text(val + 0.5, i, str(val), va='center', fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
            st.markdown('</div>', unsafe_allow_html=True)


        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("Zone Distribution Over Time")
        fig, ax = plt.subplots(figsize=(14, 6))
        pivot = df.pivot_table(index='Passout Year', columns='Zone', aggfunc='size', fill_value=0)
        pivot.plot(kind='area', ax=ax, alpha=0.7, stacked=True)
        ax.set_xlabel("Passout Year", fontsize=12, fontweight='bold')
        ax.set_ylabel("Number of Graduates", fontsize=12, fontweight='bold')
        ax.legend(title="Zone", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Data Table
    st.markdown("---")
    st.markdown("## 📋 Complete Dataset")
    st.dataframe(df, use_container_width=True, height=400)
    

else:
    st.info("👆 Please upload an Excel or CSV file to begin analysis")
    st.markdown("""
    ### Expected Data Format:
    - **University/Country**: Combined field (e.g., "MIT/US")
    - **Address**: Zone, District, City separated by commas
    - **Passout Year**: Graduation year
    - **Gender**: Student gender
    """)