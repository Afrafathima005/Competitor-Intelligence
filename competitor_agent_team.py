import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(
    page_title="🌟 Competitive Intelligence Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Now import other modules
import os
from dotenv import load_dotenv
from exa_py import Exa
from openai import OpenAI
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from collections import defaultdict
from PIL import Image
import base64
from fpdf import FPDF

# Load API keys
load_dotenv()
EXA_API_KEY = os.getenv("EXA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize clients
exa = Exa(api_key=EXA_API_KEY)
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# --- Background Image Setup ---
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main-container {{
            background-color: rgba(255, 255, 255, 0.88);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(4px);
            margin: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.18);
            animation: fadeIn 1s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .card {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            transition: all 0.3s ease !important;
            border-radius: 12px !important;
            border-left: 4px solid #3498db !important;
        }}
        .card:hover {{
            transform: translateY(-5px) scale(1.01) !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        }}
        .sidebar .sidebar-content {{
            background-color: rgba(255, 255, 255, 0.85) !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(52, 152, 219, 0.9) !important;
            color: white !important;
        }}
        .progress-bar {{
            height: 8px;
            background: linear-gradient(90deg, #3498db, #4361ee);
            border-radius: 10px;
            margin: 1rem 0;
        }}
        .pulse {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(52, 152, 219, 0.7); }}
            70% {{ box-shadow: 0 0 0 12px rgba(52, 152, 219, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(52, 152, 219, 0); }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background image (replace with your image path)
add_bg_from_local('2.png')

# --- Button Color Customization ---
st.markdown(
    """
    <style>
    /* Change all Streamlit buttons (including wide/primary) to light blue gradient */
    .stButton > button, .stButton button, .stButton > button:first-child {
        background: linear-gradient(90deg, #6ec1e4 0%, #b3e0fc 100%) !important;
        color: #2c3e50 !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(110, 193, 228, 0.15) !important;
        transition: background 0.2s;
    }
    .stButton > button:hover, .stButton button:hover, .stButton > button:first-child:hover {
        background: linear-gradient(90deg, #4fa3d1 0%, #a0d8f1 100%) !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- App Header ---
st.title("🌟 Competitive Intelligence")
st.markdown("""
    <div style='background-color:rgba(52, 152, 219, 0.15); padding:15px; border-radius:10px; margin-bottom:20px;'>
    <b style='color:#2c3e50;'>Generate comprehensive competitive intelligence reports with AI-powered insights</b>
    </div>
""", unsafe_allow_html=True)

# --- Main Container ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <h3 style='color:#2c3e50;'>Analysis Settings</h3>
            <div class='pulse' style='margin:0 auto; width:60px; height:60px; 
                    background:#3498db; border-radius:50%;'></div>
        </div>
    """, unsafe_allow_html=True)
    
    analysis_depth = st.selectbox(
        "🔍 Analysis Depth",
        ["Standard", "Comprehensive", "Deep Dive"],
        index=1
    )
    
    include_swot = st.checkbox("📋 Include SWOT Analysis", True)
    include_benchmarking = st.checkbox("📊 Include Benchmarking", True)
    include_forecasting = st.checkbox("🔮 Market Forecast", False)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align:center; margin-top:1.5rem;'>
            <p style='font-size:0.8rem; color:#666;'>Powered by AI Analytics</p>
        </div>
    """, unsafe_allow_html=True)

# --- Main Input Form ---
with st.form("main_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        company_input = st.text_input(
            "Company Name",
            placeholder="e.g., Microsoft, Apple, Tesla",
            help="Enter the company you want to analyze"
        )
    with col2:
        num_competitors = st.number_input(
            "Competitors",
            min_value=3,
            max_value=10,
            value=5,
            step=1
        )
    
    submitted = st.form_submit_button(
        "🚀 Generate Analysis",
        use_container_width=True,
        type="primary"
    )

# --- Analysis Execution ---
if submitted and company_input:
    progress_bar = st.progress(0, text="Initializing analysis...")
    analysis_data = defaultdict(dict)
    
    # Step 1: Identify Competitors
    try:
        progress_bar.progress(10, text="Identifying key competitors...")
        competitor_prompt = f"""
        Identify the top {num_competitors} direct competitors for {company_input} in 2024.
        For each competitor, include:
        - Company name
        - Primary competing products/services
        - Estimated market share
        - Key differentiation factors
        
        Format as JSON with this structure:
        {{
            "competitors": [
                {{
                    "name": "Competitor Name",
                    "products": ["product1", "product2"],
                    "market_share": "X%",
                    "differentiation": "Key differentiator"
                }},
                ...
            ]
        }}
        """
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": competitor_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        competitors = json.loads(response.choices[0].message.content)
        analysis_data['competitors'] = competitors['competitors']
        progress_bar.progress(30, text="Competitors identified")
        
    except Exception as e:
        st.error(f"Competitor identification failed: {str(e)}")
        st.stop()
    
    # Step 2: Market Position Analysis
    try:
        progress_bar.progress(40, text="Analyzing market positions...")
        market_prompt = f"""
        Analyze the market positions of {company_input} and its competitors:
        {json.dumps(competitors, indent=2)}
        
        Provide:
        1. Market share comparison
        2. Growth trends
        3. Geographic distribution
        4. Customer segmentation
        
        Format as markdown with clear sections and tables where appropriate.
        """
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": market_prompt}],
            temperature=0.4,
            max_tokens=1500
        )
        analysis_data['market_position'] = response.choices[0].message.content
        progress_bar.progress(60, text="Market analysis complete")
        
    except Exception as e:
        st.warning(f"Market analysis incomplete: {str(e)}")
    
    # Step 3: Technology Comparison
    try:
        progress_bar.progress(70, text="Comparing technologies...")
        tech_prompt = f"""
        Compare the technology stacks of {company_input} and:
        {[c['name'] for c in analysis_data['competitors']]}
        
        Include:
        - Core technologies used
        - R&D investment comparisons
        - Patent analysis
        - Technology adoption rates
        - AI/ML capabilities
        
        Present in a detailed markdown format with tables.
        """
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": tech_prompt}],
            temperature=0.4,
            max_tokens=1500
        )
        analysis_data['technology'] = response.choices[0].message.content
        progress_bar.progress(85, text="Technology comparison done")
        
    except Exception as e:
        st.warning(f"Technology comparison incomplete: {str(e)}")
    
    # Step 4: SWOT Analysis (if enabled)
    if include_swot:
        try:
            progress_bar.progress(90, text="Preparing SWOT analysis...")
            swot_prompt = f"""
            Create a comprehensive SWOT analysis for {company_input} considering:
            - Competitors: {[c['name'] for c in analysis_data['competitors']]}
            - Market position data
            - Technology comparisons
            
            Include:
            1. Strengths (relative to competitors)
            2. Weaknesses (compared to competitors)
            3. Opportunities (market gaps)
            4. Threats (from competitors)
            
            Format as markdown with clear sections.
            """
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": swot_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            analysis_data['swot'] = response.choices[0].message.content
        except Exception as e:
            st.warning(f"SWOT analysis incomplete: {str(e)}")
    
    progress_bar.progress(100, text="Analysis complete!")
    time.sleep(0.5)
    progress_bar.empty()
    
    # Display Results
    st.success("✅ Analysis completed successfully!")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🆚 Competitors", 
        "📈 Market Analysis", 
        "💻 Technology", 
        "📥 Export"
    ])
    
    with tab1:
        st.subheader(f"{company_input} Competitive Overview")
        
        # Key Metrics Cards
        cols = st.columns(3)
        with cols[0]:
            st.markdown("""
                <div class="card">
                    <h3>Market Position</h3>
                    <p><b>Leader</b> in 3 of 5 product categories</p>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("""
                <div class="card">
                    <h3>Competitive Threat</h3>
                    <p><b>High</b> from {competitor}</p>
                </div>
            """.format(competitor=analysis_data['competitors'][0]['name']), unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown("""
                <div class="card">
                    <h3>Technology Edge</h3>
                    <p><b>Advantage</b> in AI/ML</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Market Share Visualization
        st.subheader("Market Share Comparison")
        market_shares = {
            company_input: 35,
            **{c['name']: float(c['market_share'].strip('%'))
              for c in analysis_data['competitors']
              if '%' in c['market_share']}
        }
        fig = px.pie(
            names=list(market_shares.keys()),
            values=list(market_shares.values()),
            hole=0.3,
            title=f"{company_input} vs Competitors Market Share",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Competitor Deep Dive")
        for competitor in analysis_data['competitors']:
            with st.expander(f"🔍 {competitor['name']}", expanded=False):
                st.markdown(f"""
                    <div class="card">
                        <h4>{competitor['name']}</h4>
                        <p><b>Market Share:</b> {competitor['market_share']}</p>
                        <p><b>Key Products:</b> {', '.join(competitor['products'])}</p>
                        <p><b>Differentiation:</b> {competitor['differentiation']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Generate competitive threat analysis
                threat_prompt = f"""
                Analyze the competitive threat posed by {competitor['name']} to {company_input}.
                Focus on:
                - Product overlap
                - Market segments where they compete directly
                - Relative strengths and weaknesses
                - Potential defensive strategies
                """
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": threat_prompt}],
                    temperature=0.4,
                    max_tokens=800
                )
                st.markdown(response.choices[0].message.content)
    
    with tab3:
        st.subheader("Market Position Analysis")
        st.markdown(analysis_data['market_position'])
        
        # Growth Trends Visualization
        st.subheader("Growth Trends")
        growth_data = {
            "Company": [company_input] + [c['name'] for c in analysis_data['competitors']],
            "Growth Rate": [15, 12, 18, 10, 8, 14]  # Mock data
        }
        fig = px.bar(
            growth_data,
            x="Company",
            y="Growth Rate",
            title="Annual Growth Rate Comparison",
            color="Company",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Technology Comparison")
        st.markdown(analysis_data['technology'])
        
        if include_benchmarking:
            st.subheader("Technology Benchmarking")
            tech_metrics = {
                "Metric": ["AI Capabilities", "Cloud Infrastructure", "R&D Investment"],
                company_input: [8, 9, 7],
                analysis_data['competitors'][0]['name']: [9, 7, 8],
                analysis_data['competitors'][1]['name']: [7, 8, 6]
            }
            fig = go.Figure()
            for company in tech_metrics.keys():
                if company != "Metric":
                    fig.add_trace(go.Bar(
                        name=company,
                        x=tech_metrics["Metric"],
                        y=tech_metrics[company]
                    ))
            fig.update_layout(
                barmode='group',
                title="Technology Capability Benchmarking",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("Export Analysis")
        
        # Generate comprehensive report
        report_prompt = f"""
        Compile a comprehensive competitive intelligence report for {company_input} including:
        1. Executive Summary
        2. Competitor Analysis
        3. Market Position
        4. Technology Comparison
        5. Strategic Recommendations
        
        Use all available data and format as markdown.
        """
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": report_prompt}],
            temperature=0.3,
            max_tokens=2500
        )
        full_report = response.choices[0].message.content
        
        # Download options
        st.download_button(
            label="📄 Download Markdown Report",
            data=full_report,
            file_name=f"{company_input}_competitive_analysis_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
        
        st.download_button(
            label="📊 Download Data (JSON)",
            data=json.dumps(analysis_data, indent=2),
            file_name=f"{company_input}_competitive_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        # PDF Export
        def create_pdf_from_text(text, filename="report.pdf"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in text.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf_output = pdf.output(dest='S').encode('latin1')
            return pdf_output
        pdf_bytes = create_pdf_from_text(full_report)
        import base64
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        pdf_filename = f"{company_input}_competitive_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📄 Download PDF Report</a>'
        st.markdown(pdf_href, unsafe_allow_html=True)
        
        st.markdown("### Report Preview")
        with st.expander("View Full Report"):
            st.markdown(full_report[:2000] + "...")

elif submitted:
    st.warning("⚠️ Please enter a company name to analyze")

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Footer with animation
st.markdown("""
<div style="text-align:center; margin-top:2rem; padding:1.5rem; background:rgba(52, 152, 219, 0.15); border-radius:12px;">
    <p style="margin:0; color:#2c3e50; font-weight:500;">Competitive Intelligence Pro © 2024</p>
    <div style="display:flex; justify-content:center; gap:8px; margin-top:12px;">
        <div style="width:10px; height:10px; background:#3498db; border-radius:50%; animation:pulse 1.5s infinite;"></div>
        <div style="width:10px; height:10px; background:#3498db; border-radius:50%; animation:pulse 1.5s infinite; animation-delay:0.3s;"></div>
        <div style="width:10px; height:10px; background:#3498db; border-radius:50%; animation:pulse 1.5s infinite; animation-delay:0.6s;"></div>
    </div>
</div>
""", unsafe_allow_html=True)