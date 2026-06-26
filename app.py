import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from statsmodels.tsa.stattools import coint
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Equity Research Terminal", layout="wide")

# ---- PASSWORD GATE ----
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown("# EQUITY RESEARCH TERMINAL")
    st.markdown("<p style='color:#888; font-size:12px; letter-spacing:2px;'>RESTRICTED ACCESS — ENTER PASSWORD TO CONTINUE</p>", unsafe_allow_html=True)
    password = st.text_input("PASSWORD", type="password")
    if st.button("ENTER", type="primary"):
        if password == "Airbear2004!":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("INCORRECT PASSWORD")
    st.stop()

st.set_page_config(page_title="Equity Research Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .stSidebar { background-color: #111111; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #00ff88;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-value { font-size: 26px; font-weight: 700; color: #00ff88; }
    .metric-label { font-size: 11px; color: #888; letter-spacing: 2px; text-transform: uppercase; }
    .section-header {
        font-size: 13px;
        color: #00ff88;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-bottom: 1px solid #333;
        padding-bottom: 8px;
        margin: 24px 0 16px 0;
    }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #00ff88; }
</style>
""", unsafe_allow_html=True)

st.markdown("# EQUITY RESEARCH TERMINAL")
st.markdown("<p style='color:#888; font-size:12px; letter-spacing:2px;'>BUILT BY AARON DEHRING | FAMILY WEALTH PARTNERS | QUANTITATIVE ANALYSIS DIVISION</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### TERMINAL SETTINGS")
ticker = st.sidebar.text_input("PRIMARY TICKER", value="AAPL").upper()
benchmark = st.sidebar.text_input("BENCHMARK", value="SPY").upper()
period = st.sidebar.selectbox("TIME PERIOD", ["6mo", "1y", "2y", "5y"], index=1)
compare_tickers = st.sidebar.text_input("COMPARE TICKERS (comma separated)", value="MSFT,GOOGL,AMZN")
mc_simulations = st.sidebar.slider("MONTE CARLO SIMULATIONS", 100, 1000, 500)
mc_days = st.sidebar.slider("FORECAST HORIZON (days)", 30, 252, 90)
st.sidebar.markdown("<p style='color:#555; font-size:10px;'>POWERED BY YAHOO FINANCE API</p>", unsafe_allow_html=True)

@st.cache_data
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    info = stock.info
    return df, info

@st.cache_data
def load_multi(tickers, period):
    data = {}
    for t in tickers:
        try:
            df, _ = load_data(t, period)
            data[t] = df['Close']
        except:
            pass
    return pd.DataFrame(data)

df, info = load_data(ticker, period)
bench_df, _ = load_data(benchmark, period)
tickers_list = [t.strip().upper() for t in compare_tickers.split(",") if t.strip()]
all_tickers = list(set([ticker, benchmark] + tickers_list))
multi_df = load_multi(tuple(all_tickers), period)

daily_returns = df['Close'].pct_change().dropna()
bench_returns = bench_df['Close'].pct_change().dropna()

current_price = df['Close'].iloc[-1]
period_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
volatility = daily_returns.std() * np.sqrt(252) * 100
sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
var_95 = np.percentile(daily_returns, 5) * 100
aligned = pd.concat([daily_returns, bench_returns], axis=1).dropna()
aligned.columns = ['stock', 'bench']
beta = aligned.cov().iloc[0, 1] / aligned['bench'].var()
alpha = (daily_returns.mean() - beta * bench_returns.mean()) * 252 * 100
rolling_max = df['Close'].cummax()
max_drawdown = ((df['Close'] - rolling_max) / rolling_max * 100).min()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["PRICE & RISK ANALYSIS", "PORTFOLIO OPTIMIZER", "PAIRS TRADING", "EARNINGS ANALYSIS", "SENTIMENT ANALYSIS"])# ====================
# TAB 1
# ====================
with tab1:
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    metrics = [
        ("PRICE", f"${current_price:.2f}"),
        ("PERIOD RETURN", f"{period_return:+.2f}%"),
        ("SHARPE RATIO", f"{sharpe:.2f}"),
        ("BETA", f"{beta:.2f}"),
        ("ALPHA (ann.)", f"{alpha:+.2f}%"),
        ("VAR 95%", f"{var_95:.2f}%"),
        ("MAX DRAWDOWN", f"{max_drawdown:.2f}%"),
    ]
    for col, (label, value) in zip([m1,m2,m3,m4,m5,m6,m7], metrics):
        col.markdown(f"<div class='metric-card'><div class='metric-value'>{value}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>PRICE ACTION & VOLUME ANALYSIS</div>", unsafe_allow_html=True)
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()
    df['BB_upper'] = df['MA20'] + 2 * df['Close'].rolling(20).std()
    df['BB_lower'] = df['MA20'] - 2 * df['Close'].rolling(20).std()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='rgba(0,255,136,0.2)', width=1), name='BB Upper', showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], fill='tonexty', fillcolor='rgba(0,255,136,0.05)', line=dict(color='rgba(0,255,136,0.2)', width=1), name='Bollinger Bands'), row=1, col=1)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=ticker, increasing_line_color='#00ff88', decreasing_line_color='#ff4444'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#FFD700', width=1, dash='dash'), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#FF8C00', width=1, dash='dash'), name='MA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], line=dict(color='#FF4500', width=1, dash='dot'), name='MA200'), row=1, col=1)
    colors = ['#00ff88' if c >= o else '#ff4444' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume', opacity=0.7), row=2, col=1)
    fig.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=550, showlegend=True, xaxis_rangeslider_visible=False, font=dict(family='monospace', color='#888'))
    fig.update_yaxes(gridcolor='#1a1a1a')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>MONTE CARLO SIMULATION</div>", unsafe_allow_html=True)
    mu = daily_returns.mean()
    sigma = daily_returns.std()
    last_price = df['Close'].iloc[-1]
    simulations = np.zeros((mc_days, mc_simulations))
    for i in range(mc_simulations):
        prices = [last_price]
        for _ in range(mc_days - 1):
            shock = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + shock))
        simulations[:, i] = prices

    p5 = np.percentile(simulations, 5, axis=1)
    p25 = np.percentile(simulations, 25, axis=1)
    p50 = np.percentile(simulations, 50, axis=1)
    p75 = np.percentile(simulations, 75, axis=1)
    p95 = np.percentile(simulations, 95, axis=1)

    mc1, mc2, mc3 = st.columns(3)
    mc1.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>${p95[-1]:.2f}</div><div class='metric-label'>BULL CASE (95th)</div></div>", unsafe_allow_html=True)
    mc2.markdown(f"<div class='metric-card'><div class='metric-value'>${p50[-1]:.2f}</div><div class='metric-label'>BASE CASE (MEDIAN)</div></div>", unsafe_allow_html=True)
    mc3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#ff4444'>${p5[-1]:.2f}</div><div class='metric-label'>BEAR CASE (5th)</div></div>", unsafe_allow_html=True)

    fig_mc = go.Figure()
    for i in range(min(150, mc_simulations)):
        fig_mc.add_trace(go.Scatter(y=simulations[:, i], mode='lines', line=dict(color='rgba(0,255,136,0.03)', width=1), showlegend=False))
    fig_mc.add_trace(go.Scatter(y=p95, line=dict(color='rgba(0,255,136,0.5)', width=2, dash='dash'), name='95th Percentile'))
    fig_mc.add_trace(go.Scatter(y=p75, fill='tonexty', fillcolor='rgba(0,255,136,0.05)', line=dict(color='rgba(0,255,136,0.3)', width=1), name='75th Percentile'))
    fig_mc.add_trace(go.Scatter(y=p50, line=dict(color='#00ff88', width=3), name='Median Path'))
    fig_mc.add_trace(go.Scatter(y=p25, fill='tonexty', fillcolor='rgba(255,68,68,0.05)', line=dict(color='rgba(255,68,68,0.3)', width=1), name='25th Percentile'))
    fig_mc.add_trace(go.Scatter(y=p5, line=dict(color='rgba(255,68,68,0.5)', width=2, dash='dash'), name='5th Percentile'))
    fig_mc.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=400, font=dict(family='monospace'))
    st.plotly_chart(fig_mc, use_container_width=True)

    st.markdown("<div class='section-header'>CROSS-ASSET CORRELATION MATRIX</div>", unsafe_allow_html=True)
    returns_df = multi_df.pct_change().dropna()
    corr = returns_df.corr()
    fig_corr = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale=[[0,'#ff4444'],[0.5,'#111'],[1,'#00ff88']], zmin=-1, zmax=1, text=np.round(corr.values, 2), texttemplate="%{text}", textfont=dict(size=12, color='white')))
    fig_corr.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=400, font=dict(family='monospace'))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("<div class='section-header'>ROLLING 60-DAY BETA vs {}</div>".format(benchmark), unsafe_allow_html=True)
    aligned2 = pd.concat([daily_returns, bench_returns], axis=1).dropna()
    aligned2.columns = ['stock', 'bench']
    rolling_beta = aligned2['stock'].rolling(60).cov(aligned2['bench']) / aligned2['bench'].rolling(60).var()
    fig_beta = go.Figure()
    fig_beta.add_hline(y=1.0, line_dash='dash', line_color='#555', annotation_text='BETA = 1.0')
    fig_beta.add_trace(go.Scatter(x=rolling_beta.index, y=rolling_beta.values, fill='tozeroy', fillcolor='rgba(0,255,136,0.1)', line=dict(color='#00ff88', width=2), name='Rolling Beta'))
    fig_beta.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, font=dict(family='monospace'))
    st.plotly_chart(fig_beta, use_container_width=True)

    st.markdown("<div class='section-header'>RETURN DISTRIBUTION & RISK PROFILE</div>", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(x=daily_returns * 100, nbinsx=60, marker_color='#00ff88', opacity=0.7, name='Daily Returns'))
        fig_dist.add_vline(x=var_95, line_dash='dash', line_color='#ff4444', annotation_text=f'VaR 95%: {var_95:.2f}%')
        fig_dist.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, title='Daily Return Distribution', font=dict(family='monospace', size=10))
        st.plotly_chart(fig_dist, use_container_width=True)
    with d2:
        cumulative = (1 + daily_returns).cumprod()
        bench_cumulative = (1 + bench_returns).cumprod()
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=cumulative.index, y=cumulative.values, line=dict(color='#00ff88', width=2), name=ticker))
        fig_cum.add_trace(go.Scatter(x=bench_cumulative.index, y=bench_cumulative.values, line=dict(color='#888', width=2, dash='dash'), name=benchmark))
        fig_cum.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, title='Cumulative Returns vs Benchmark', font=dict(family='monospace', size=10))
        st.plotly_chart(fig_cum, use_container_width=True)

    st.markdown("<div class='section-header'>AI ANALYST DEBATE ENGINE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Three independent AI analysts debate the position. Bull vs Bear vs Risk. Consensus generated after.</p>", unsafe_allow_html=True)

    if st.button("RUN ANALYST DEBATE", type="primary"):

        API_KEY = "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"
        HEADERS = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        }

        market_data = f"""
Ticker: {ticker} ({info.get('longName', ticker)})
Sector: {info.get('sector', 'N/A')}
Market Cap: {info.get('marketCap', 'N/A')}
Current Price: ${current_price:.2f}
Period Return: {period_return:+.2f}%
Sharpe Ratio: {sharpe:.2f}
Beta: {beta:.2f}
Annualized Alpha: {alpha:+.2f}%
Annualized Volatility: {volatility:.2f}%
Value at Risk (95%): {var_95:.2f}%
Max Drawdown: {max_drawdown:.2f}%
Monte Carlo Median ({mc_days}d): ${p50[-1]:.2f}
Monte Carlo Bull Case: ${p95[-1]:.2f}
Monte Carlo Bear Case: ${p5[-1]:.2f}
"""

        analysts = [
            {
                "role": "BULL ANALYST",
                "color": "#00ff88",
                "prompt": f"""You are an aggressive bull-side equity analyst at a top hedge fund. Make the strongest possible BUY case for {ticker}.

{market_data}

Use exactly these section labels in ALL CAPS with no symbols before them:
BULL THESIS
KEY CATALYSTS
PRICE TARGET RATIONALE

3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""
            },
            {
                "role": "BEAR ANALYST",
                "color": "#ff4444",
                "prompt": f"""You are a short-seller and bear-side analyst at a top hedge fund. Make the strongest possible SELL case for {ticker}.

{market_data}

Use exactly these section labels in ALL CAPS with no symbols before them:
BEAR THESIS
KEY RISKS
DOWNSIDE TARGET

3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""
            },
            {
                "role": "RISK ANALYST",
                "color": "#FFD700",
                "prompt": f"""You are a quantitative risk analyst at a prime brokerage. Provide a cold, data-driven risk assessment of {ticker} with no bull or bear bias.

{market_data}

Use exactly these section labels in ALL CAPS with no symbols before them:
VOLATILITY ANALYSIS
TAIL RISK ASSESSMENT
POSITION SIZING RECOMMENDATION

3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""
            }
        ]

        memos = {}
        col_bull, col_bear, col_risk = st.columns(3)
        columns = [col_bull, col_bear, col_risk]

        for i, analyst in enumerate(analysts):
            with columns[i]:
                st.markdown(f"<div style='color:{analyst['color']}; font-size:12px; letter-spacing:2px; font-family:monospace; margin-bottom:8px; font-weight:700;'>{analyst['role']}</div>", unsafe_allow_html=True)
                with st.spinner(f"Analyzing..."):
                    response = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers=HEADERS,
                        json={"model": "claude-sonnet-4-6", "max_tokens": 800, "messages": [{"role": "user", "content": analyst['prompt']}]}
                    )
                    memo = response.json()['content'][0]['text']
                    memos[analyst['role']] = memo
                    formatted = memo
                    for label in ['BULL THESIS', 'KEY CATALYSTS', 'PRICE TARGET RATIONALE', 'BEAR THESIS', 'KEY RISKS', 'DOWNSIDE TARGET', 'VOLATILITY ANALYSIS', 'TAIL RISK ASSESSMENT', 'POSITION SIZING RECOMMENDATION']:
                        formatted = formatted.replace(label, f"<br><span style='color:{analyst['color']}; letter-spacing:2px; font-size:10px;'>{label}</span><br>")
                    st.markdown(f"<div style='background:#0d1117; border:1px solid {analyst['color']}; border-radius:8px; padding:20px; font-family:monospace; font-size:12px; line-height:2; color:#ccc; min-height:400px;'>{formatted}</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>CONSENSUS RATING</div>", unsafe_allow_html=True)
        with st.spinner("Synthesizing consensus..."):
            consensus_prompt = f"""You are the head of research at a top investment bank. Three analysts have debated {ticker}.

BULL ANALYST: {memos.get('BULL ANALYST', '')}
BEAR ANALYST: {memos.get('BEAR ANALYST', '')}
RISK ANALYST: {memos.get('RISK ANALYST', '')}

Synthesize into a final consensus using exactly these section labels in ALL CAPS:
CONSENSUS VERDICT
KEY DEBATE POINTS
FINAL RECOMMENDATION

Start CONSENSUS VERDICT with one of: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""

            consensus_response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=HEADERS,
                json={"model": "claude-sonnet-4-6", "max_tokens": 800, "messages": [{"role": "user", "content": consensus_prompt}]}
            )
            consensus = consensus_response.json()['content'][0]['text']
            formatted_consensus = consensus
            for label in ['CONSENSUS VERDICT', 'KEY DEBATE POINTS', 'FINAL RECOMMENDATION']:
                formatted_consensus = formatted_consensus.replace(label, f"<br><span style='color:#00ccff; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
            st.markdown(f"<div style='background:#0d1117; border:1px solid #00ccff; border-radius:8px; padding:24px; font-family:monospace; font-size:13px; line-height:2; color:#ccc;'><div style='color:#00ccff; font-size:12px; letter-spacing:3px; margin-bottom:16px;'>HEAD OF RESEARCH — CONSENSUS REPORT</div>{formatted_consensus}</div>", unsafe_allow_html=True)
# ====================
# TAB 2
# ====================
with tab2:
    st.markdown("<div class='section-header'>PORTFOLIO OPTIMIZER — MARKOWITZ MEAN-VARIANCE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Enter up to 10 tickers to compute the optimal portfolio allocation and efficient frontier.</p>", unsafe_allow_html=True)

    port_input = st.text_input("PORTFOLIO TICKERS (comma separated)", value="AAPL,MSFT,GOOGL,AMZN,SPY")
    port_tickers = [t.strip().upper() for t in port_input.split(",") if t.strip()]
    port_period = st.selectbox("LOOKBACK PERIOD", ["1y", "2y", "3y", "5y"], index=1, key="port_period")

    if st.button("RUN OPTIMIZATION", type="primary"):
        with st.spinner("Running mean-variance optimization..."):

            @st.cache_data
            def load_portfolio_data(tickers, period):
                dfs = {}
                for t in tickers:
                    try:
                        d = yf.Ticker(t).history(period=period)['Close']
                        dfs[t] = d
                    except:
                        pass
                return pd.DataFrame(dfs).dropna()

            prices = load_portfolio_data(tuple(port_tickers), port_period)
            returns = prices.pct_change().dropna()
            mean_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252
            n = len(port_tickers)

            num_portfolios = 5000
            results = np.zeros((3, num_portfolios))
            weights_record = []

            for i in range(num_portfolios):
                w = np.random.random(n)
                w /= w.sum()
                weights_record.append(w)
                port_return = np.dot(w, mean_returns)
                port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
                sharpe_p = port_return / port_vol
                results[0, i] = port_vol
                results[1, i] = port_return
                results[2, i] = sharpe_p

            max_sharpe_idx = np.argmax(results[2])
            min_vol_idx = np.argmin(results[0])
            max_sharpe_weights = weights_record[max_sharpe_idx]
            min_vol_weights = weights_record[min_vol_idx]

            st.markdown("<div class='section-header'>OPTIMAL PORTFOLIO RESULTS</div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)

            with o1:
                st.markdown("**MAXIMUM SHARPE RATIO PORTFOLIO**")
                ms1, ms2, ms3 = st.columns(3)
                ms1.markdown(f"<div class='metric-card'><div class='metric-value'>{results[2, max_sharpe_idx]:.2f}</div><div class='metric-label'>SHARPE RATIO</div></div>", unsafe_allow_html=True)
                ms2.markdown(f"<div class='metric-card'><div class='metric-value'>{results[1, max_sharpe_idx]*100:.2f}%</div><div class='metric-label'>ANN. RETURN</div></div>", unsafe_allow_html=True)
                ms3.markdown(f"<div class='metric-card'><div class='metric-value'>{results[0, max_sharpe_idx]*100:.2f}%</div><div class='metric-label'>ANN. VOLATILITY</div></div>", unsafe_allow_html=True)
                fig_pie1 = go.Figure(go.Pie(labels=port_tickers, values=max_sharpe_weights, hole=0.4, marker=dict(colors=['#00ff88','#00ccff','#FFD700','#FF8C00','#ff4444','#aa44ff','#00ffcc','#ff88aa','#88ffaa','#ffcc00'])))
                fig_pie1.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
                st.plotly_chart(fig_pie1, use_container_width=True)

            with o2:
                st.markdown("**MINIMUM VOLATILITY PORTFOLIO**")
                mv1, mv2, mv3 = st.columns(3)
                mv1.markdown(f"<div class='metric-card'><div class='metric-value'>{results[2, min_vol_idx]:.2f}</div><div class='metric-label'>SHARPE RATIO</div></div>", unsafe_allow_html=True)
                mv2.markdown(f"<div class='metric-card'><div class='metric-value'>{results[1, min_vol_idx]*100:.2f}%</div><div class='metric-label'>ANN. RETURN</div></div>", unsafe_allow_html=True)
                mv3.markdown(f"<div class='metric-card'><div class='metric-value'>{results[0, min_vol_idx]*100:.2f}%</div><div class='metric-label'>ANN. VOLATILITY</div></div>", unsafe_allow_html=True)
                fig_pie2 = go.Figure(go.Pie(labels=port_tickers, values=min_vol_weights, hole=0.4, marker=dict(colors=['#00ff88','#00ccff','#FFD700','#FF8C00','#ff4444','#aa44ff','#00ffcc','#ff88aa','#88ffaa','#ffcc00'])))
                fig_pie2.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
                st.plotly_chart(fig_pie2, use_container_width=True)

            st.markdown("<div class='section-header'>EFFICIENT FRONTIER</div>", unsafe_allow_html=True)
            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(x=results[0]*100, y=results[1]*100, mode='markers', marker=dict(color=results[2], colorscale=[[0,'#ff4444'],[0.5,'#FFD700'],[1,'#00ff88']], size=3, opacity=0.6, colorbar=dict(title='Sharpe', thickness=10)), name='Portfolios'))
            fig_ef.add_trace(go.Scatter(x=[results[0, max_sharpe_idx]*100], y=[results[1, max_sharpe_idx]*100], mode='markers', marker=dict(color='#00ff88', size=18, symbol='star'), name='Max Sharpe'))
            fig_ef.add_trace(go.Scatter(x=[results[0, min_vol_idx]*100], y=[results[1, min_vol_idx]*100], mode='markers', marker=dict(color='#00ccff', size=18, symbol='diamond'), name='Min Volatility'))
            fig_ef.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=500, font=dict(family='monospace'), xaxis_title='ANNUALIZED VOLATILITY (%)', yaxis_title='ANNUALIZED RETURN (%)', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(r=40))
            st.plotly_chart(fig_ef, use_container_width=True)

            st.markdown("<div class='section-header'>ALLOCATION WEIGHTS</div>", unsafe_allow_html=True)
            weights_df = pd.DataFrame({'Ticker': port_tickers, 'Max Sharpe Weight': [f"{w*100:.2f}%" for w in max_sharpe_weights], 'Min Vol Weight': [f"{w*100:.2f}%" for w in min_vol_weights]})
            st.dataframe(weights_df.set_index('Ticker'), use_container_width=True)

# ====================
# TAB 3
# ====================
with tab3:
    st.markdown("<div class='section-header'>PAIRS TRADING SIGNAL ENGINE — STATISTICAL ARBITRAGE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Tests cointegration between two assets and generates mean-reversion signals based on z-score thresholds.</p>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    pair1 = col_p1.text_input("ASSET 1", value="KO").upper()
    pair2 = col_p2.text_input("ASSET 2", value="PEP").upper()
    pairs_period = st.selectbox("LOOKBACK PERIOD", ["1y", "2y", "3y", "5y"], index=1, key="pairs_period")
    z_entry = st.slider("Z-SCORE ENTRY THRESHOLD", 1.0, 3.0, 2.0, 0.1)
    z_exit = st.slider("Z-SCORE EXIT THRESHOLD", 0.0, 1.5, 0.5, 0.1)

    if st.button("RUN PAIRS ANALYSIS", type="primary"):
        with st.spinner("Running cointegration analysis..."):

            @st.cache_data
            def load_pairs(t1, t2, period):
                d1 = yf.Ticker(t1).history(period=period)['Close']
                d2 = yf.Ticker(t2).history(period=period)['Close']
                return pd.DataFrame({t1: d1, t2: d2}).dropna()

            pairs_df = load_pairs(pair1, pair2, pairs_period)
            score, pvalue, _ = coint(pairs_df[pair1], pairs_df[pair2])

            coint_col1, coint_col2, coint_col3 = st.columns(3)
            coint_col1.markdown(f"<div class='metric-card'><div class='metric-value'>{score:.4f}</div><div class='metric-label'>COINTEGRATION SCORE</div></div>", unsafe_allow_html=True)
            coint_col2.markdown(f"<div class='metric-card'><div class='metric-value'>{pvalue:.4f}</div><div class='metric-label'>P-VALUE</div></div>", unsafe_allow_html=True)

            if pvalue < 0.05:
                verdict = "COINTEGRATED"
                verdict_color = "#00ff88"
                verdict_note = "Pairs trading strategy is statistically valid"
            else:
                verdict = "NOT COINTEGRATED"
                verdict_color = "#ff4444"
                verdict_note = "Insufficient statistical relationship"

            coint_col3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:{verdict_color}'>{verdict}</div><div class='metric-label'>{verdict_note}</div></div>", unsafe_allow_html=True)

            X = pairs_df[pair2].values.reshape(-1, 1)
            y = pairs_df[pair1].values
            hedge_model = LinearRegression().fit(X, y)
            hedge_ratio = hedge_model.coef_[0]

            spread = pairs_df[pair1] - hedge_ratio * pairs_df[pair2]
            zscore = (spread - spread.mean()) / spread.std()

            signals = pd.Series('NEUTRAL', index=zscore.index)
            signals[zscore > z_entry] = 'SELL SPREAD'
            signals[zscore < -z_entry] = 'BUY SPREAD'
            signals[abs(zscore) < z_exit] = 'EXIT'

            current_zscore = zscore.iloc[-1]
            current_signal = signals.iloc[-1]
            signal_color = '#FFD700' if current_signal == 'NEUTRAL' else '#00ff88' if current_signal == 'BUY SPREAD' else '#ff4444' if current_signal == 'SELL SPREAD' else '#00ccff'

            st.markdown("<div class='section-header'>CURRENT SIGNAL</div>", unsafe_allow_html=True)
            s1, s2, s3 = st.columns(3)
            s1.markdown(f"<div class='metric-card'><div class='metric-value' style='color:{signal_color}'>{current_signal}</div><div class='metric-label'>ACTIVE SIGNAL</div></div>", unsafe_allow_html=True)
            s2.markdown(f"<div class='metric-card'><div class='metric-value'>{current_zscore:.2f}</div><div class='metric-label'>CURRENT Z-SCORE</div></div>", unsafe_allow_html=True)
            s3.markdown(f"<div class='metric-card'><div class='metric-value'>{hedge_ratio:.4f}</div><div class='metric-label'>HEDGE RATIO</div></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>NORMALIZED PRICE COMPARISON</div>", unsafe_allow_html=True)
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(x=pairs_df.index, y=pairs_df[pair1]/pairs_df[pair1].iloc[0]*100, line=dict(color='#00ff88', width=2), name=pair1))
            fig_price.add_trace(go.Scatter(x=pairs_df.index, y=pairs_df[pair2]/pairs_df[pair2].iloc[0]*100, line=dict(color='#00ccff', width=2), name=pair2))
            fig_price.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, font=dict(family='monospace'), yaxis_title='NORMALIZED PRICE (BASE 100)')
            st.plotly_chart(fig_price, use_container_width=True)

            st.markdown("<div class='section-header'>Z-SCORE & TRADING SIGNALS</div>", unsafe_allow_html=True)
            buy_signals = zscore[signals == 'BUY SPREAD']
            sell_signals = zscore[signals == 'SELL SPREAD']
            exit_signals = zscore[signals == 'EXIT']

            fig_spread = go.Figure()
            fig_spread.add_hline(y=z_entry, line_dash='dash', line_color='#ff4444', annotation_text=f'SELL ({z_entry})')
            fig_spread.add_hline(y=-z_entry, line_dash='dash', line_color='#00ff88', annotation_text=f'BUY (-{z_entry})')
            fig_spread.add_hline(y=z_exit, line_dash='dot', line_color='#888')
            fig_spread.add_hline(y=-z_exit, line_dash='dot', line_color='#888')
            fig_spread.add_hline(y=0, line_color='#444')
            fig_spread.add_trace(go.Scatter(x=zscore.index, y=zscore.values, line=dict(color='#FFD700', width=1.5), name='Z-Score'))
            fig_spread.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals.values, mode='markers', marker=dict(color='#00ff88', size=10, symbol='triangle-up'), name='BUY SPREAD'))
            fig_spread.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals.values, mode='markers', marker=dict(color='#ff4444', size=10, symbol='triangle-down'), name='SELL SPREAD'))
            fig_spread.add_trace(go.Scatter(x=exit_signals.index, y=exit_signals.values, mode='markers', marker=dict(color='#00ccff', size=8, symbol='circle'), name='EXIT'))
            fig_spread.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=400, font=dict(family='monospace'), yaxis_title='Z-SCORE')
            st.plotly_chart(fig_spread, use_container_width=True)

            st.markdown("<div class='section-header'>SIGNAL HISTORY</div>", unsafe_allow_html=True)
            signal_df = pd.DataFrame({'Z-SCORE': zscore.round(4), 'SPREAD': spread.round(4), 'SIGNAL': signals}).tail(30).iloc[::-1]
            st.dataframe(signal_df, use_container_width=True)
# ====================
# TAB 4
# ====================
with tab4:
    st.markdown("<div class='section-header'>EARNINGS SURPRISE MODEL — QUANTITATIVE EARNINGS ANALYSIS</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Analyzes historical earnings surprises, pre/post earnings price behavior, and generates a quantitative earnings outlook.</p>", unsafe_allow_html=True)

    earn_ticker = st.text_input("EARNINGS TICKER", value="AAPL", key="earn_ticker").upper()
    pre_window = st.slider("PRE-EARNINGS WINDOW (days)", 5, 30, 20, key="pre_window")
    post_window = st.slider("POST-EARNINGS WINDOW (days)", 1, 10, 3, key="post_window")

    if st.button("RUN EARNINGS ANALYSIS", type="primary", key="run_earnings_btn"):
        with st.spinner("Pulling earnings data and running analysis..."):

            stock = yf.Ticker(earn_ticker)
            earnings = stock.earnings_dates
            hist = stock.history(period="5y")
            info_e = stock.info

            if earnings is not None and len(earnings) > 0:
                earnings = earnings.dropna(subset=['EPS Estimate', 'Reported EPS'])
                earnings = earnings.head(12)
                earnings.index = earnings.index.tz_localize(None) if earnings.index.tzinfo is not None else earnings.index
                hist.index = hist.index.tz_localize(None) if hist.index.tzinfo is not None else hist.index

                earnings['Surprise %'] = ((earnings['Reported EPS'] - earnings['EPS Estimate']) / abs(earnings['EPS Estimate'])) * 100
                earnings['Beat'] = earnings['Surprise %'] > 0

                beats = earnings['Beat'].sum()
                misses = len(earnings) - beats
                avg_surprise = earnings['Surprise %'].mean()
                beat_rate = (beats / len(earnings)) * 100

                pre_returns = []
                post_returns = []

                for date in earnings.index:
                    try:
                        date = pd.Timestamp(date)
                        hist_dates = hist.index
                        pos = hist_dates.searchsorted(date)
                        if pos >= pre_window and pos + post_window < len(hist):
                            pre_start = hist.iloc[pos - pre_window]['Close']
                            pre_end = hist.iloc[pos - 1]['Close']
                            post_start = hist.iloc[pos]['Close']
                            post_end = hist.iloc[pos + post_window]['Close']
                            pre_ret = (pre_end - pre_start) / pre_start * 100
                            post_ret = (post_end - post_start) / post_start * 100
                            pre_returns.append(pre_ret)
                            post_returns.append(post_ret)
                        else:
                            pre_returns.append(None)
                            post_returns.append(None)
                    except:
                        pre_returns.append(None)
                        post_returns.append(None)

                earnings['Pre-Earnings Return'] = pre_returns
                earnings['Post-Earnings Return'] = post_returns

                st.session_state['earnings_data'] = earnings
                st.session_state['earnings_info'] = {
                    'beat_rate': beat_rate,
                    'avg_surprise': avg_surprise,
                    'beats': beats,
                    'misses': misses,
                    'ticker': earn_ticker,
                    'sector': info_e.get('sector', 'N/A'),
                    'price': current_price
                }

    if 'earnings_data' in st.session_state:
        earnings = st.session_state['earnings_data']
        einfo = st.session_state['earnings_info']
        beat_rate = einfo['beat_rate']
        avg_surprise = einfo['avg_surprise']
        beats = einfo['beats']
        misses = einfo['misses']

        st.markdown("<div class='section-header'>EARNINGS SCORECARD</div>", unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4)
        e1.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>{beat_rate:.0f}%</div><div class='metric-label'>BEAT RATE</div></div>", unsafe_allow_html=True)
        e2.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_surprise:+.2f}%</div><div class='metric-label'>AVG SURPRISE</div></div>", unsafe_allow_html=True)
        e3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>{int(beats)}</div><div class='metric-label'>BEATS</div></div>", unsafe_allow_html=True)
        e4.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#ff4444'>{int(misses)}</div><div class='metric-label'>MISSES</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>EARNINGS SURPRISE HISTORY</div>", unsafe_allow_html=True)
        colors_earn = ['#00ff88' if b else '#ff4444' for b in earnings['Beat']]
        fig_earn = go.Figure()
        fig_earn.add_hline(y=0, line_color='#444')
        fig_earn.add_trace(go.Bar(x=[str(d.date()) for d in earnings.index], y=earnings['Surprise %'], marker_color=colors_earn, name='EPS Surprise %'))
        fig_earn.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=350, font=dict(family='monospace'), yaxis_title='SURPRISE %', xaxis_title='EARNINGS DATE')
        st.plotly_chart(fig_earn, use_container_width=True)

        clean = earnings.dropna(subset=['Pre-Earnings Return', 'Post-Earnings Return'])
        if len(clean) > 0:
            avg_pre = clean['Pre-Earnings Return'].mean()
            avg_post = clean['Post-Earnings Return'].mean()
            avg_post_beat = clean[clean['Beat']]['Post-Earnings Return'].mean() if len(clean[clean['Beat']]) > 0 else 0
            avg_post_miss = clean[~clean['Beat']]['Post-Earnings Return'].mean() if len(clean[~clean['Beat']]) > 0 else 0

            st.markdown("<div class='section-header'>PRE vs POST EARNINGS PRICE BEHAVIOR</div>", unsafe_allow_html=True)
            p1, p2, p3, p4 = st.columns(4)
            p1.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_pre:+.2f}%</div><div class='metric-label'>AVG PRE-EARNINGS</div></div>", unsafe_allow_html=True)
            p2.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_post:+.2f}%</div><div class='metric-label'>AVG POST-EARNINGS</div></div>", unsafe_allow_html=True)
            p3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>{avg_post_beat:+.2f}%</div><div class='metric-label'>POST-EARNINGS (BEATS)</div></div>", unsafe_allow_html=True)
            p4.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#ff4444'>{avg_post_miss:+.2f}%</div><div class='metric-label'>POST-EARNINGS (MISSES)</div></div>", unsafe_allow_html=True)

            fig_pre_post = go.Figure()
            dates = [str(d.date()) for d in clean.index]
            fig_pre_post.add_trace(go.Bar(x=dates, y=clean['Pre-Earnings Return'], name='Pre-Earnings', marker_color='#00ccff', opacity=0.8))
            fig_pre_post.add_trace(go.Bar(x=dates, y=clean['Post-Earnings Return'], name='Post-Earnings', marker_color='#FFD700', opacity=0.8))
            fig_pre_post.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=350, font=dict(family='monospace'), barmode='group', yaxis_title='RETURN %')
            st.plotly_chart(fig_pre_post, use_container_width=True)

        st.markdown("<div class='section-header'>EARNINGS DETAIL</div>", unsafe_allow_html=True)
        display_df = earnings[['EPS Estimate', 'Reported EPS', 'Surprise %', 'Beat', 'Pre-Earnings Return', 'Post-Earnings Return']].copy()
        display_df.index = [str(d.date()) for d in display_df.index]
        display_df['Surprise %'] = display_df['Surprise %'].round(2)
        display_df['Pre-Earnings Return'] = display_df['Pre-Earnings Return'].round(2)
        display_df['Post-Earnings Return'] = display_df['Post-Earnings Return'].round(2)
        st.dataframe(display_df, use_container_width=True)

        st.markdown("<div class='section-header'>AI EARNINGS OUTLOOK</div>", unsafe_allow_html=True)
        if st.button("GENERATE EARNINGS OUTLOOK", type="primary", key="gen_earnings_outlook"):
            with st.spinner("Generating earnings outlook..."):
                earn_prompt = f"""You are a sell-side equity analyst specializing in earnings analysis. Analyze the following earnings data for {einfo['ticker']} and generate an institutional earnings outlook.

