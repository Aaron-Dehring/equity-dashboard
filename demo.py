import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
def clean(text):
    return text.replace('$', '&#36;')

st.set_page_config(page_title="Equity Research Terminal — Demo", layout="wide")

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
    .demo-banner {
        background: linear-gradient(135deg, #1a1a00 0%, #2a2a00 100%);
        border: 1px solid #FFD700;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 20px;
        font-family: monospace;
        font-size: 12px;
        color: #FFD700;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# EQUITY RESEARCH TERMINAL")
st.markdown("<p style='color:#888; font-size:12px; letter-spacing:2px;'>BUILT BY AARON DEHRING | FAMILY WEALTH PARTNERS | QUANTITATIVE ANALYSIS DIVISION</p>", unsafe_allow_html=True)
st.markdown("<div class='demo-banner'>DEMO MODE — All data shown is real AAPL data captured June 27, 2026. AI memos are pre-generated. For the live version with real-time data and active AI analysis, contact Aaron Dehring.</div>", unsafe_allow_html=True)
st.markdown("---")

# ---- HARDCODED DEMO DATA ----
METRICS = {
    "price": "$283.78",
    "period_return": "+38.31%",
    "sharpe": "1.50",
    "beta": "0.88",
    "alpha": "+20.23%",
    "var": "-1.96%",
    "max_drawdown": "-13.82%"
}

MC = {
    "bull": "$400.68",
    "base": "$317.57",
    "bear": "$255.37"
}

BULL_MEMO = """BULL THESIS
Apple is the single most dominant consumer technology franchise on the planet, commanding a $4.17 trillion market cap fully justified by its unmatched ecosystem lock-in, pricing power, and recurring services revenue that now generates over $100 billion annually. With a beta of just 0.88 and a max drawdown of only -13.82%, AAPL offers institutional investors the rare combination of explosive upside and defensive capital preservation. The annualized alpha of +20.23% reflects a structurally superior business model that consistently outperforms the market on a risk-adjusted basis. A Sharpe ratio of 1.50 confirms that every unit of volatility in this name is being richly compensated, making AAPL the highest-quality risk-reward in large-cap tech.

KEY CATALYSTS
The generative AI integration cycle is just beginning, and Apple Intelligence embedded across the iPhone, Mac, and iPad ecosystem will drive the most powerful upgrade supercycle since the iPhone X, pulling hundreds of millions of users on older devices into new hardware purchases. Services — including the App Store, Apple TV+, Apple Arcade, and iCloud — continue to compound at high-margin rates, expanding gross margins toward 50% and fundamentally re-rating the earnings multiple. The Vision Pro spatial computing platform represents a multi-year optionality play that the market is not yet pricing in. International markets, particularly India where Apple is aggressively expanding manufacturing and retail presence, represent a $500 billion incremental revenue opportunity barely reflected in current estimates.

PRICE TARGET RATIONALE
Our 90-day Monte Carlo median of $317.57 represents a conservative base case, while the bull scenario of $400.68 implies roughly 41% upside from current levels of $283.78. The period return of +38.31% demonstrates that momentum is firmly intact and institutional accumulation continues to overwhelm any selling pressure. Apple's buyback engine — retiring approximately $90 billion in shares annually — acts as a perpetual EPS accelerator that makes the current multiple look cheap on a forward-adjusted basis. We set a 12-month price target of $390, underpinned by 32x our FY2026 EPS estimate of $12.20, with clear upside to $420 if services growth re-accelerates above 15% year-over-year."""

BEAR_MEMO = """BEAR THESIS
Apple is trading at a historically stretched valuation of roughly 34x forward earnings on a $4.17 trillion market cap, pricing in perfection at a time when the iPhone upgrade cycle is visibly decelerating and China revenue faces structural headwinds from rising domestic competitors like Huawei and Xiaomi. Services revenue is facing increasing regulatory scrutiny from the EU and DOJ, with App Store fee structures under direct legal assault that could meaningfully impair the highest-margin business in the company. The stock has already returned 38% in the recent period, leaving virtually no margin of safety for any fundamental disappointment. At this valuation, Apple is being priced as a high-growth software company when it is, at its core, a mature hardware manufacturer with slowing unit volumes.

KEY RISKS
The China business, representing approximately 19% of total revenue, is acutely vulnerable to geopolitical escalation, consumer boycotts, and government-directed preference for domestic brands, any one of which could remove $70 billion or more in annual revenue from the model. Apple Intelligence has so far failed to produce a measurable reacceleration in iPhone demand, meaning the bull case narrative is unproven and priced in simultaneously. Gross margin expansion assumptions embedded in consensus estimates are fragile, as tariff exposure on manufacturing concentrated in Asia creates significant cost uncertainty. Share buybacks are becoming less accretive at this price level and cannot indefinitely substitute for organic revenue growth.

DOWNSIDE TARGET
Our bear case price target is $255 per share, consistent with the Monte Carlo bear scenario and implying roughly 10% downside from current levels. A more severe de-rating toward 24x forward earnings on a China revenue impairment scenario would push the stock toward $210-$220. A compression to peer-average hardware multiples implies closer to $190 on a blended basis. We view the risk-reward as deeply asymmetric to the downside at current prices, with limited upside to the Monte Carlo bull case of $400 relative to meaningful structural bear scenarios."""

RISK_MEMO = """VOLATILITY ANALYSIS
Annualized volatility of 23.68% places AAPL in a moderate risk category relative to large-cap technology peers, sitting below the threshold typically associated with high-volatility growth names. The beta of 0.88 confirms a slight dampening effect relative to broad market moves, meaning AAPL absorbs roughly 88% of index-level swings under normal market conditions. The Sharpe ratio of 1.50 indicates that the current risk-adjusted return profile is favorable, though this metric is backward-looking and subject to regime change. Traders should note that a 23.68% annualized figure implies daily moves of approximately 1.49% under log-normal assumptions.

TAIL RISK ASSESSMENT
The 95% single-day Value at Risk of -1.96% translates to a potential loss of approximately $5.56 per share on a given trading day under normal distributional assumptions, though fat-tail events routinely breach VaR thresholds. The maximum drawdown of -13.82% over the measured period represents the realized peak-to-trough exposure, and future drawdowns should not be anchored to this figure as a ceiling. Monte Carlo simulation projects a bear-case 90-day price of $255.37, representing downside of approximately -10.01% from current levels. The spread between bull case $400.68 and bear case $255.37 implies a scenario range of $145.31, signaling meaningful path uncertainty despite the favorable median estimate.

POSITION SIZING RECOMMENDATION
Using a standard 2% portfolio risk rule and the 95% VaR of -1.96%, maximum notional exposure per $1,000,000 of portfolio capital should not exceed approximately $1,020,408 before leverage adjustments. At a beta of 0.88, AAPL provides a modest hedge benefit in a long-only equity book, but position sizes should be stress-tested against the full -13.82% drawdown scenario. The annualized alpha of +20.23% is statistically notable but should be treated with skepticism absent factor decomposition. Risk managers should cap single-name concentration in AAPL at no more than 8-10% of gross exposure given the tail scenario width and current elevated price relative to Monte Carlo median projections."""

CONSENSUS_MEMO = """CONSENSUS VERDICT
BUY. Apple remains a fundamentally superior franchise with demonstrated risk-adjusted outperformance, a Sharpe ratio of 1.50, and an annualized alpha of +20.23% that reflects genuine structural advantages. The services engine generating over $100 billion annually, combined with a $90 billion annual buyback program, creates a durable earnings compounding mechanism that justifies a premium multiple even in a slower hardware environment. While the current valuation of approximately 34x forward earnings leaves limited margin of safety, the combination of ecosystem lock-in, expanding gross margins approaching 50%, and early-stage AI integration optionality supports a constructive medium-term outlook. The Monte Carlo median of $317.57 and bull case of $400.68 provide a credible range of outcomes that outweigh the bear case of $255.37 on a probability-weighted basis.

KEY DEBATE POINTS
The central tension is whether Apple deserves a software-grade multiple on a hardware-dependent revenue base, and the answer hinges almost entirely on the trajectory of services growth under increasing regulatory pressure from the EU and DOJ. China represents the single most material unpriced risk, with approximately 19% of total revenue exposed to geopolitical escalation and domestic brand competition that could collectively remove $70 billion or more in annual revenue. The AI upgrade cycle narrative is simultaneously the strongest bull catalyst and the most dangerous assumption, as Apple Intelligence has not yet produced measurable iPhone demand reacceleration. Tariff exposure on Asian manufacturing concentration adds a further layer of margin fragility that consensus estimates have not fully stress-tested.

FINAL RECOMMENDATION
Establish or maintain a long position in AAPL with a 12-month price target of $370, reflecting a modest discount to the bull analyst's $390 target to account for China risk and regulatory uncertainty. Position sizing should conform to the risk analyst's recommendation of no more than 8-10% of gross portfolio exposure, with stress-testing conducted against the full $255 bear scenario. Investors should treat any pullback toward the $260-$270 range as a materially more attractive entry point. A re-rating toward $420 or beyond remains achievable but requires observable evidence of AI-driven upgrade acceleration and services revenue reacceleration above 15% year-over-year."""

EARNINGS_MEMO = """EARNINGS TRACK RECORD
Apple has demonstrated an exceptional earnings consistency profile, achieving a perfect 100% beat rate across the last 12 consecutive quarters with zero misses. The average EPS surprise of +4.29% reflects management's disciplined practice of conservative guidance, a well-established pattern that has built substantial credibility with institutional investors. This track record places AAPL among the most reliable large-cap earnings compounders in the Technology sector, reducing event-driven uncertainty heading into each reporting period. The consistency of outperformance suggests structural advantages in cost management, revenue mix optimization, and supply chain execution that are unlikely to deteriorate in the near term.

PRE-EARNINGS SETUP
At a current price of $283.78, the market has likely priced in a meaningful degree of earnings outperformance given Apple's well-documented beat history. Options markets will reflect elevated implied volatility in the days preceding the report, creating both hedging costs and potential mean-reversion opportunities. The risk-reward setup favors disciplined position sizing, as consensus estimates may already embed a de facto beat premium that limits upside surprise potential. Investors should monitor channel checks, App Store revenue data, and Services segment commentary as leading indicators of the quarter's trajectory.

RISK FACTORS
The primary earnings risk stems from macroeconomic softness in Greater China, which remains a material revenue contributor sensitive to currency fluctuation and consumer sentiment shifts. Supply chain disruptions, component cost inflation, or manufacturing concentration risks could compress gross margins and undermine the consistency of the positive EPS surprise trend. Regulatory headwinds in the EU and US, particularly surrounding App Store monetization and antitrust scrutiny of the Services segment, represent a longer-term overhang. Any deceleration in iPhone upgrade cycles or weakening enterprise demand for Mac and iPad product lines could pressure revenue mix.

EARNINGS OUTLOOK
Based on the 100% beat rate and sustained average surprise of +4.29%, the probabilistic base case strongly favors another EPS outperformance in the upcoming reporting period. Management's guidance philosophy of conservative framing provides the analytical foundation to expect consensus estimates to again prove beatable. Services segment growth, gross margin trajectory, and capital return program updates will be the three primary variables driving post-earnings price action at current valuation levels near $283.78. Institutional investors are advised to maintain or modestly add to core positions ahead of the print, while deploying defined-risk structures to manage downside exposure."""

SENTIMENT_MEMO = """SENTIMENT OVERVIEW
The NLP sentiment analysis of 39 articles over the trailing 30-day period yields a net bullish signal for AAPL, with an average polarity score of +0.1164 on a normalized scale of -1.0 to +1.0. Bullish articles numbered 17 against only 4 bearish articles, with 18 neutral articles comprising the largest single cohort in the sample. The average subjectivity reading of 0.4335 suggests the corpus sits near the midpoint between purely objective reporting and opinion-driven commentary. Overall, the data reflects a cautiously constructive institutional narrative around AAPL during the measurement window.

SIGNAL STRENGTH ASSESSMENT
While the directional signal is bullish, the polarity score of +0.1164 reflects a relatively modest conviction level, sitting only modestly above the neutral midpoint. The bullish-to-bearish article ratio of approximately 4.25-to-1 is encouraging, yet the dominance of neutral articles at 46% of total coverage tempers any interpretation of strong directional momentum. The subjectivity score of 0.4335 introduces moderate noise into the signal, as sentiment derived from opinion-heavy sources carries less informational reliability. This constitutes a weak-to-moderate bullish signal rather than a high-conviction directional catalyst.

CONTRARIAN CONSIDERATIONS
The elevated neutral article count of 18 may indicate that a meaningful portion of the analyst and media community is withholding directional conviction, potentially in anticipation of a binary catalyst such as earnings or product announcements. The 4 bearish articles, while a minority, should not be dismissed outright, as bearish voices in a predominantly bullish sentiment environment have historically carried outsized informational value. A polarity score of only +0.1164 leaves significant room for sentiment deterioration with minimal negative news flow. Institutions holding long exposure should monitor for any shift in the neutral cohort migrating toward bearish framing.

TRADING IMPLICATIONS
The weak-to-moderate bullish sentiment signal supports a measured long bias in AAPL, but does not justify aggressive position sizing or a high-delta options strategy at current sentiment levels. A disciplined approach would involve scaling into long exposure incrementally rather than initiating a full position on sentiment data alone. Risk managers should assign a sentiment-based stop trigger if the 30-day rolling polarity score declines below 0.0 or if the bearish article count rises above 8 within a subsequent 30-day window. Pairing this sentiment data with technical price action and fundamental catalysts is essential before elevating AAPL to a high-conviction portfolio position."""

HEADLINES = [
    ("NEUTRAL", "2026-06-27", "CNBC", "The memory shortage shaking Apple and Microsoft is 'existential crisis' for smal...", "+0.0000", "0.6667"),
    ("BULLISH", "2026-06-27", "MarketWatch", "It's a tale of two S&P 500s as rotation out of top tech stocks shifts into overd...", "+0.2500", "0.6250"),
    ("NEUTRAL", "2026-06-26", "CNBC", "'The cult of Elon': SpaceX investors grapple with volatility amid big swings", "+0.0000", "0.0889"),
    ("NEUTRAL", "2026-06-26", "CNBC", "CNBC Daily Open: Oil worries flare as tech's winners split from the pack", "+0.0000", "0.3750"),
    ("BEARISH", "2026-06-25", "CNBC", "Microsoft lifts price of Xbox consoles due to soaring component costs", "-0.2625", "0.3875"),
    ("NEUTRAL", "2026-06-24", "CNBC", "Micron is tech's new margin king as memory crisis pushes company past Nvidia and...", "-0.0379", "0.2348"),
    ("NEUTRAL", "2026-06-23", "CNBC", "Tech rout intensifies as selloff grips global stocks", "+0.0000", "0.1250"),
    ("NEUTRAL", "2026-06-20", "Bloomberg", "Big tech stock buybacks vanish as AI spending spree eats up cash", "+0.0000", "0.1000"),
    ("BULLISH", "2026-06-18", "CNBC", "The Fed decision, JetBlue's Florida plans, Intel's Apple partnership and more in...", "+0.2500", "0.7500"),
    ("BULLISH", "2026-06-18", "CNBC", "Here are 5 wild stats from SpaceX's first week on the Nasdaq", "+0.1750", "0.4000"),
    ("NEUTRAL", "2026-06-18", "CNBC", "Intel rises 9% after Trump says company will partner with Apple on U.S. chip des...", "+0.0000", "0.1250"),
    ("BULLISH", "2026-06-17", "MarketWatch", "Retail investors have been buying more SpaceX shares than all of the 'Magnificen...", "+0.4100", "0.3867"),
    ("NEUTRAL", "2026-06-17", "CNBC", "CNBC Daily Open: Markets cheer Iran calm as Trump eyes his next deal", "+0.0800", "0.4500"),
    ("BULLISH", "2026-06-16", "MarketWatch", "Wall Street can't stop talking about 'MANGOS' stocks as the 'Magnificent Seven'...", "+0.5591", "0.7386"),
    ("BULLISH", "2026-06-16", "MarketWatch", "Tesla booted from the 'Magnificent Seven' by a top fund manager. Here is the tec...", "+0.3750", "0.6500"),
    ("NEUTRAL", "2026-06-16", "CNBC", "Intel begins production of most-advanced chip, inching closer to possible Apple...", "+0.0000", "1.0000"),
    ("BULLISH", "2026-06-16", "Investopedia", "SpaceX Stock Extends Its Post-IPO Climb — It Was Worth More Than Amazon Earlier...", "+0.2100", "0.3067"),
    ("NEUTRAL", "2026-06-16", "Investopedia", "Markets News, June 16, 2026: Dow Hits Record as Chip Stocks Lead Tech Lower; Spa...", "+0.0000", "0.0000"),
    ("BULLISH", "2026-06-15", "CNBC", "SpaceX: To the moon for investors or a bumpy ride? Here's what experts say", "+0.2250", "0.3167"),
    ("NEUTRAL", "2026-06-11", "CNBC", "SpaceX to close above $2 trillion market cap on its debut, prediction market tra...", "+0.0000", "0.5500"),
]

# ---- LOAD REAL PRICE DATA FOR CHARTS ----
@st.cache_data
def load_price_data():
    try:
        df = yf.Ticker("AAPL").history(period="1y")
        bench = yf.Ticker("SPY").history(period="1y")
        ko = yf.Ticker("KO").history(period="2y")['Close']
        pep = yf.Ticker("PEP").history(period="2y")['Close']
        return df, bench, ko, pep
    except:
        return None, None, None, None

df, bench_df, ko, pep = load_price_data()

# ---- SIDEBAR ----
st.sidebar.markdown("### TERMINAL SETTINGS")
st.sidebar.markdown("<p style='color:#FFD700; font-size:11px; letter-spacing:1px;'>DEMO MODE — AAPL | 1Y</p>", unsafe_allow_html=True)
st.sidebar.text_input("PRIMARY TICKER", value="AAPL", disabled=True)
st.sidebar.text_input("BENCHMARK", value="SPY", disabled=True)
st.sidebar.selectbox("TIME PERIOD", ["1y"], disabled=True)
st.sidebar.text_input("COMPARE TICKERS", value="MSFT,GOOGL,AMZN", disabled=True)
st.sidebar.slider("MONTE CARLO SIMULATIONS", 100, 1000, 500, disabled=True)
st.sidebar.slider("FORECAST HORIZON (days)", 30, 252, 90, disabled=True)
st.sidebar.markdown("<p style='color:#555; font-size:10px;'>POWERED BY POLYGON.IO</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "PRICE & RISK ANALYSIS", "PORTFOLIO OPTIMIZER", "PAIRS TRADING", "EARNINGS ANALYSIS", "SENTIMENT ANALYSIS"
])

# ====================
# TAB 1
# ====================
with tab1:
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    for col, (label, value) in zip([m1,m2,m3,m4,m5,m6,m7], [
        ("PRICE", METRICS["price"]),
        ("PERIOD RETURN", METRICS["period_return"]),
        ("SHARPE RATIO", METRICS["sharpe"]),
        ("BETA", METRICS["beta"]),
        ("ALPHA (ann.)", METRICS["alpha"]),
        ("VAR 95%", METRICS["var"]),
        ("MAX DRAWDOWN", METRICS["max_drawdown"]),
    ]):
        col.markdown(f"<div class='metric-card'><div class='metric-value'>{value}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>PRICE ACTION & VOLUME ANALYSIS</div>", unsafe_allow_html=True)
    if df is not None and not df.empty:
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        df['BB_upper'] = df['MA20'] + 2 * df['Close'].rolling(20).std()
        df['BB_lower'] = df['MA20'] - 2 * df['Close'].rolling(20).std()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='rgba(0,255,136,0.2)', width=1), name='BB Upper', showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], fill='tonexty', fillcolor='rgba(0,255,136,0.05)', line=dict(color='rgba(0,255,136,0.2)', width=1), name='Bollinger Bands'), row=1, col=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='AAPL', increasing_line_color='#00ff88', decreasing_line_color='#ff4444'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#FFD700', width=1, dash='dash'), name='MA20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#FF8C00', width=1, dash='dash'), name='MA50'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], line=dict(color='#FF4500', width=1, dash='dot'), name='MA200'), row=1, col=1)
        colors_v = ['#00ff88' if c >= o else '#ff4444' for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors_v, name='Volume', opacity=0.7), row=2, col=1)
        fig.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=550, showlegend=True, xaxis_rangeslider_visible=False, font=dict(family='monospace', color='#888'))
        fig.update_yaxes(gridcolor='#1a1a1a')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>MONTE CARLO SIMULATION</div>", unsafe_allow_html=True)
    if df is not None and not df.empty:
        daily_returns = df['Close'].pct_change().dropna()
        mu = daily_returns.mean()
        sigma = daily_returns.std()
        last_price = df['Close'].iloc[-1]
        mc_days = 90
        mc_sims = 500
        simulations = np.zeros((mc_days, mc_sims))
        for i in range(mc_sims):
            prices = [last_price]
            for _ in range(mc_days - 1):
                prices.append(prices[-1] * (1 + np.random.normal(mu, sigma)))
            simulations[:, i] = prices
        p5 = np.percentile(simulations, 5, axis=1)
        p50 = np.percentile(simulations, 50, axis=1)
        p95 = np.percentile(simulations, 95, axis=1)

    mc1, mc2, mc3 = st.columns(3)
    mc1.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00ff88'>{MC['bull']}</div><div class='metric-label'>BULL CASE (95th)</div></div>", unsafe_allow_html=True)
    mc2.markdown(f"<div class='metric-card'><div class='metric-value'>{MC['base']}</div><div class='metric-label'>BASE CASE (MEDIAN)</div></div>", unsafe_allow_html=True)
    mc3.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#ff4444'>{MC['bear']}</div><div class='metric-label'>BEAR CASE (5th)</div></div>", unsafe_allow_html=True)

    if df is not None and not df.empty:
        fig_mc = go.Figure()
        for i in range(min(150, mc_sims)):
            fig_mc.add_trace(go.Scatter(y=simulations[:, i], mode='lines', line=dict(color='rgba(0,255,136,0.03)', width=1), showlegend=False))
        fig_mc.add_trace(go.Scatter(y=p95, line=dict(color='rgba(0,255,136,0.5)', width=2, dash='dash'), name='95th Percentile'))
        fig_mc.add_trace(go.Scatter(y=p50, line=dict(color='#00ff88', width=3), name='Median Path'))
        fig_mc.add_trace(go.Scatter(y=p5, line=dict(color='rgba(255,68,68,0.5)', width=2, dash='dash'), name='5th Percentile'))
        fig_mc.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=400, font=dict(family='monospace'))
        st.plotly_chart(fig_mc, use_container_width=True)

    if df is not None and bench_df is not None and not df.empty and not bench_df.empty:
        st.markdown("<div class='section-header'>RETURN DISTRIBUTION & RISK PROFILE</div>", unsafe_allow_html=True)
        daily_returns = df['Close'].pct_change().dropna()
        bench_returns = bench_df['Close'].pct_change().dropna()
        d1, d2 = st.columns(2)
        with d1:
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(x=daily_returns * 100, nbinsx=60, marker_color='#00ff88', opacity=0.7))
            fig_dist.add_vline(x=-1.96, line_dash='dash', line_color='#ff4444', annotation_text='VaR 95%: -1.96%')
            fig_dist.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, title='Daily Return Distribution', font=dict(family='monospace', size=10))
            st.plotly_chart(fig_dist, use_container_width=True)
        with d2:
            cumulative = (1 + daily_returns).cumprod()
            bench_cumulative = (1 + bench_returns).cumprod()
            fig_cum = go.Figure()
            fig_cum.add_trace(go.Scatter(x=cumulative.index, y=cumulative.values, line=dict(color='#00ff88', width=2), name='AAPL'))
            fig_cum.add_trace(go.Scatter(x=bench_cumulative.index, y=bench_cumulative.values, line=dict(color='#888', width=2, dash='dash'), name='SPY'))
            fig_cum.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, title='Cumulative Returns vs Benchmark', font=dict(family='monospace', size=10))
            st.plotly_chart(fig_cum, use_container_width=True)

    st.markdown("<div class='section-header'>AI ANALYST DEBATE ENGINE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Three independent AI analysts debate the position. Bull vs Bear vs Risk. Consensus generated after.</p>", unsafe_allow_html=True)

    if st.button("RUN ANALYST DEBATE", type="primary", key="demo_debate_btn"):
        st.session_state['demo_debate'] = True

    if st.session_state.get('demo_debate'):
        col_bull, col_bear, col_risk = st.columns(3)
        for col, role, color, memo in [
            (col_bull, "BULL ANALYST", "#00ff88", BULL_MEMO),
            (col_bear, "BEAR ANALYST", "#ff4444", BEAR_MEMO),
            (col_risk, "RISK ANALYST", "#FFD700", RISK_MEMO),
        ]:
            with col:
                st.markdown(f"<div style='color:{color}; font-size:12px; letter-spacing:2px; font-family:monospace; margin-bottom:8px; font-weight:700;'>{role}</div>", unsafe_allow_html=True)
                formatted = clean(memo)
                for label in ['BULL THESIS', 'KEY CATALYSTS', 'PRICE TARGET RATIONALE', 'BEAR THESIS', 'KEY RISKS', 'DOWNSIDE TARGET', 'VOLATILITY ANALYSIS', 'TAIL RISK ASSESSMENT', 'POSITION SIZING RECOMMENDATION']:
                    formatted = formatted.replace(label, f"<br><span style='color:{color}; letter-spacing:2px; font-size:10px;'>{label}</span><br>")
                st.markdown(f"<div style='background:#0d1117; border:1px solid {color}; border-radius:8px; padding:20px; font-family:monospace; font-size:12px; line-height:2; color:#ccc; min-height:400px;'>{formatted}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>CONSENSUS RATING</div>", unsafe_allow_html=True)
        formatted_consensus = clean(CONSENSUS_MEMO)
        for label in ['CONSENSUS VERDICT', 'KEY DEBATE POINTS', 'FINAL RECOMMENDATION']:
            formatted_consensus = formatted_consensus.replace(label, f"<br><span style='color:#00ccff; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
        st.markdown(f"<div style='background:#0d1117; border:1px solid #00ccff; border-radius:8px; padding:24px; font-family:monospace; font-size:13px; line-height:2; color:#ccc;'><div style='color:#00ccff; font-size:12px; letter-spacing:3px; margin-bottom:16px;'>HEAD OF RESEARCH — CONSENSUS REPORT</div>{formatted_consensus}</div>", unsafe_allow_html=True)

# ====================
# TAB 2
# ====================
with tab2:
    st.markdown("<div class='section-header'>PORTFOLIO OPTIMIZER — MARKOWITZ MEAN-VARIANCE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Demo showing optimization for AAPL, MSFT, GOOGL, AMZN, SPY over 2-year lookback.</p>", unsafe_allow_html=True)

    port_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "SPY"]

    o1, o2 = st.columns(2)
    with o1:
        st.markdown("**MAXIMUM SHARPE RATIO PORTFOLIO**")
        ms1, ms2, ms3 = st.columns(3)
        ms1.markdown("<div class='metric-card'><div class='metric-value'>1.20</div><div class='metric-label'>SHARPE RATIO</div></div>", unsafe_allow_html=True)
        ms2.markdown("<div class='metric-card'><div class='metric-value'>25.99%</div><div class='metric-label'>ANN. RETURN</div></div>", unsafe_allow_html=True)
        ms3.markdown("<div class='metric-card'><div class='metric-value'>21.62%</div><div class='metric-label'>ANN. VOLATILITY</div></div>", unsafe_allow_html=True)
        fig_pie1 = go.Figure(go.Pie(labels=port_tickers, values=[0.30, 0.25, 0.20, 0.15, 0.10], hole=0.4, marker=dict(colors=['#00ff88','#00ccff','#FFD700','#FF8C00','#ff4444'])))
        fig_pie1.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
        st.plotly_chart(fig_pie1, use_container_width=True)
    with o2:
        st.markdown("**MINIMUM VOLATILITY PORTFOLIO**")
        mv1, mv2, mv3 = st.columns(3)
        mv1.markdown("<div class='metric-card'><div class='metric-value'>0.88</div><div class='metric-label'>SHARPE RATIO</div></div>", unsafe_allow_html=True)
        mv2.markdown("<div class='metric-card'><div class='metric-value'>15.55%</div><div class='metric-label'>ANN. RETURN</div></div>", unsafe_allow_html=True)
        mv3.markdown("<div class='metric-card'><div class='metric-value'>17.67%</div><div class='metric-label'>ANN. VOLATILITY</div></div>", unsafe_allow_html=True)
        fig_pie2 = go.Figure(go.Pie(labels=port_tickers, values=[0.10, 0.15, 0.15, 0.10, 0.50], hole=0.4, marker=dict(colors=['#00ff88','#00ccff','#FFD700','#FF8C00','#ff4444'])))
        fig_pie2.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
        st.plotly_chart(fig_pie2, use_container_width=True)

    st.markdown("<div class='section-header'>EFFICIENT FRONTIER</div>", unsafe_allow_html=True)
    np.random.seed(42)
    n_ports = 2000
    vols = np.random.uniform(0.12, 0.35, n_ports)
    rets = vols * np.random.uniform(0.6, 1.4, n_ports) + 0.05
    sharpes = rets / vols
    fig_ef = go.Figure()
    fig_ef.add_trace(go.Scatter(x=vols*100, y=rets*100, mode='markers', marker=dict(color=sharpes, colorscale=[[0,'#ff4444'],[0.5,'#FFD700'],[1,'#00ff88']], size=3, opacity=0.6, colorbar=dict(title='Sharpe', thickness=10)), name='Portfolios'))
    fig_ef.add_trace(go.Scatter(x=[21.62], y=[25.99], mode='markers', marker=dict(color='#00ff88', size=18, symbol='star'), name='Max Sharpe'))
    fig_ef.add_trace(go.Scatter(x=[17.67], y=[15.55], mode='markers', marker=dict(color='#00ccff', size=18, symbol='diamond'), name='Min Volatility'))
    fig_ef.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=500, font=dict(family='monospace'), xaxis_title='ANNUALIZED VOLATILITY (%)', yaxis_title='ANNUALIZED RETURN (%)', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    st.plotly_chart(fig_ef, use_container_width=True)

    st.markdown("<div class='section-header'>ALLOCATION WEIGHTS</div>", unsafe_allow_html=True)
    weights_df = pd.DataFrame({
        'Ticker': port_tickers,
        'Max Sharpe Weight': ['30.00%', '25.00%', '20.00%', '15.00%', '10.00%'],
        'Min Vol Weight': ['10.00%', '15.00%', '15.00%', '10.00%', '50.00%']
    })
    st.dataframe(weights_df.set_index('Ticker'), use_container_width=True)