EARNINGS DATA:
- Beat Rate: {beat_rate:.0f}% ({int(beats)} beats, {int(misses)} misses over last {len(earnings)} quarters)
- Average EPS Surprise: {avg_surprise:+.2f}%
- Sector: {einfo['sector']}
- Current Stock Price: ${einfo['price']:.2f}

Use exactly these section labels in ALL CAPS:
EARNINGS TRACK RECORD
PRE-EARNINGS SETUP
RISK FACTORS
EARNINGS OUTLOOK

3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""

                earn_response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": "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",
                        "anthropic-version": "2023-06-01"
                    },
                    json={"model": "claude-sonnet-4-6", "max_tokens": 800, "messages": [{"role": "user", "content": earn_prompt}]}
                )
                earn_memo = earn_response.json()['content'][0]['text']
                for label in ['EARNINGS TRACK RECORD', 'PRE-EARNINGS SETUP', 'RISK FACTORS', 'EARNINGS OUTLOOK']:
                    earn_memo = earn_memo.replace(label, f"<br><span style='color:#00ff88; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
                st.session_state['earn_memo'] = earn_memo

        if 'earn_memo' in st.session_state:
            st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:8px; padding:24px; font-family:monospace; font-size:12px; line-height:2; color:#ccc;'>{st.session_state['earn_memo']}</div>", unsafe_allow_html=True)
# ====================
# TAB 5
# ====================
with tab5:
    st.markdown("<div class='section-header'>MARKET SENTIMENT ANALYSIS — NLP NEWS SCORING</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Pulls live news headlines and runs NLP sentiment scoring to generate a quantitative sentiment signal.</p>", unsafe_allow_html=True)

    NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"

    sent_ticker = st.text_input("SENTIMENT TICKER", value="AAPL", key="sent_ticker").upper()
    sent_company = st.text_input("COMPANY NAME (for news search)", value="Apple", key="sent_company")
    num_articles = st.slider("NUMBER OF ARTICLES", 10, 100, 50, key="num_articles")

    if st.button("RUN SENTIMENT ANALYSIS", type="primary", key="run_sentiment_btn"):
        with st.spinner("Pulling news and scoring sentiment..."):
            from textblob import TextBlob
            from newsapi import NewsApiClient
            from datetime import datetime, timedelta

            newsapi = NewsApiClient(api_key="04eb3eee1c894efebfd1454428228f9a")
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            articles = newsapi.get_everything(
                q=sent_company,
                from_param=from_date,
                language='en',
                sort_by='publishedAt',
                page_size=num_articles
            )

            if articles['totalResults'] > 0:
                news_data = []
                for article in articles['articles']:
                    title = article['title'] or ''
                    description = article['description'] or ''
                    text = title + ' ' + description
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity
                    if polarity > 0.1:
                        label = 'BULLISH'
                    elif polarity < -0.1:
                        label = 'BEARISH'
                    else:
                        label = 'NEUTRAL'
                    news_data.append({
                        'date': article['publishedAt'][:10],
                        'title': title[:80] + '...' if len(title) > 80 else title,
                        'source': article['source']['name'],
                        'polarity': round(polarity, 4),
                        'subjectivity': round(subjectivity, 4),
                        'sentiment': label
                    })

                news_df = pd.DataFrame(news_data)
                st.session_state['news_df'] = news_df
                st.session_state['stored_sent_ticker'] = sent_ticker
                st.session_state['stored_sent_company'] = sent_company
    if 'news_df' in st.session_state:
        news_df = st.session_state['news_df']
        sent_ticker_stored = st.session_state['stored_sent_ticker']
        bullish = len(news_df[news_df['sentiment'] == 'BULLISH'])
        bearish = len(news_df[news_df['sentiment'] == 'BEARISH'])
        neutral = len(news_df[news_df['sentiment'] == 'NEUTRAL'])
        avg_polarity = news_df['polarity'].mean()
        avg_subjectivity = news_df['subjectivity'].mean()

        if avg_polarity > 0.1:
            overall = 'BULLISH'
            overall_color = '#00ff88'
        elif avg_polarity < -0.1:
            overall = 'BEARISH'
            overall_color = '#ff4444'
        else:
            overall = 'NEUTRAL'
            overall_color = '#FFD700'

        st.markdown("<div class='section-header'>SENTIMENT SCORECARD</div>", unsafe_allow_html=True)
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.markdown(f"<div class='metric-card'><div class='metric-value' style='color:{overall_color}'>{overall}</div><div class='metric-label'>OVERALL SIGNAL</div></div>", unsafe_allow_html=True)
        s2.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_polarity:+.4f}</div><div class='metric-label'>AVG POLARITY</div></div>", unsafe_allow_html=True)
        s3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>{bullish}</div><div class='metric-label'>BULLISH ARTICLES</div></div>", unsafe_allow_html=True)
        s4.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#ff4444'>{bearish}</div><div class='metric-label'>BEARISH ARTICLES</div></div>", unsafe_allow_html=True)
        s5.markdown(f"<div class='metric-card'><div class='metric-value'>{neutral}</div><div class='metric-label'>NEUTRAL ARTICLES</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>SENTIMENT DISTRIBUTION</div>", unsafe_allow_html=True)
        col_pie, col_polar = st.columns(2)

        with col_pie:
            fig_sent_pie = go.Figure(go.Pie(
                labels=['BULLISH', 'BEARISH', 'NEUTRAL'],
                values=[bullish, bearish, neutral],
                hole=0.4,
                marker=dict(colors=['#00ff88', '#ff4444', '#FFD700'])
            ))
            fig_sent_pie.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
            st.plotly_chart(fig_sent_pie, use_container_width=True)

        with col_polar:
            fig_polar = go.Figure()
            fig_polar.add_trace(go.Histogram(
                x=news_df['polarity'],
                nbinsx=30,
                marker_color='#00ff88',
                opacity=0.7,
                name='Polarity Distribution'
            ))
            fig_polar.add_vline(x=avg_polarity, line_dash='dash', line_color='#FFD700', annotation_text=f'AVG: {avg_polarity:+.4f}')
            fig_polar.add_vline(x=0, line_color='#444')
            fig_polar.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, font=dict(family='monospace', size=10), xaxis_title='POLARITY SCORE', yaxis_title='COUNT')
            st.plotly_chart(fig_polar, use_container_width=True)

        st.markdown("<div class='section-header'>SENTIMENT OVER TIME</div>", unsafe_allow_html=True)
        daily_sent = news_df.groupby('date')['polarity'].mean().reset_index()
        daily_sent = daily_sent.sort_values('date')
        colors_sent = ['#00ff88' if p > 0.1 else '#ff4444' if p < -0.1 else '#FFD700' for p in daily_sent['polarity']]

        fig_time = go.Figure()
        fig_time.add_hline(y=0.1, line_dash='dot', line_color='#00ff88', annotation_text='BULLISH THRESHOLD')
        fig_time.add_hline(y=-0.1, line_dash='dot', line_color='#ff4444', annotation_text='BEARISH THRESHOLD')
        fig_time.add_hline(y=0, line_color='#444')
        fig_time.add_trace(go.Bar(x=daily_sent['date'], y=daily_sent['polarity'], marker_color=colors_sent, name='Daily Avg Sentiment'))
        fig_time.add_trace(go.Scatter(x=daily_sent['date'], y=daily_sent['polarity'].rolling(3).mean(), line=dict(color='#FFD700', width=2), name='3-Day MA'))
        fig_time.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=350, font=dict(family='monospace'), yaxis_title='AVG POLARITY')
        st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("<div class='section-header'>HEADLINE FEED</div>", unsafe_allow_html=True)
        for _, row in news_df.head(20).iterrows():
            color = '#00ff88' if row['sentiment'] == 'BULLISH' else '#ff4444' if row['sentiment'] == 'BEARISH' else '#FFD700'
            st.markdown(f"<div style='background:#0d1117; border-left:3px solid {color}; padding:10px 16px; margin-bottom:8px; font-family:monospace; font-size:12px;'><span style='color:{color}; font-size:10px; letter-spacing:2px;'>{row['sentiment']}</span> | <span style='color:#888; font-size:10px;'>{row['date']} | {row['source']}</span><br><span style='color:#ccc;'>{row['title']}</span><br><span style='color:#555; font-size:10px;'>POLARITY: {row['polarity']:+.4f} | SUBJECTIVITY: {row['subjectivity']:.4f}</span></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>AI SENTIMENT MEMO</div>", unsafe_allow_html=True)
        if st.button("GENERATE SENTIMENT MEMO", type="primary", key="gen_sentiment_memo"):
            with st.spinner("Generating sentiment analysis memo..."):
                sent_prompt = f"""You are a quantitative sentiment analyst at a hedge fund. Analyze the following NLP sentiment data for {sent_ticker_stored} and generate an institutional sentiment memo.

SENTIMENT DATA:
- Overall Signal: {overall}
- Average Polarity Score: {avg_polarity:+.4f} (scale: -1.0 bearish to +1.0 bullish)
- Average Subjectivity: {avg_subjectivity:.4f} (scale: 0 objective to 1.0 subjective)
- Bullish Articles: {bullish}
- Bearish Articles: {bearish}
- Neutral Articles: {neutral}
- Total Articles Analyzed: {len(news_df)}
- Time Period: Last 30 days

Use exactly these section labels in ALL CAPS:
SENTIMENT OVERVIEW
SIGNAL STRENGTH ASSESSMENT
CONTRARIAN CONSIDERATIONS
TRADING IMPLICATIONS

3-4 sentences per section. No emojis. No markdown headers. No # symbols. Always put a space after every number, dollar sign, and punctuation mark."""

                sent_response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": "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",
                        "anthropic-version": "2023-06-01"
                    },
                    json={"model": "claude-sonnet-4-6", "max_tokens": 800, "messages": [{"role": "user", "content": sent_prompt}]}
                )
                sent_memo = sent_response.json()['content'][0]['text']
                for label in ['SENTIMENT OVERVIEW', 'SIGNAL STRENGTH ASSESSMENT', 'CONTRARIAN CONSIDERATIONS', 'TRADING IMPLICATIONS']:
                    sent_memo = sent_memo.replace(label, f"<br><span style='color:#00ff88; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
                st.session_state['sent_memo'] = sent_memo

        if 'sent_memo' in st.session_state:
            st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:8px; padding:24px; font-family:monospace; font-size:12px; line-height:2; color:#ccc;'>{st.session_state['sent_memo']}</div>", unsafe_allow_html=True)
# ---- FOOTER ----
st.markdown("---")
st.markdown("<p style='color:#333; font-size:10px; text-align:center; letter-spacing:2px;'>EQUITY RESEARCH TERMINAL v2.0 | AARON DEHRING | FOR INFORMATIONAL PURPOSES ONLY | NOT INVESTMENT ADVICE</p>", unsafe_allow_html=True)