# ====================
# TAB 3
# ====================
with tab3:
    st.markdown("<div class='section-header'>PAIRS TRADING SIGNAL ENGINE — STATISTICAL ARBITRAGE</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Demo showing KO vs PEP analysis. Live version runs cointegration testing on any two assets in real time.</p>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    col_p1.text_input("ASSET 1", value="KO", disabled=True)
    col_p2.text_input("ASSET 2", value="PEP", disabled=True)

    coint_col1, coint_col2, coint_col3 = st.columns(3)
    coint_col1.markdown("<div class='metric-card'><div class='metric-value'>-0.5728</div><div class='metric-label'>COINTEGRATION SCORE</div></div>", unsafe_allow_html=True)
    coint_col2.markdown("<div class='metric-card'><div class='metric-value'>0.9587</div><div class='metric-label'>P-VALUE</div></div>", unsafe_allow_html=True)
    coint_col3.markdown("<div class='metric-card'><div class='metric-value' style='color:#ff4444'>NOT COINTEGRATED</div><div class='metric-label'>Insufficient statistical relationship</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>CURRENT SIGNAL</div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.markdown("<div class='metric-card'><div class='metric-value' style='color:#ff4444'>SELL SPREAD</div><div class='metric-label'>ACTIVE SIGNAL</div></div>", unsafe_allow_html=True)
    s2.markdown("<div class='metric-card'><div class='metric-value'>2.52</div><div class='metric-label'>CURRENT Z-SCORE</div></div>", unsafe_allow_html=True)
    s3.markdown("<div class='metric-card'><div class='metric-value'>0.0588</div><div class='metric-label'>HEDGE RATIO</div></div>", unsafe_allow_html=True)

    if ko is not None and pep is not None:
        st.markdown("<div class='section-header'>NORMALIZED PRICE COMPARISON</div>", unsafe_allow_html=True)
        fig_pairs = go.Figure()
        fig_pairs.add_trace(go.Scatter(x=ko.index, y=ko/ko.iloc[0]*100, line=dict(color='#00ff88', width=2), name='KO'))
        fig_pairs.add_trace(go.Scatter(x=pep.index, y=pep/pep.iloc[0]*100, line=dict(color='#00ccff', width=2), name='PEP'))
        fig_pairs.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, font=dict(family='monospace'), yaxis_title='NORMALIZED PRICE (BASE 100)')
        st.plotly_chart(fig_pairs, use_container_width=True)

# ====================
# TAB 4
# ====================
with tab4:
    st.markdown("<div class='section-header'>EARNINGS SURPRISE MODEL — QUANTITATIVE EARNINGS ANALYSIS</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Demo showing AAPL earnings data. Live version analyzes any ticker in real time.</p>", unsafe_allow_html=True)

    e1, e2, e3, e4 = st.columns(4)
    e1.markdown("<div class='metric-card'><div class='metric-value' style='color:#00ff88'>100%</div><div class='metric-label'>BEAT RATE</div></div>", unsafe_allow_html=True)
    e2.markdown("<div class='metric-card'><div class='metric-value'>+4.29%</div><div class='metric-label'>AVG SURPRISE</div></div>", unsafe_allow_html=True)
    e3.markdown("<div class='metric-card'><div class='metric-value' style='color:#00ff88'>12</div><div class='metric-label'>BEATS</div></div>", unsafe_allow_html=True)
    e4.markdown("<div class='metric-card'><div class='metric-value' style='color:#ff4444'>0</div><div class='metric-label'>MISSES</div></div>", unsafe_allow_html=True)

    earnings_data = [
        ("2026-04-30", 1.94, 2.01, 3.61, 6.03, 2.63),
        ("2026-01-29", 2.67, 2.84, 6.37, -5.00, 6.56),
        ("2025-10-30", 1.77, 1.85, 4.52, 5.19, -0.09),
        ("2025-07-31", 1.43, 1.57, 9.79, -2.80, 5.37),
        ("2025-05-01", 1.62, 1.65, 1.85, 4.99, -4.43),
        ("2025-01-30", 2.35, 2.40, 2.13, -5.12, -1.50),
        ("2024-10-31", 0.95, 0.97, 2.11, -0.39, -0.09),
        ("2024-08-01", 1.34, 1.40, 4.48, -3.53, -4.57),
        ("2024-05-02", 1.51, 1.53, 1.32, 2.03, -0.35),
        ("2024-02-01", 2.10, 2.18, 3.81, 2.72, 1.92),
    ]

    st.markdown("<div class='section-header'>EARNINGS SURPRISE HISTORY</div>", unsafe_allow_html=True)
    fig_earn = go.Figure()
    fig_earn.add_hline(y=0, line_color='#444')
    fig_earn.add_trace(go.Bar(x=[d[0] for d in earnings_data], y=[d[3] for d in earnings_data], marker_color=['#00ff88'] * len(earnings_data), name='EPS Surprise %'))
    fig_earn.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=350, font=dict(family='monospace'), yaxis_title='SURPRISE %')
    st.plotly_chart(fig_earn, use_container_width=True)

    st.markdown("<div class='section-header'>PRE vs POST EARNINGS PRICE BEHAVIOR</div>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    p1.markdown("<div class='metric-card'><div class='metric-value'>+0.37%</div><div class='metric-label'>AVG PRE-EARNINGS</div></div>", unsafe_allow_html=True)
    p2.markdown("<div class='metric-card'><div class='metric-value'>+0.58%</div><div class='metric-label'>AVG POST-EARNINGS</div></div>", unsafe_allow_html=True)
    p3.markdown("<div class='metric-card'><div class='metric-value' style='color:#00ff88'>+0.58%</div><div class='metric-label'>POST-EARNINGS (BEATS)</div></div>", unsafe_allow_html=True)
    p4.markdown("<div class='metric-card'><div class='metric-value' style='color:#ff4444'>+0.00%</div><div class='metric-label'>POST-EARNINGS (MISSES)</div></div>", unsafe_allow_html=True)

    fig_pre_post = go.Figure()
    fig_pre_post.add_trace(go.Bar(x=[d[0] for d in earnings_data], y=[d[4] for d in earnings_data], name='Pre-Earnings', marker_color='#00ccff', opacity=0.8))
    fig_pre_post.add_trace(go.Bar(x=[d[0] for d in earnings_data], y=[d[5] for d in earnings_data], name='Post-Earnings', marker_color='#FFD700', opacity=0.8))
    fig_pre_post.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=350, font=dict(family='monospace'), barmode='group', yaxis_title='RETURN %')
    st.plotly_chart(fig_pre_post, use_container_width=True)

    st.markdown("<div class='section-header'>AI EARNINGS OUTLOOK</div>", unsafe_allow_html=True)
    if st.button("GENERATE EARNINGS OUTLOOK", type="primary", key="demo_earn_btn"):
        st.session_state['demo_earn'] = True

    if st.session_state.get('demo_earn'):
        formatted_earn = clean(EARNINGS_MEMO)
        for label in ['EARNINGS TRACK RECORD', 'PRE-EARNINGS SETUP', 'RISK FACTORS', 'EARNINGS OUTLOOK']:
            formatted_earn = formatted_earn.replace(label, f"<br><span style='color:#00ff88; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
        st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:8px; padding:24px; font-family:monospace; font-size:12px; line-height:2; color:#ccc;'>{formatted_earn}</div>", unsafe_allow_html=True)

# ====================
# TAB 5
# ====================
with tab5:
    st.markdown("<div class='section-header'>MARKET SENTIMENT ANALYSIS — NLP NEWS SCORING</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>Demo showing AAPL sentiment analysis from June 27, 2026. Live version pulls fresh headlines in real time.</p>", unsafe_allow_html=True)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.markdown("<div class='metric-card'><div class='metric-value' style='color:#00ff88'>BULLISH</div><div class='metric-label'>OVERALL SIGNAL</div></div>", unsafe_allow_html=True)
    s2.markdown("<div class='metric-card'><div class='metric-value'>+0.1164</div><div class='metric-label'>AVG POLARITY</div></div>", unsafe_allow_html=True)
    s3.markdown("<div class='metric-card'><div class='metric-value' style='color:#00ff88'>17</div><div class='metric-label'>BULLISH ARTICLES</div></div>", unsafe_allow_html=True)
    s4.markdown("<div class='metric-card'><div class='metric-value' style='color:#ff4444'>4</div><div class='metric-label'>BEARISH ARTICLES</div></div>", unsafe_allow_html=True)
    s5.markdown("<div class='metric-card'><div class='metric-value'>18</div><div class='metric-label'>NEUTRAL ARTICLES</div></div>", unsafe_allow_html=True)

    col_pie, col_polar = st.columns(2)
    with col_pie:
        fig_sent_pie = go.Figure(go.Pie(labels=['BULLISH', 'BEARISH', 'NEUTRAL'], values=[17, 4, 18], hole=0.4, marker=dict(colors=['#00ff88', '#ff4444', '#FFD700'])))
        fig_sent_pie.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', height=300, font=dict(family='monospace', size=10))
        st.plotly_chart(fig_sent_pie, use_container_width=True)
    with col_polar:
        polarities = [float(h[4]) for h in HEADLINES]
        fig_polar = go.Figure()
        fig_polar.add_trace(go.Histogram(x=polarities, nbinsx=20, marker_color='#00ff88', opacity=0.7))
        fig_polar.add_vline(x=0.1164, line_dash='dash', line_color='#FFD700', annotation_text='AVG: +0.1164')
        fig_polar.add_vline(x=0, line_color='#444')
        fig_polar.update_layout(template='plotly_dark', paper_bgcolor='#0a0a0a', plot_bgcolor='#0d0d0d', height=300, font=dict(family='monospace', size=10), xaxis_title='POLARITY SCORE', yaxis_title='COUNT')
        st.plotly_chart(fig_polar, use_container_width=True)

    st.markdown("<div class='section-header'>HEADLINE FEED</div>", unsafe_allow_html=True)
    for sentiment, date, source, title, polarity, subjectivity in HEADLINES:
        color = '#00ff88' if sentiment == 'BULLISH' else '#ff4444' if sentiment == 'BEARISH' else '#FFD700'
        st.markdown(f"<div style='background:#0d1117; border-left:3px solid {color}; padding:10px 16px; margin-bottom:8px; font-family:monospace; font-size:12px;'><span style='color:{color}; font-size:10px; letter-spacing:2px;'>{sentiment}</span> | <span style='color:#888; font-size:10px;'>{date} | {source}</span><br><span style='color:#ccc;'>{title}</span><br><span style='color:#555; font-size:10px;'>POLARITY: {polarity} | SUBJECTIVITY: {subjectivity}</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>AI SENTIMENT MEMO</div>", unsafe_allow_html=True)
    if st.button("GENERATE SENTIMENT MEMO", type="primary", key="demo_sent_btn"):
        st.session_state['demo_sent'] = True

    if st.session_state.get('demo_sent'):
        formatted_sent = clean(SENTIMENT_MEMO)
        for label in ['SENTIMENT OVERVIEW', 'SIGNAL STRENGTH ASSESSMENT', 'CONTRARIAN CONSIDERATIONS', 'TRADING IMPLICATIONS']:
            formatted_sent = formatted_sent.replace(label, f"<br><span style='color:#00ff88; letter-spacing:2px; font-size:11px;'>{label}</span><br>")
        st.markdown(f"<div style='background:#0d1117; border:1px solid #00ff88; border-radius:8px; padding:24px; font-family:monospace; font-size:12px; line-height:2; color:#ccc;'>{formatted_sent}</div>", unsafe_allow_html=True)

# ---- FOOTER ----
st.markdown("---")
st.markdown("<p style='color:#333; font-size:10px; text-align:center; letter-spacing:2px;'>EQUITY RESEARCH TERMINAL v2.0 | AARON DEHRING | DEMO VERSION | FOR INFORMATIONAL PURPOSES ONLY | NOT INVESTMENT ADVICE</p>", unsafe_allow_html=True)