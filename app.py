import html
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. PAGE CONFIGURATION (FULL-BLEED WEB APP)
# ==============================================================================
st.set_page_config(
    page_title="SPG-X // Enterprise Solar Telemetry & Forecasting",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. FLUID FULL-SCREEN, BLANK-CANVAS BOOT & 3D SCROLL-POP DESIGN SYSTEM
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {
    --bg-base: #04070d;
    --bg-panel: rgba(10, 16, 29, 0.84);
    --bg-panel-solid: #0a101d;
    --border-subtle: rgba(148, 163, 184, 0.16);
    --border-hover: rgba(245, 158, 11, 0.7);
    --accent-amber: #f59e0b;
    --accent-cyan: #0ea5e9;
    --accent-emerald: #10b981;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

*, *::before, *::after {
    box-sizing: border-box;
}

/* Lock Horizontal Overflow Globally (Strict Vertical Scroll Only) */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    overflow-x: hidden !important;
    max-width: 100% !important;
    scroll-behavior: smooth;
}

/* Hide Streamlit Top Bar & Deploy Button so Hero Never Overlaps */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
#MainMenu,
footer {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}

.stApp {
    background-color: var(--bg-base);
    background-image:
        radial-gradient(circle at 10% 10%, rgba(14, 165, 233, 0.1) 0px, transparent 38%),
        radial-gradient(circle at 90% 8%, rgba(245, 158, 11, 0.1) 0px, transparent 40%),
        radial-gradient(circle at 50% 92%, rgba(16, 185, 129, 0.06) 0px, transparent 45%),
        linear-gradient(rgba(148, 163, 184, 0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.022) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 100% 100%, 38px 38px, 38px 38px;
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding-top: 0.9rem !important;
    padding-left: 1.4rem !important;
    padding-right: 1.4rem !important;
    padding-bottom: 3rem !important;
    margin: 0 auto !important;
}

/* ==========================================================================
   BLANK-CANVAS BOOT LOCK (HIDES ALL BRICKS UNTIL SWARM BUILDS THEM)
   ========================================================================== */
@keyframes safetyFallbackReveal {
    to { opacity: 1; transform: none; }
}

body:not(.spgx-build-complete) .corp-header,
body:not(.spgx-build-complete) .marquee-shell,
body:not(.spgx-build-complete) div[data-testid="stTabs"] > div[role="tablist"],
body:not(.spgx-build-complete) .section-strip,
body:not(.spgx-build-complete) div[data-testid="stSelectbox"],
body:not(.spgx-build-complete) div[data-testid="stCheckbox"],
body:not(.spgx-build-complete) div[data-testid="stTextInput"],
body:not(.spgx-build-complete) div[data-testid="stExpander"],
body:not(.spgx-build-complete) div[data-testid="stSlider"],
body:not(.spgx-build-complete) .telemetry-bar,
body:not(.spgx-build-complete) .kpi-card,
body:not(.spgx-build-complete) .yield-hero,
body:not(.spgx-build-complete) div[data-testid="stPlotlyChart"],
body:not(.spgx-build-complete) .map-caption-strip,
body:not(.spgx-build-complete) .arch-card {
    opacity: 0;
    transform: perspective(1000px) rotateX(16deg) translateY(24px) scale(0.94);
    animation: safetyFallbackReveal 0.6s ease 15s forwards;
}

/* Class applied by Swarm Engine the moment a brick finishes construction */
.spgx-brick-built {
    opacity: 1 !important;
    transform: perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1) !important;
    transition:
        opacity 0.62s cubic-bezier(0.16, 1, 0.3, 1),
        transform 0.68s cubic-bezier(0.22, 1.28, 0.36, 1),
        border-color 0.3s ease,
        box-shadow 0.35s ease !important;
    animation: none !important;
}

/* ==========================================================================
   KEYFRAMES FOR POST-BUILD HOVER, FLOATING & HOLOGRAPHIC EFFECTS
   ========================================================================== */
@keyframes tileFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}

@keyframes holoSweep {
    0% { transform: translateX(-140%) skewX(-22deg); }
    35%, 100% { transform: translateX(220%) skewX(-22deg); }
}

@keyframes marqueeRoll {
    0% { transform: translateX(0%); }
    100% { transform: translateX(-50%); }
}

@keyframes statusPulse {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { box-shadow: 0 0 0 9px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@keyframes borderGlowSweep {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ==========================================================================
   HERO HEADER BANNER
   ========================================================================== */
.corp-header {
    position: relative;
    width: 100%;
    border-radius: 16px;
    background:
        linear-gradient(105deg, rgba(4, 7, 13, 0.95) 0%, rgba(10, 16, 29, 0.88) 58%, rgba(14, 165, 233, 0.15) 100%),
        url('https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=2000&q=80') center 38% / cover no-repeat;
    border: 1px solid rgba(148, 163, 184, 0.22);
    padding: 1.45rem 1.8rem;
    margin-bottom: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.1rem;
    box-shadow: 0 20px 48px -15px rgba(0, 0, 0, 0.8);
    overflow: hidden;
}

.corp-header::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-amber), var(--accent-cyan), var(--accent-emerald), var(--accent-amber));
    background-size: 300% 100%;
    animation: borderGlowSweep 5s ease infinite;
}

.brand-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-amber);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.35rem;
    line-height: 1.35;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    min-width: 8px;
    border-radius: 50%;
    background: var(--accent-emerald);
    display: inline-block;
    animation: statusPulse 2s infinite;
}

.brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.3rem, 2.2vw, 2rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin: 0 0 0.28rem 0;
    line-height: 1.18;
}

.brand-subtitle {
    color: var(--text-secondary);
    font-size: clamp(0.77rem, 1vw, 0.88rem);
    margin: 0;
    max-width: 680px;
    line-height: 1.45;
}

.header-meta-grid {
    display: grid;
    grid-template-columns: repeat(3, auto);
    gap: 1.2rem;
    background: rgba(4, 7, 13, 0.85);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    padding: 0.7rem 1.1rem;
}

.meta-item {
    display: flex;
    flex-direction: column;
}

.meta-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.59rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.meta-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.79rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 2px;
}

/* ==========================================================================
   INFINITE ROLLING MARQUEE TICKER
   ========================================================================== */
.marquee-shell {
    display: flex;
    align-items: center;
    width: 100%;
    background: rgba(10, 16, 29, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 10px;
    padding: 0.45rem 0.85rem;
    margin-bottom: 1rem;
    overflow: hidden;
    position: relative;
}

.marquee-pin {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    color: var(--accent-amber);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    padding-right: 0.8rem;
    border-right: 1px solid rgba(148, 163, 184, 0.2);
    white-space: nowrap;
    z-index: 2;
    background: rgba(10, 16, 29, 0.96);
}

.marquee-viewport {
    overflow: hidden;
    flex: 1;
    min-width: 0;
    mask-image: linear-gradient(to right, transparent 0%, black 4%, black 96%, transparent 100%);
}

.marquee-track {
    display: flex;
    width: max-content;
    gap: 0.6rem;
    padding-left: 0.75rem;
    animation: marqueeRoll 24s linear infinite;
}

.marquee-shell:hover .marquee-track {
    animation-play-state: paused;
}

.api-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.69rem;
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.2);
    padding: 3px 11px;
    border-radius: 999px;
    white-space: nowrap;
    transition: all 0.25s cubic-bezier(0.22, 1.28, 0.36, 1);
}

.api-badge:hover {
    border-color: var(--accent-amber);
    color: #ffffff;
    transform: translateY(-2px) scale(1.05);
}

.api-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-amber);
    box-shadow: 0 0 8px var(--accent-amber);
}

/* ==========================================================================
   COMPACT SECTION HEADER STRIP
   ========================================================================== */
.section-strip {
    width: 100%;
    background: linear-gradient(90deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 16, 29, 0.82) 100%);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-left: 3px solid var(--accent-amber);
    border-radius: 11px;
    padding: 0.68rem 1rem;
    margin-bottom: 0.55rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    box-shadow: 0 10px 24px -10px rgba(0, 0, 0, 0.6);
}

.panel-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.93rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.panel-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--accent-cyan);
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.35);
    padding: 3px 9px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.map-caption-strip {
    width: 100%;
    background: rgba(10, 16, 29, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 9px;
    padding: 0.48rem 0.85rem;
    margin-top: -0.35rem;
    margin-bottom: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
}

/* ==========================================================================
   KPI TELEMETRY DECK (HOLO-SWEEP + POP-UP HOVER)
   ========================================================================== */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.85rem;
    width: 100%;
    margin-bottom: 1rem;
    perspective: 1100px;
}

.kpi-card {
    background: linear-gradient(160deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 16, 29, 0.96) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 13px;
    padding: 0.95rem 1.05rem;
    position: relative;
    overflow: hidden;
    min-width: 0;
    transform-style: preserve-3d;
    transition: transform 0.38s cubic-bezier(0.22, 1.28, 0.36, 1), border-color 0.3s ease, box-shadow 0.38s ease;
}

.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 45%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.055), transparent);
    transform: translateX(-140%) skewX(-22deg);
    animation: holoSweep 7s ease-in-out infinite;
    pointer-events: none;
}

.kpi-card:nth-child(2)::before { animation-delay: 1.2s; }
.kpi-card:nth-child(3)::before { animation-delay: 2.4s; }
.kpi-card:nth-child(4)::before { animation-delay: 3.6s; }
.kpi-card:nth-child(5)::before { animation-delay: 4.8s; }

.kpi-card::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-amber), var(--accent-cyan), var(--accent-emerald));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.35s cubic-bezier(0.22, 1.28, 0.36, 1);
}

.kpi-card:hover, .kpi-card:active {
    transform: perspective(800px) rotateX(7deg) rotateY(-5deg) translateY(-7px) scale(1.035) !important;
    border-color: var(--border-hover);
    box-shadow: 0 18px 34px -8px rgba(0, 0, 0, 0.8), 0 0 24px rgba(245, 158, 11, 0.18);
}

.kpi-card:hover::after, .kpi-card:active::after {
    transform: scaleX(1);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}

.kpi-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-secondary);
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(1.18rem, 1.5vw, 1.48rem);
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.15;
}

.kpi-unit {
    font-size: 0.76rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-left: 3px;
}

.kpi-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.32rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Primary Power Yield Readout Hero */
.yield-hero {
    position: relative;
    overflow: hidden;
    width: 100%;
    background: linear-gradient(125deg, rgba(10, 16, 29, 0.96) 0%, rgba(15, 23, 42, 0.92) 55%, rgba(245, 158, 11, 0.18) 100%);
    border: 1px solid rgba(245, 158, 11, 0.45);
    border-left: 5px solid var(--accent-amber);
    border-radius: 14px;
    padding: 1.3rem 1.65rem;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    box-shadow: 0 20px 44px -12px rgba(0, 0, 0, 0.68);
    transition: transform 0.38s cubic-bezier(0.22, 1.28, 0.36, 1), box-shadow 0.38s ease;
}

.yield-hero::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 35%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.09), transparent);
    transform: translateX(-140%) skewX(-22deg);
    animation: holoSweep 6.5s ease-in-out infinite;
    pointer-events: none;
}

.yield-hero:hover {
    transform: perspective(1000px) rotateX(3deg) translateY(-4px) scale(1.01) !important;
    box-shadow: 0 24px 52px -10px rgba(245, 158, 11, 0.25);
}

.yield-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: var(--accent-amber);
    margin-bottom: 0.25rem;
}

.yield-location {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(0.98rem, 1.4vw, 1.2rem);
    font-weight: 700;
    color: var(--text-primary);
}

.yield-note {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

.yield-number-box {
    text-align: right;
}

.yield-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(2rem, 3.2vw, 2.8rem);
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    letter-spacing: -0.03em;
    text-shadow: 0 0 28px rgba(245, 158, 11, 0.38);
}

.yield-unit {
    font-size: 1rem;
    font-weight: 600;
    color: var(--accent-amber);
    margin-left: 6px;
}

/* Telemetry Status Strip */
.telemetry-bar {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.6rem;
    background: rgba(10, 16, 29, 0.92);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 0.65rem 1.05rem;
    margin-bottom: 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    color: var(--text-secondary);
}

.status-pill-day {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.5);
    color: #fbbf24;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.67rem;
}

.status-pill-night {
    background: rgba(14, 165, 233, 0.14);
    border: 1px solid rgba(14, 165, 233, 0.45);
    color: #38bdf8;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.67rem;
}

/* Segmented Corporate Tabs */
div[data-testid="stTabs"] > div[role="tablist"] {
    background: var(--bg-panel-solid);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 6px;
    gap: 6px;
    margin-bottom: 1.05rem;
    display: flex;
    flex-wrap: wrap;
}

div[data-testid="stTabs"] button[role="tab"] {
    border-radius: 8px !important;
    padding: 0.5rem 1.05rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    transition: all 0.25s cubic-bezier(0.22, 1.28, 0.36, 1) !important;
}

div[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.04) !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.18), rgba(14, 165, 233, 0.12)) !important;
    color: #ffffff !important;
    border: 1px solid rgba(245, 158, 11, 0.5) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
}

div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Footer Architecture Grid */
.arch-footer {
    width: 100%;
    margin-top: 2rem;
    padding-top: 1.3rem;
    border-top: 1px solid var(--border-subtle);
}

.arch-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin-top: 0.8rem;
}

.arch-card {
    background: rgba(10, 16, 29, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    transition: all 0.36s cubic-bezier(0.22, 1.28, 0.36, 1);
}

.arch-card:hover {
    border-color: rgba(245, 158, 11, 0.6);
    transform: perspective(800px) rotateX(5deg) translateY(-6px) scale(1.02) !important;
    box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.65);
}

.arch-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    color: var(--accent-amber);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.arch-provider {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0.2rem 0;
}

.arch-desc {
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.45;
}

/* Input Refinements */
div[data-testid="stNumberInput"] > div > div > input,
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stSelectbox"] > div > div {
    background-color: #070b14 !important;
    border: 1px solid rgba(148, 163, 184, 0.24) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ==========================================================================
   MOBILE & PHONE VIEWPORT OPTIMIZATION (FIXED HORIZONTAL, FLUID VERTICAL)
   ========================================================================== */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.6rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-bottom: 2.5rem !important;
    }

    .corp-header {
        padding: 1.15rem 1.1rem;
        border-radius: 14px;
        gap: 0.85rem;
    }

    .brand-eyebrow {
        font-size: 0.61rem;
        letter-spacing: 0.08em;
    }

    .brand-title {
        font-size: 1.32rem;
        line-height: 1.22;
    }

    .brand-subtitle {
        font-size: 0.77rem;
    }

    .header-meta-grid {
        width: 100%;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.45rem;
        padding: 0.6rem 0.7rem;
    }

    .meta-label { font-size: 0.53rem; }
    .meta-val { font-size: 0.66rem; word-break: break-word; }

    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 0.65rem;
    }

    .kpi-grid > .kpi-card:last-child:nth-child(odd) {
        grid-column: span 2;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        flex: 1 1 100%;
        justify-content: flex-start !important;
        font-size: 0.71rem !important;
        padding: 0.48rem 0.85rem !important;
    }

    .yield-hero {
        padding: 1.1rem 1.15rem;
        flex-direction: column;
        align-items: flex-start;
    }

    .yield-number-box {
        text-align: left;
        width: 100%;
        padding-top: 0.45rem;
        border-top: 1px solid rgba(148, 163, 184, 0.14);
    }

    .arch-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. MODEL, DATASET & FEATURE DEFINITIONS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "solar_model.pkl"
CSV_PATH = BASE_DIR / "spg.csv"

HOME_BASE_LAT = 22.5867
HOME_BASE_LON = 88.4750

FEATURE_SCHEMA = [
    ("temperature_2_m_above_gnd", "Ambient Temperature (2m)", "degC", 14.75, "Surface Meteorology"),
    ("relative_humidity_2_m_above_gnd", "Relative Humidity (2m)", "%", 48.0, "Surface Meteorology"),
    ("mean_sea_level_pressure_MSL", "Sea Level Pressure (MSL)", "hPa", 1018.1, "Surface Meteorology"),
    ("total_precipitation_sfc", "Surface Precipitation", "mm", 0.0, "Surface Meteorology"),
    ("snowfall_amount_sfc", "Snowfall Amount", "mm", 0.0, "Surface Meteorology"),
    ("total_cloud_cover_sfc", "Total Cloud Cover", "%", 8.7, "Atmospheric Cloud Layers"),
    ("high_cloud_cover_high_cld_lay", "High-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("medium_cloud_cover_mid_cld_lay", "Mid-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("low_cloud_cover_low_cld_lay", "Low-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("shortwave_radiation_backwards_sfc", "Shortwave Solar Irradiance", "W/m2", 381.81, "Solar Geometry & Flux"),
    ("wind_speed_10_m_above_gnd", "Wind Speed (10m Anemometer)", "km/h", 14.46, "Multi-Altitude Wind Profile"),
    ("wind_direction_10_m_above_gnd", "Wind Direction (10m)", "deg", 191.77, "Multi-Altitude Wind Profile"),
    ("wind_speed_80_m_above_gnd", "Wind Speed (80m Hub Height)", "km/h", 16.24, "Multi-Altitude Wind Profile"),
    ("wind_direction_80_m_above_gnd", "Wind Direction (80m)", "deg", 187.77, "Multi-Altitude Wind Profile"),
    ("wind_speed_900_mb", "Upper Wind Speed (900 mb)", "km/h", 14.49, "Multi-Altitude Wind Profile"),
    ("wind_direction_900_mb", "Upper Wind Direction (900 mb)", "deg", 187.99, "Multi-Altitude Wind Profile"),
    ("wind_gust_10_m_above_gnd", "Surface Wind Gust (10m)", "km/h", 18.0, "Multi-Altitude Wind Profile"),
    ("angle_of_incidence", "PV Angle of Incidence (AOI)", "deg", 47.34, "Solar Geometry & Flux"),
    ("zenith", "Solar Zenith Angle", "deg", 62.14, "Solar Geometry & Flux"),
    ("azimuth", "Solar Azimuth Angle", "deg", 163.24, "Solar Geometry & Flux"),
]

FEATURE_COLUMNS = [item[0] for item in FEATURE_SCHEMA]
DEFAULT_TELEMETRY = {item[0]: item[3] for item in FEATURE_SCHEMA}

CURATED_NEARBY_HUBS = [
    {"label": "New Town, Rajarhat, Kolkata, West Bengal, India", "short_name": "New Town, Kolkata", "lat": 22.5867, "lon": 88.4750, "country": "India"},
    {"label": "Salt Lake Sector V (Bidhannagar), Kolkata, West Bengal, 700091, India", "short_name": "Salt Lake Sector V", "lat": 22.5726, "lon": 88.4312, "country": "India"},
    {"label": "Haldia Industrial Belt, Purba Medinipur, West Bengal, 721604, India", "short_name": "Haldia, West Bengal", "lat": 22.0667, "lon": 88.0698, "country": "India"},
    {"label": "IIT Kharagpur Campus, Kharagpur, West Bengal, 721302, India", "short_name": "Kharagpur, WB", "lat": 22.3149, "lon": 87.3105, "country": "India"},
    {"label": "Durgapur Steel & Solar Grid, Paschim Bardhaman, West Bengal, India", "short_name": "Durgapur, WB", "lat": 23.5204, "lon": 87.3119, "country": "India"},
    {"label": "Kolaghat Thermal & Solar Substation, Purba Medinipur, West Bengal, India", "short_name": "Kolaghat, WB", "lat": 22.4270, "lon": 87.8710, "country": "India"},
    {"label": "Sagardighi Power Grid, Murshidabad, West Bengal, 742226, India", "short_name": "Sagardighi, WB", "lat": 24.3769, "lon": 88.0886, "country": "India"},
    {"label": "Bhadla Utility Solar Park, Phalodi, Rajasthan, India", "short_name": "Bhadla Solar Park", "lat": 27.5362, "lon": 71.9167, "country": "India"},
]


@st.cache_resource(show_spinner=False)
def load_solar_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


@st.cache_data(show_spinner=False)
def load_reference_bounds():
    if CSV_PATH.exists():
        try:
            df = pd.read_csv(CSV_PATH)
            bounds = {}
            for col in FEATURE_COLUMNS:
                if col in df.columns:
                    bounds[col] = (float(df[col].min()), float(df[col].max()), float(df[col].median()))
            return bounds
        except Exception:
            pass
    return {}


model = load_solar_model()
feature_bounds = load_reference_bounds()


# ==============================================================================
# 4. GEOMETRY, HAVERSINE DISTANCE, REVERSE GEOCODER & MULTI-ENGINE GEOCODING
# ==============================================================================
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


@st.cache_data(ttl=1800, show_spinner=False)
def reverse_geocode_coords(lat: float, lon: float) -> str:
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 15},
            headers={"User-Agent": "SPGX-Solar-Workbench/8.0"},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            addr = data.get("address", {})
            area = (
                addr.get("suburb")
                or addr.get("neighbourhood")
                or addr.get("residential")
                or addr.get("town")
                or addr.get("city_district")
                or addr.get("village")
                or addr.get("city")
                or data.get("name")
            )
            city = addr.get("city") or addr.get("state_district") or addr.get("state") or ""
            if area and city and area.lower() != city.lower():
                return f"{area}, {city}"
            if area:
                return str(area)
    except Exception:
        pass
    return f"Live GPS ({lat:.4f}N, {lon:.4f}E)"


def parse_direct_gps_query(query: str):
    q = (query or "").strip()
    m = re.search(r"(-?\d+\.\d+)\s*[,/;\s]\s*(-?\d+\.\d+)", q)
    if m:
        try:
            lat, lon = float(m.group(1)), float(m.group(2))
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                return lat, lon
        except Exception:
            pass
    return None


def compute_solar_angles(lat: float, lon: float, dt_utc: datetime, panel_tilt: float = 25.0, panel_azimuth: float = 180.0):
    day_of_year = dt_utc.timetuple().tm_yday
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour_decimal - 12.0) / 24.0)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )

    tst = hour_decimal * 60.0 + eqtime + 4.0 * lon
    ha_rad, lat_rad = math.radians((tst / 4.0) - 180.0), math.radians(lat)

    cos_zenith = max(-1.0, min(1.0, math.sin(lat_rad) * math.sin(decl) + math.cos(lat_rad) * math.cos(decl) * math.cos(ha_rad)))
    zenith_rad = math.acos(cos_zenith)

    if math.sin(zenith_rad) > 1e-5:
        cos_az = max(
            -1.0,
            min(1.0, (math.sin(decl) * math.cos(lat_rad) - math.cos(decl) * math.sin(lat_rad) * math.cos(ha_rad)) / math.sin(zenith_rad)),
        )
        az_deg = 360.0 - math.degrees(math.acos(cos_az)) if ((tst / 4.0) - 180.0) > 0 else math.degrees(math.acos(cos_az))
    else:
        az_deg = 180.0

    tilt_rad, surf_az_rad, az_rad = math.radians(panel_tilt), math.radians(panel_azimuth), math.radians(az_deg)
    cos_aoi = max(
        -1.0,
        min(1.0, math.cos(zenith_rad) * math.cos(tilt_rad) + math.sin(zenith_rad) * math.sin(tilt_rad) * math.cos(az_rad - surf_az_rad)),
    )
    return round(math.degrees(zenith_rad), 2), round(az_deg, 2), round(math.degrees(math.acos(cos_aoi)), 2)


def build_feature_vector(telemetry_dict: dict) -> pd.DataFrame:
    row = {col: float(telemetry_dict.get(col, DEFAULT_TELEMETRY[col])) for col in FEATURE_COLUMNS}
    if model is not None and hasattr(model, "feature_names_in_"):
        return pd.DataFrame([row])[[c for c in model.feature_names_in_ if c in row]]
    return pd.DataFrame([row])[FEATURE_COLUMNS]


def predict_power_kw(telemetry_dict: dict, is_day: int = 1, geometry_scale: float = 1.0) -> float:
    rad = float(telemetry_dict.get("shortwave_radiation_backwards_sfc", 0.0))
    if is_day == 0 or rad <= 0.0:
        return 0.0
    if model is None:
        return max(0.0, rad * 2.45 * geometry_scale)
    return max(0.0, float(model.predict(build_feature_vector(telemetry_dict))[0]) * geometry_scale)


@st.cache_data(ttl=900, show_spinner=False)
def search_locations_multi_engine(query: str, prioritize_india: bool = True, prioritize_nearby: bool = True, gmaps_api_key: str = ""):
    q = (query or "").strip()

    parsed_gps = parse_direct_gps_query(q)
    if parsed_gps is not None:
        g_lat, g_lon = parsed_gps
        place_name = reverse_geocode_coords(g_lat, g_lon)
        return [
            {
                "label": f"{place_name} ({g_lat:.5f}N, {g_lon:.5f}E)",
                "short_name": place_name,
                "lat": g_lat,
                "lon": g_lon,
                "country": "India",
                "dist_km": haversine_km(HOME_BASE_LAT, HOME_BASE_LON, g_lat, g_lon),
                "source": "LIVE-GPS",
            }
        ]

    if len(q) < 2:
        return CURATED_NEARBY_HUBS[:6]

    results, seen = [], set()

    def add_candidate(label, short, lat, lon, country, source):
        if (round(lat, 3), round(lon, 3)) in seen:
            return
        seen.add((round(lat, 3), round(lon, 3)))
        results.append(
            {
                "label": label,
                "short_name": short,
                "lat": lat,
                "lon": lon,
                "country": country,
                "dist_km": haversine_km(HOME_BASE_LAT, HOME_BASE_LON, lat, lon),
                "source": source,
            }
        )

    for hub in CURATED_NEARBY_HUBS:
        if q.lower() in hub["label"].lower() or q.lower() in hub["short_name"].lower():
            add_candidate(hub["label"], hub["short_name"], hub["lat"], hub["lon"], hub["country"], "GRID-HUB")

    if gmaps_api_key.strip():
        try:
            r = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": q, "key": gmaps_api_key.strip(), **({"region": "in"} if prioritize_india else {})},
                timeout=5,
            )
            if r.status_code == 200:
                for item in r.json().get("results", [])[:5]:
                    loc, fmt = item.get("geometry", {}).get("location", {}), item.get("formatted_address", q)
                    add_candidate(fmt, fmt.split(",")[0].strip(), float(loc["lat"]), float(loc["lng"]), "India" if "india" in fmt.lower() else "", "GMAPS")
        except Exception:
            pass

    try:
        nom_params = {"q": q, "format": "jsonv2", "addressdetails": 1, "limit": 6}
        if prioritize_india and not prioritize_nearby:
            nom_params["countrycodes"] = "in"
        elif prioritize_nearby:
            nom_params.update({"viewbox": "85.5,27.5,90.0,20.5", "bounded": 0})
        r_nom = requests.get("https://nominatim.openstreetmap.org/search", params=nom_params, headers={"User-Agent": "SPGX"}, timeout=6)
        if r_nom.status_code == 200:
            for item in r_nom.json():
                addr, disp = item.get("address", {}), item.get("display_name", "")
                add_candidate(
                    disp,
                    item.get("name") or addr.get("city") or addr.get("town") or disp.split(",")[0],
                    float(item["lat"]),
                    float(item["lon"]),
                    addr.get("country", ""),
                    "OSM",
                )
    except Exception:
        pass

    try:
        r_ph = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": q, "limit": 6, **({"lat": HOME_BASE_LAT, "lon": HOME_BASE_LON} if prioritize_nearby else {})},
            timeout=6,
        )
        if r_ph.status_code == 200:
            for f in r_ph.json().get("features", []):
                props, coords = f.get("properties", {}), f.get("geometry", {}).get("coordinates", [HOME_BASE_LON, HOME_BASE_LAT])
                parts = [props.get(k) for k in ["name", "street", "district", "city", "state", "postcode", "country"] if props.get(k)]
                if parts:
                    add_candidate(
                        ", ".join(dict.fromkeys(parts)),
                        props.get("name") or props.get("city") or q,
                        float(coords[1]),
                        float(coords[0]),
                        props.get("country", ""),
                        "PHOTON",
                    )
    except Exception:
        pass

    if not results:
        for hub in CURATED_NEARBY_HUBS[:4]:
            add_candidate(hub["label"], hub["short_name"], hub["lat"], hub["lon"], hub["country"], "FALLBACK")

    results.sort(
        key=lambda x: (
            0 if "india" in x.get("country", "").lower() or "india" in x["label"].lower() else 1,
            0 if x.get("dist_km", 99999) <= 350 else 1,
            x.get("dist_km", 99999),
        )
    )
    return results[:8]


@st.cache_data(ttl=600, show_spinner=False)
def fetch_open_meteo_telemetry(lat: float, lon: float):
    return requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,pressure_msl,precipitation,snowfall,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,shortwave_radiation,wind_speed_10m,wind_direction_10m,wind_speed_80m,wind_direction_80m,wind_gusts_10m,is_day",
            "hourly": "temperature_2m,relative_humidity_2m,pressure_msl,precipitation,snowfall,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,shortwave_radiation,wind_speed_10m,wind_direction_10m,wind_speed_80m,wind_direction_80m,wind_gusts_10m,is_day",
            "forecast_days": 3,
            "timezone": "auto",
        },
        timeout=10,
    ).json()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_nasa_power_recent(lat: float, lon: float):
    for end_lag, span in [(10, 45), (60, 45), (180, 30), (365, 25)]:
        try:
            end_dt = datetime.now(timezone.utc).date() - timedelta(days=end_lag)
            r = requests.get(
                "https://power.larc.nasa.gov/api/temporal/hourly/point",
                params={
                    "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,PS,WS10M,WD10M,PRECTOTCORR",
                    "community": "RE",
                    "longitude": round(float(lon), 4),
                    "latitude": round(float(lat), 4),
                    "start": (end_dt - timedelta(days=span)).strftime("%Y%m%d"),
                    "end": end_dt.strftime("%Y%m%d"),
                    "format": "JSON",
                    "time-standard": "UTC",
                },
                timeout=15,
            )
            if r.status_code != 200:
                continue
            param = r.json().get("properties", {}).get("parameter", {})
            rad_dict = param.get("ALLSKY_SFC_SW_DWN", {})
            if not rad_dict:
                continue

            records = []
            for ts_key, rad_val in sorted(rad_dict.items()):
                if rad_val is None or float(rad_val) < -90:
                    continue
                dt_obj = datetime.strptime(str(ts_key), "%Y%m%d%H").replace(tzinfo=timezone.utc)
                ws_raw = float(param.get("WS10M", {}).get(ts_key, 3.2))
                ws = max(0.0, (ws_raw if ws_raw > -90 else 3.0) * 3.6)
                ps = float(param.get("PS", {}).get(ts_key, 101.3))
                zen, az, aoi = compute_solar_angles(lat, lon, dt_obj)

                t2m_raw = float(param.get("T2M", {}).get(ts_key, 24.0))
                rh_raw = float(param.get("RH2M", {}).get(ts_key, 55.0))
                prec_raw = float(param.get("PRECTOTCORR", {}).get(ts_key, 0.0))

                tele = dict(DEFAULT_TELEMETRY)
                tele.update(
                    {
                        "temperature_2_m_above_gnd": t2m_raw if t2m_raw > -90 else 24.0,
                        "relative_humidity_2_m_above_gnd": max(0.0, min(100.0, rh_raw if rh_raw > -90 else 55.0)),
                        "mean_sea_level_pressure_MSL": ps * 10.0 if (0 < ps < 200) else (ps if ps > 200 else 1013.0),
                        "total_precipitation_sfc": max(0.0, prec_raw if prec_raw > -90 else 0.0),
                        "shortwave_radiation_backwards_sfc": float(rad_val),
                        "wind_speed_10_m_above_gnd": ws,
                        "wind_direction_10_m_above_gnd": float(param.get("WD10M", {}).get(ts_key, 180.0)),
                        "wind_speed_80_m_above_gnd": ws * 1.18,
                        "wind_direction_80_m_above_gnd": float(param.get("WD10M", {}).get(ts_key, 180.0)),
                        "wind_speed_900_mb": ws * 1.25,
                        "wind_direction_900_mb": float(param.get("WD10M", {}).get(ts_key, 180.0)),
                        "wind_gust_10_m_above_gnd": ws * 1.35,
                        "zenith": zen,
                        "azimuth": az,
                        "angle_of_incidence": aoi,
                    }
                )
                records.append(
                    {
                        "timestamp": dt_obj,
                        "irradiance_wm2": float(rad_val),
                        "predicted_kw": predict_power_kw(tele, is_day=(1 if float(rad_val) > 2.0 else 0)),
                    }
                )
            if len(records) >= 48 and max(x["irradiance_wm2"] for x in records) > 10.0:
                return pd.DataFrame(records).sort_values("timestamp").tail(168).reset_index(drop=True)
        except Exception:
            continue

    try:
        r_era = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": (datetime.now(timezone.utc).date() - timedelta(days=14)).strftime("%Y-%m-%d"),
                "end_date": (datetime.now(timezone.utc).date() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "hourly": "shortwave_radiation,temperature_2m,relative_humidity_2m,pressure_msl,precipitation,wind_speed_10m,wind_direction_10m",
                "timezone": "UTC",
            },
            timeout=15,
        )
        if r_era.status_code == 200:
            h, records = r_era.json().get("hourly", {}), []
            for i, t_str in enumerate(h.get("time", [])):
                dt_obj = pd.to_datetime(t_str).to_pydatetime().replace(tzinfo=timezone.utc)
                rad_v, ws = float(h["shortwave_radiation"][i] or 0.0), float(h["wind_speed_10m"][i] or 8.0)
                zen, az, aoi = compute_solar_angles(lat, lon, dt_obj)
                tele = dict(DEFAULT_TELEMETRY)
                tele.update(
                    {
                        "temperature_2_m_above_gnd": float(h["temperature_2m"][i] or 24.0),
                        "relative_humidity_2_m_above_gnd": float(h["relative_humidity_2m"][i] or 55.0),
                        "mean_sea_level_pressure_MSL": float(h["pressure_msl"][i] or 1013.0),
                        "total_precipitation_sfc": float(h["precipitation"][i] or 0.0),
                        "shortwave_radiation_backwards_sfc": rad_v,
                        "wind_speed_10_m_above_gnd": ws,
                        "wind_direction_10_m_above_gnd": float(h["wind_direction_10m"][i] or 180.0),
                        "wind_speed_80_m_above_gnd": ws * 1.18,
                        "wind_direction_80_m_above_gnd": float(h["wind_direction_10m"][i] or 180.0),
                        "wind_speed_900_mb": ws * 1.25,
                        "wind_direction_900_mb": float(h["wind_direction_10m"][i] or 180.0),
                        "wind_gust_10_m_above_gnd": ws * 1.35,
                        "zenith": zen,
                        "azimuth": az,
                        "angle_of_incidence": aoi,
                    }
                )
                records.append(
                    {
                        "timestamp": dt_obj,
                        "irradiance_wm2": rad_v,
                        "predicted_kw": predict_power_kw(tele, is_day=(1 if rad_v > 2.0 else 0)),
                    }
                )
            if records:
                return pd.DataFrame(records).tail(168).reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame()


# ==============================================================================
# 5. INITIALIZE GPS & SEARCH SESSION STATE
# ==============================================================================
if "gps_locked" not in st.session_state:
    st.session_state.gps_locked = False
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = HOME_BASE_LAT
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = HOME_BASE_LON
if "search_query_box" not in st.session_state:
    st.session_state.search_query_box = "New Town, Rajarhat, Kolkata"

qp = st.query_params
if "gps_lat" in qp and "gps_lon" in qp:
    try:
        parsed_lat = float(qp["gps_lat"])
        parsed_lon = float(qp["gps_lon"])
        if -90.0 <= parsed_lat <= 90.0 and -180.0 <= parsed_lon <= 180.0:
            st.session_state.gps_lat = parsed_lat
            st.session_state.gps_lon = parsed_lon
            st.session_state.gps_locked = True
            gps_tag = f"GPS: {parsed_lat:.5f}, {parsed_lon:.5f}"
            if st.session_state.get("last_qp_gps") != gps_tag:
                st.session_state.last_qp_gps = gps_tag
                st.session_state.search_query_box = gps_tag
    except Exception:
        pass

# ==============================================================================
# 6. ENTERPRISE FULL-SCREEN HEADER & INFINITE ROLLING API TICKER
# ==============================================================================
utc_now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
model_status_label = "RF-ENSEMBLE // ONLINE" if model is not None else "PHYSICS FALLBACK"

st.markdown(
    f"""
<div class="corp-header">
    <div>
        <div class="brand-eyebrow"><span class="pulse-dot"></span> SPG-X // UTILITY-SCALE PHOTOVOLTAIC TELEMETRY &amp; FORECASTING</div>
        <h1 class="brand-title">Solar Power Prediction Grid &amp; Telemetry Workbench</h1>
        <p class="brand-subtitle">Full-spectrum atmospheric boundary-layer modeling, real-time satellite irradiance synthesis, and ML yield dispatch.</p>
    </div>
    <div class="header-meta-grid">
        <div class="meta-item"><span class="meta-label">INFERENCE ENGINE</span><span class="meta-val">{model_status_label}</span></div>
        <div class="meta-item"><span class="meta-label">TELEMETRY STREAM</span><span class="meta-val">OPEN-METEO / NASA</span></div>
        <div class="meta-item"><span class="meta-label">SYSTEM CLOCK</span><span class="meta-val">{utc_now_str}</span></div>
    </div>
</div>

<div class="marquee-shell">
    <div class="marquee-pin">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.3"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        POWERED BY
    </div>
    <div class="marquee-viewport">
        <div class="marquee-track">
            <span class="api-badge"><span class="api-dot"></span>Open-Meteo NWP Weather API</span>
            <span class="api-badge"><span class="api-dot"></span>NASA LaRC POWER Satellite Archive</span>
            <span class="api-badge"><span class="api-dot"></span>HTML5 Browser GPS Geolocation</span>
            <span class="api-badge"><span class="api-dot"></span>OpenStreetMap Contributors &amp; CARTO Maps</span>
            <span class="api-badge"><span class="api-dot"></span>Swarm Rebuild Brick-by-Brick Engine</span>
            <span class="api-badge"><span class="api-dot"></span>Scikit-Learn Random Forest (20-Feature Ensemble)</span>
            <span class="api-badge"><span class="api-dot"></span>Open-Meteo NWP Weather API</span>
            <span class="api-badge"><span class="api-dot"></span>NASA LaRC POWER Satellite Archive</span>
            <span class="api-badge"><span class="api-dot"></span>HTML5 Browser GPS Geolocation</span>
            <span class="api-badge"><span class="api-dot"></span>OpenStreetMap Contributors &amp; CARTO Maps</span>
            <span class="api-badge"><span class="api-dot"></span>Swarm Rebuild Brick-by-Brick Engine</span>
            <span class="api-badge"><span class="api-dot"></span>Scikit-Learn Random Forest (20-Feature Ensemble)</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 7. MAIN NAVIGATION WORKBENCH TABS
# ==============================================================================
tab_live, tab_matrix, tab_nasa = st.tabs(
    [
        "01 // LIVE GLOBAL TELEMETRY & FORECAST",
        "02 // MANUAL TELEMETRY & FEATURE MATRIX",
        "03 // NASA POWER HISTORICAL VALIDATION",
    ]
)

# ------------------------------------------------------------------------------
# TAB 1: FULL-SCREEN BENTO TELEMETRY, LIVE GPS, BRICK-BY-BRICK SWARM & CARTO MAP
# ------------------------------------------------------------------------------
with tab_live:
    col_left, col_right = st.columns([1.05, 2.15], gap="large")

    with col_left:
        st.markdown(
            """
        <div class="section-strip">
            <div class="panel-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                Spatial Target &amp; Live GPS Lock
            </div>
            <span class="panel-tag">GPS + CARTO MAP</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Unclipped GPS Button + Slow, Smooth Brick-by-Brick Blank-Canvas Swarm Engine
        components.html(
            """
            <!DOCTYPE html>
            <html>
            <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body {
                    background: transparent;
                    padding: 4px 2px 6px 2px;
                    overflow: hidden;
                    font-family: 'JetBrains Mono', monospace;
                }
                .btn-row {
                    display: flex;
                    gap: 8px;
                    width: 100%;
                }
                .gps-btn {
                    flex: 1;
                    min-height: 48px;
                    padding: 10px 12px;
                    border-radius: 10px;
                    border: 1.5px solid rgba(16, 185, 129, 0.65);
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(14, 165, 233, 0.18) 100%);
                    color: #f8fafc;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: clamp(10px, 2.5vw, 11.5px);
                    font-weight: 700;
                    letter-spacing: 0.04em;
                    line-height: 1.25;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    gap: 8px;
                    box-shadow: 0 6px 18px -4px rgba(16, 185, 129, 0.28);
                    transition: all 0.25s cubic-bezier(0.22, 1.28, 0.36, 1);
                }
                .gps-btn:hover, .gps-btn:active {
                    border-color: #f59e0b;
                    transform: translateY(-2px);
                    box-shadow: 0 10px 22px -4px rgba(245, 158, 11, 0.35);
                }
                .swarm-btn {
                    min-height: 48px;
                    padding: 10px 12px;
                    border-radius: 10px;
                    border: 1.5px solid rgba(245, 158, 11, 0.6);
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(14, 165, 233, 0.16) 100%);
                    color: #f8fafc;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: clamp(10px, 2.4vw, 11px);
                    font-weight: 700;
                    cursor: pointer;
                    white-space: nowrap;
                    transition: all 0.25s cubic-bezier(0.22, 1.28, 0.36, 1);
                }
                .swarm-btn:hover {
                    border-color: #38bdf8;
                    transform: translateY(-2px);
                }
                .gps-dot {
                    width: 8px;
                    height: 8px;
                    min-width: 8px;
                    border-radius: 50%;
                    background: #10b981;
                    box-shadow: 0 0 10px #10b981;
                }
            </style>
            </head>
            <body>
                <div class="btn-row">
                    <button id="gpsBtn" class="gps-btn" onclick="requestLiveGPS()">
                        <span id="gpsDot" class="gps-dot"></span>
                        <span id="gpsBtnText">DETECT MY LIVE GPS LOCATION</span>
                    </button>
                    <button class="swarm-btn" onclick="triggerParentSwarmRebuild()" title="Replay Blank-Canvas Brick-by-Brick Build">
                        &#9889; REPLAY BUILD
                    </button>
                </div>

                <script>
                function feedCoordsToStreamlit(lat, lon) {
                    const formatted = 'GPS: ' + lat + ', ' + lon;
                    try {
                        const parentDoc = window.parent.document;
                        const inputs = parentDoc.querySelectorAll('input[type="text"]');
                        for (let inp of inputs) {
                            const label = inp.getAttribute('aria-label') || '';
                            if (label.includes('Search Any City') || inputs.length === 1) {
                                const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
                                setter.call(inp, formatted);
                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                inp.dispatchEvent(new Event('change', { bubbles: true }));
                                inp.focus();
                                inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                                inp.blur();
                                return true;
                            }
                        }
                    } catch (e) {}

                    try {
                        const parentUrl = new URL(window.parent.location.href);
                        parentUrl.searchParams.set('gps_lat', lat);
                        parentUrl.searchParams.set('gps_lon', lon);
                        window.parent.location.href = parentUrl.toString();
                    } catch (e) {
                        window.location.search = '?gps_lat=' + lat + '&gps_lon=' + lon;
                    }
                    return false;
                }

                function requestLiveGPS() {
                    const btnText = document.getElementById('gpsBtnText');
                    const dot = document.getElementById('gpsDot');
                    const geo = (window.parent && window.parent.navigator && window.parent.navigator.geolocation)
                                ? window.parent.navigator.geolocation
                                : navigator.geolocation;

                    if (!geo) {
                        btnText.innerText = 'GPS NOT SUPPORTED';
                        return;
                    }

                    btnText.innerText = 'ACQUIRING LIVE GPS...';
                    dot.style.background = '#f59e0b';

                    geo.getCurrentPosition(
                        function(pos) {
                            const lat = pos.coords.latitude.toFixed(5);
                            const lon = pos.coords.longitude.toFixed(5);
                            dot.style.background = '#10b981';
                            btnText.innerText = 'GPS LOCKED: ' + lat + '°N, ' + lon + '°E';
                            feedCoordsToStreamlit(lat, lon);
                        },
                        function(err) {
                            dot.style.background = '#ef4444';
                            btnText.innerText = 'ALLOW LOCATION PERMISSION';
                        },
                        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
                    );
                }

                function triggerParentSwarmRebuild() {
                    try {
                        if (window.parent && window.parent.runSPGXBrickByBrickRebuild) {
                            window.parent.runSPGXBrickByBrickRebuild();
                        }
                    } catch (e) {}
                }

                // =========================================================================
                // BRICK-BY-BRICK BLANK-CANVAS SWARM ENGINE (INSPIRED BY swarm-cursors)
                // SLOW, DELIBERATE, SEQUENTIAL CONSTRUCTION -> RADIAL SCATTER EXIT
                // =========================================================================
                (function setupBrickByBrickSwarmEngine() {
                    try {
                        const pWin = window.parent;
                        const pDoc = pWin.document;

                        // If initial build already finished in this session, keep bricks visible on Streamlit reruns
                        if (pWin.__spgxInitialBuildDone && !pWin.__spgxRebuilding) {
                            pDoc.body.classList.add('spgx-build-complete');
                        }

                        // 1. Attach 3D Scroll-Roll IntersectionObserver (Active only after build finishes)
                        if (!pWin.__spgxScrollObserverAttached) {
                            pWin.__spgxScrollObserverAttached = true;
                            const observer = new IntersectionObserver((entries) => {
                                entries.forEach((entry) => {
                                    if (pWin.__spgxRebuilding || !pDoc.body.classList.contains('spgx-build-complete')) return;
                                    if (entry.isIntersecting) {
                                        entry.target.style.opacity = '1';
                                        entry.target.style.transform = 'perspective(950px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)';
                                    } else {
                                        const rect = entry.boundingClientRect;
                                        const tiltDir = rect.top > 0 ? 13 : -11;
                                        entry.target.style.opacity = '0.74';
                                        entry.target.style.transform = 'perspective(950px) rotateX(' + tiltDir + 'deg) translateY(' + (rect.top > 0 ? '18px' : '-12px') + ') scale(0.96)';
                                    }
                                });
                            }, { threshold: [0.08, 0.25] });

                            const attachAnimations = () => {
                                if (pWin.__spgxRebuilding) return;
                                const selector = '.section-strip, .kpi-card, .yield-hero, .arch-card, .telemetry-bar, [data-testid="stPlotlyChart"], [data-testid="stNumberInput"], [data-testid="stSelectbox"], [data-testid="stTextInput"]';
                                pDoc.querySelectorAll(selector).forEach((el) => {
                                    if (!el.dataset.rollAttached) {
                                        el.dataset.rollAttached = '1';
                                        el.style.transition = 'transform 0.55s cubic-bezier(0.22, 1.28, 0.36, 1), opacity 0.5s ease, border-color 0.3s ease';
                                        observer.observe(el);
                                    }
                                });
                            };
                            setInterval(attachAnimations, 2000);
                        }

                        // 2. Define the Slow, Smooth Brick-by-Brick Blank-Canvas Build Sequence
                        pWin.runSPGXBrickByBrickRebuild = function() {
                            if (pWin.__spgxAnimFrame) {
                                pWin.cancelAnimationFrame(pWin.__spgxAnimFrame);
                            }
                            const oldCanvas = pDoc.getElementById('spgx-swarm-canvas');
                            if (oldCanvas) oldCanvas.remove();

                            // Lock body into blank-canvas mode
                            pDoc.body.classList.remove('spgx-build-complete');
                            pWin.__spgxRebuilding = true;

                            const canvas = pDoc.createElement('canvas');
                            canvas.id = 'spgx-swarm-canvas';
                            canvas.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:999999;';
                            pDoc.body.appendChild(canvas);
                            const ctx = canvas.getContext('2d');

                            let W = canvas.width = pWin.innerWidth;
                            let H = canvas.height = pWin.innerHeight;

                            const COLORS = ['#f59e0b', '#0ea5e9', '#10b981', '#a855f7', '#ec4899', '#38bdf8', '#facc15', '#fb7185', '#34d399', '#818cf8'];
                            const AGENT_TAGS = [
                                'rf-ensemble', 'nasa-larc', 'meteo-nwp', 'carto-gl', 'aoi-vector',
                                'zenith-calc', 'spline-48h', 'gps-lock', 'cloud-lay', 'wind-80m',
                                'osm-nominatim', 'photon-geo', 'grid-dispatch', 'flux-wm2'
                            ];

                            // Gather all visible bricks in logical architectural order
                            const selector = [
                                '.corp-header',
                                '.marquee-shell',
                                'div[data-testid="stTabs"] > div[role="tablist"]',
                                '.section-strip',
                                'div[data-testid="stSelectbox"]',
                                'div[data-testid="stTextInput"]',
                                'div[data-testid="stSlider"]',
                                '.telemetry-bar',
                                '.kpi-card',
                                '.yield-hero',
                                'div[data-testid="stPlotlyChart"]',
                                '.map-caption-strip',
                                '.arch-card'
                            ].join(', ');

                            const rawEls = Array.from(pDoc.querySelectorAll(selector));
                            const uniqueEls = [];
                            const seenSet = new Set();

                            rawEls.forEach((el) => {
                                if (seenSet.has(el)) return;
                                el.classList.remove('spgx-brick-built');
                                el.style.transition = 'none';
                                el.style.opacity = '0';
                                el.style.transform = 'perspective(1000px) rotateX(16deg) translateY(24px) scale(0.94)';

                                const r = el.getBoundingClientRect();
                                if (r.width > 20 && r.height > 14 && r.bottom > 0 && r.top < H + 80) {
                                    seenSet.add(el);
                                    uniqueEls.push(el);
                                } else {
                                    // Offscreen elements reveal quietly so scrolling down later works
                                    el.classList.add('spgx-brick-built');
                                }
                            });

                            // Sort bricks top-to-bottom, left-to-right so construction flows like a real blueprint
                            uniqueEls.sort((a, b) => {
                                const ra = a.getBoundingClientRect();
                                const rb = b.getBoundingClientRect();
                                if (Math.abs(ra.top - rb.top) > 32) return ra.top - rb.top;
                                return ra.left - rb.left;
                            });

                            if (!uniqueEls.length) {
                                pDoc.body.classList.add('spgx-build-complete');
                                pWin.__spgxRebuilding = false;
                                canvas.remove();
                                return;
                            }

                            const numBricks = uniqueEls.length;
                            // Deliberate, unhurried brick-by-brick timing:
                            // 0.00 -> 0.07: Initial cursor orbit at top center
                            // 0.07 -> 0.92: Sequential brick-by-brick construction
                            const ORBIT_FRAC = 0.07;
                            const BUILD_SPAN = 0.85;
                            const stepFrac = BUILD_SPAN / numBricks;
                            const brickSpan = Math.min(0.16, stepFrac * 1.65); // Only 1-2 bricks active at a time!

                            const bricks = uniqueEls.map((el, idx) => {
                                const r = el.getBoundingClientRect();
                                const startFrac = ORBIT_FRAC + idx * stepFrac;
                                const endFrac = Math.min(0.96, startFrac + brickSpan);
                                const rawText = (el.innerText || '').trim().split('\\n')[0] || ('BRICK_LAYER_' + (idx + 1));

                                return {
                                    idx,
                                    el,
                                    rect: r,
                                    startFrac,
                                    endFrac,
                                    revealed: false,
                                    flashAlpha: 0,
                                    color: COLORS[idx % COLORS.length],
                                    label: rawText.slice(0, 36),
                                    isKpi: el.classList.contains('kpi-card')
                                };
                            });

                            // Total build time scales smoothly with brick count (~10.5s - 11.5s)
                            const BUILD_MS = Math.max(9800, Math.min(11800, numBricks * 580));
                            const SCATTER_MS = 1150;
                            const TOTAL_MS = BUILD_MS + SCATTER_MS;

                            const originX = W * 0.5;
                            const originY = Math.min(130, H * 0.2);

                            // 42 Multiplayer Agents organized into 6-Agent Construction Squads
                            const agents = Array.from({ length: 42 }, (_, i) => {
                                const ang = (i / 42) * Math.PI * 2;
                                const rad = 22 + (i % 6) * 12;
                                const scatterAng = ang + (Math.random() - 0.5) * 0.3;
                                const scatterSpeed = 14 + Math.random() * 14;
                                const roleInSquad = i % 6;
                                // Roles: 0=tl-anchor, 1=crosshair-drag, 2=ibeam-type, 3=tr-guide, 4=bl-guide, 5=inspector
                                return {
                                    id: i,
                                    squadSlot: roleInSquad,
                                    x: originX + Math.cos(ang) * rad,
                                    y: originY + Math.sin(ang) * rad,
                                    vx: 0,
                                    vy: 0,
                                    trail: [],
                                    scatterVx: Math.cos(scatterAng) * scatterSpeed,
                                    scatterVy: Math.sin(scatterAng) * scatterSpeed,
                                    color: COLORS[i % COLORS.length],
                                    tag: AGENT_TAGS[i % AGENT_TAGS.length],
                                    role: roleInSquad === 1 ? 'crosshair' : (roleInSquad === 2 ? 'ibeam' : 'pointer'),
                                    alpha: 1.0,
                                    scale: 1.0
                                };
                            });

                            const startTime = performance.now();

                            function smoothstep(t) {
                                const c = Math.max(0, Math.min(1, t));
                                return c * c * (3 - 2 * c);
                            }

                            function easeOutCubic(t) {
                                const c = Math.max(0, Math.min(1, t));
                                return 1 - Math.pow(1 - c, 3);
                            }

                            function drawFigmaRulers(alpha, guideX, guideY, activeBrickIdx) {
                                if (alpha <= 0.02) return;
                                ctx.save();
                                ctx.globalAlpha = alpha;

                                // Top & Left Pixel Rulers
                                ctx.fillStyle = 'rgba(6, 10, 19, 0.94)';
                                ctx.fillRect(0, 0, W, 20);
                                ctx.fillRect(0, 20, 20, H - 20);

                                ctx.strokeStyle = 'rgba(148, 163, 184, 0.24)';
                                ctx.lineWidth = 1;
                                ctx.beginPath();
                                ctx.moveTo(0, 20); ctx.lineTo(W, 20);
                                ctx.moveTo(20, 0); ctx.lineTo(20, H);
                                ctx.stroke();

                                ctx.fillStyle = '#64748b';
                                ctx.font = '500 8.5px "JetBrains Mono", monospace';
                                for (let x = 100; x < W; x += 100) {
                                    ctx.fillRect(x, 12, 1, 8);
                                    ctx.fillText(String(x), x + 3, 10);
                                }
                                for (let y = 100; y < H; y += 100) {
                                    ctx.fillRect(12, y, 8, 1);
                                    ctx.save();
                                    ctx.translate(10, y + 3);
                                    ctx.rotate(-Math.PI / 2);
                                    ctx.fillText(String(y), 0, 0);
                                    ctx.restore();
                                }

                                // Active Red / Cyan Laser Alignment Guides
                                if (guideY > 22 && guideY < H) {
                                    ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)';
                                    ctx.setLineDash([3, 3]);
                                    ctx.beginPath();
                                    ctx.moveTo(20, guideY); ctx.lineTo(W, guideY);
                                    ctx.stroke();
                                }
                                if (guideX > 22 && guideX < W) {
                                    ctx.strokeStyle = 'rgba(14, 165, 233, 0.45)';
                                    ctx.setLineDash([3, 3]);
                                    ctx.beginPath();
                                    ctx.moveTo(guideX, 20); ctx.lineTo(guideX, H);
                                    ctx.stroke();
                                }
                                ctx.setLineDash([]);

                                // Sleek Bottom Build Progress Pill
                                const pillText = `SWARM ARCHITECT // BUILDING BRICK ${Math.min(numBricks, activeBrickIdx + 1)} OF ${numBricks} [42 AGENTS]`;
                                ctx.font = '700 10.5px "JetBrains Mono", monospace';
                                const ptw = ctx.measureText(pillText).width;
                                const px = (W - ptw - 28) / 2;
                                const py = H - 38;
                                ctx.fillStyle = 'rgba(7, 11, 20, 0.92)';
                                ctx.strokeStyle = 'rgba(245, 158, 11, 0.6)';
                                ctx.lineWidth = 1.2;
                                ctx.beginPath();
                                ctx.roundRect(px, py, ptw + 28, 24, 999);
                                ctx.fill();
                                ctx.stroke();
                                ctx.fillStyle = '#f59e0b';
                                ctx.fillText(pillText, px + 14, py + 15.5);

                                ctx.restore();
                            }

                            function drawAgentCursor(ag, showTag) {
                                if (ag.alpha <= 0.02) return;
                                ctx.save();
                                ctx.globalAlpha = Math.max(0, Math.min(1, ag.alpha));

                                // Draw smooth glowing motion trail
                                if (ag.trail.length > 1) {
                                    ctx.beginPath();
                                    ctx.moveTo(ag.trail[0].x, ag.trail[0].y);
                                    for (let k = 1; k < ag.trail.length; k++) {
                                        ctx.lineTo(ag.trail[k].x, ag.trail[k].y);
                                    }
                                    ctx.strokeStyle = ag.color + '44';
                                    ctx.lineWidth = 2;
                                    ctx.lineCap = 'round';
                                    ctx.stroke();
                                }

                                ctx.translate(ag.x, ag.y);
                                ctx.scale(ag.scale, ag.scale);

                                if (ag.role === 'crosshair') {
                                    ctx.strokeStyle = ag.color;
                                    ctx.lineWidth = 1.7;
                                    ctx.beginPath();
                                    ctx.moveTo(-8, 0); ctx.lineTo(8, 0);
                                    ctx.moveTo(0, -8); ctx.lineTo(0, 8);
                                    ctx.stroke();
                                    ctx.strokeStyle = '#ffffff';
                                    ctx.strokeRect(-2.5, -2.5, 5, 5);
                                } else if (ag.role === 'ibeam') {
                                    ctx.strokeStyle = ag.color;
                                    ctx.lineWidth = 1.7;
                                    ctx.beginPath();
                                    ctx.moveTo(0, -7); ctx.lineTo(0, 7);
                                    ctx.moveTo(-3.5, -7); ctx.lineTo(3.5, -7);
                                    ctx.moveTo(-3.5, 7); ctx.lineTo(3.5, 7);
                                    ctx.stroke();
                                } else {
                                    ctx.beginPath();
                                    ctx.moveTo(0, 0);
                                    ctx.lineTo(0, 15);
                                    ctx.lineTo(4.2, 11.5);
                                    ctx.lineTo(7.5, 18);
                                    ctx.lineTo(10, 16.8);
                                    ctx.lineTo(6.8, 10.2);
                                    ctx.lineTo(12, 10.2);
                                    ctx.closePath();
                                    ctx.fillStyle = ag.color;
                                    ctx.shadowColor = ag.color;
                                    ctx.shadowBlur = 8;
                                    ctx.fill();
                                    ctx.shadowBlur = 0;
                                    ctx.lineWidth = 1.25;
                                    ctx.strokeStyle = '#ffffff';
                                    ctx.stroke();
                                }

                                if (showTag && ag.tag) {
                                    ctx.font = '600 9.5px "JetBrains Mono", monospace';
                                    const tw = ctx.measureText(ag.tag).width;
                                    ctx.fillStyle = 'rgba(7, 11, 20, 0.9)';
                                    ctx.strokeStyle = ag.color;
                                    ctx.lineWidth = 1;
                                    ctx.beginPath();
                                    ctx.roundRect(11, 10, tw + 10, 15, 4);
                                    ctx.fill();
                                    ctx.stroke();
                                    ctx.fillStyle = '#f8fafc';
                                    ctx.fillText(ag.tag, 16, 20.5);
                                }
                                ctx.restore();
                            }

                            function frame(now) {
                                const elapsed = now - startTime;
                                ctx.clearRect(0, 0, W, H);

                                if (elapsed < BUILD_MS) {
                                    const progress = elapsed / BUILD_MS;
                                    let guideX = -1, guideY = -1;
                                    let currentBrickIdx = 0;
                                    const activeBricks = [];

                                    // Evaluate each brick's construction progress
                                    bricks.forEach((b, idx) => {
                                        const r = b.rect;
                                        const rawLocal = (progress - b.startFrac) / (b.endFrac - b.startFrac);

                                        if (rawLocal >= 0 && rawLocal <= 1.0) {
                                            activeBricks.push({ brick: b, localP: rawLocal });
                                            currentBrickIdx = idx;

                                            // Smoothly drag box from 0 -> 1
                                            const dragP = easeOutCubic(Math.min(1, rawLocal / 0.78));
                                            const curW = Math.max(10, r.width * dragP);
                                            const curH = Math.max(10, r.height * dragP);

                                            guideX = r.left + curW;
                                            guideY = r.top + curH;

                                            ctx.save();
                                            // Blueprint Shimmer Fill
                                            ctx.fillStyle = b.color + '18';
                                            ctx.fillRect(r.left, r.top, curW, curH);

                                            // Dashed Wireframe Box
                                            ctx.strokeStyle = b.color;
                                            ctx.lineWidth = 1.6;
                                            ctx.setLineDash([6, 4]);
                                            ctx.strokeRect(r.left, r.top, curW, curH);
                                            ctx.setLineDash([]);

                                            // 4 Corner CAD Handles
                                            const hs = 4.5;
                                            ctx.fillStyle = '#ffffff';
                                            ctx.strokeStyle = b.color;
                                            [
                                                [r.left - hs / 2, r.top - hs / 2],
                                                [r.left + curW - hs / 2, r.top - hs / 2],
                                                [r.left - hs / 2, r.top + curH - hs / 2],
                                                [r.left + curW - hs / 2, r.top + curH - hs / 2]
                                            ].forEach(([hx, hy]) => {
                                                ctx.fillRect(hx, hy, hs, hs);
                                                ctx.strokeRect(hx, hy, hs, hs);
                                            });

                                            // Live W × H Dimension Pill Badge
                                            const dimText = `${Math.round(curW)} × ${Math.round(curH)}`;
                                            ctx.font = '700 9.5px "JetBrains Mono", monospace';
                                            const dtw = ctx.measureText(dimText).width;
                                            const bx = Math.max(r.left, r.left + curW - dtw - 10);
                                            const by = r.top + curH + 4;
                                            ctx.fillStyle = b.color;
                                            ctx.beginPath();
                                            ctx.roundRect(bx, by, dtw + 10, 15, 3);
                                            ctx.fill();
                                            ctx.fillStyle = '#04070d';
                                            ctx.fillText(dimText, bx + 5, by + 11);

                                            // Live I-Beam Typed Text inside the Brick
                                            if (rawLocal > 0.22) {
                                                const typeP = smoothstep((rawLocal - 0.22) / 0.62);
                                                const chars = Math.floor(b.label.length * typeP);
                                                const typed = b.label.slice(0, chars);
                                                ctx.font = '600 10.5px "JetBrains Mono", monospace';
                                                ctx.fillStyle = '#f8fafc';
                                                const tx = r.left + 12;
                                                const ty = r.top + Math.min(24, curH * 0.55);
                                                ctx.fillText(typed, tx, ty);

                                                if (Math.floor(now / 110) % 2 === 0) {
                                                    const tw = ctx.measureText(typed).width;
                                                    ctx.fillStyle = '#f59e0b';
                                                    ctx.fillRect(tx + tw + 3, ty - 9, 2, 11);
                                                }
                                            }

                                            // Red Option-Drag Gap Guide between adjacent KPI bricks
                                            if (b.isKpi && idx > 0 && bricks[idx - 1].isKpi) {
                                                const prevR = bricks[idx - 1].rect;
                                                if (Math.abs(prevR.top - r.top) < 25 && r.left > prevR.right) {
                                                    const midY = r.top + r.height / 2;
                                                    ctx.strokeStyle = '#ef4444';
                                                    ctx.lineWidth = 1.3;
                                                    ctx.beginPath();
                                                    ctx.moveTo(prevR.right, midY);
                                                    ctx.lineTo(r.left, midY);
                                                    ctx.stroke();
                                                }
                                            }
                                            ctx.restore();
                                        }

                                        // Pop the real DOM Brick into existence when its wireframe reaches 86%
                                        if (rawLocal >= 0.86 && !b.revealed) {
                                            b.revealed = true;
                                            b.flashAlpha = 0.85;
                                            b.el.classList.add('spgx-brick-built');
                                        }

                                        // Subtle completion border glow when brick locks in
                                        if (b.flashAlpha > 0.02) {
                                            ctx.save();
                                            ctx.strokeStyle = b.color;
                                            ctx.globalAlpha = b.flashAlpha;
                                            ctx.lineWidth = 2.5;
                                            ctx.shadowColor = b.color;
                                            ctx.shadowBlur = 14;
                                            ctx.strokeRect(r.left, r.top, r.width, r.height);
                                            ctx.restore();
                                            b.flashAlpha *= 0.90;
                                        }
                                    });

                                    drawFigmaRulers(0.92, guideX, guideY, currentBrickIdx);

                                    // Direct all 42 Cursors in smooth squads onto the active brick(s)
                                    agents.forEach((ag, i) => {
                                        let tx, ty;

                                        if (progress < ORBIT_FRAC) {
                                            // Calm initial gather orbit at top center
                                            const orbitAng = (i / 42) * Math.PI * 2 + (progress / ORBIT_FRAC) * Math.PI * 1.6;
                                            const orbitRad = 26 + (i % 6) * 14;
                                            tx = originX + Math.cos(orbitAng) * orbitRad;
                                            ty = originY + Math.sin(orbitAng) * orbitRad;
                                        } else {
                                            // Assign each squad to one of the currently active bricks (1-2 bricks at a time)
                                            const activeEntry = activeBricks.length
                                                ? activeBricks[Math.floor(i / 6) % activeBricks.length]
                                                : { brick: bricks[Math.min(bricks.length - 1, currentBrickIdx)], localP: 1.0 };

                                            const b = activeEntry.brick;
                                            const lp = activeEntry.localP;
                                            const r = b.rect;
                                            const dragP = easeOutCubic(Math.min(1, lp / 0.78));
                                            const curW = Math.max(10, r.width * dragP);
                                            const curH = Math.max(10, r.height * dragP);

                                            if (ag.squadSlot === 0) {
                                                // Top-left anchor cursor
                                                tx = r.left;
                                                ty = r.top;
                                            } else if (ag.squadSlot === 1) {
                                                // Bottom-right crosshair dragging cursor
                                                tx = r.left + curW;
                                                ty = r.top + curH;
                                            } else if (ag.squadSlot === 2) {
                                                // I-Beam typing cursor gliding left-to-right inside box
                                                const typeP = smoothstep(Math.max(0, (lp - 0.22) / 0.62));
                                                tx = r.left + 14 + Math.min(r.width - 24, typeP * 195);
                                                ty = r.top + Math.min(24, curH * 0.55);
                                            } else if (ag.squadSlot === 3) {
                                                // Top-right corner guide cursor
                                                tx = r.left + curW;
                                                ty = r.top;
                                            } else if (ag.squadSlot === 4) {
                                                // Bottom-left corner guide cursor
                                                tx = r.left;
                                                ty = r.top + curH;
                                            } else {
                                                // Perimeter inspector cursor
                                                const perimAng = now * 0.0045 + i;
                                                tx = r.left + (Math.cos(perimAng) * 0.42 + 0.5) * curW;
                                                ty = r.top + (Math.sin(perimAng) * 0.42 + 0.5) * curH;
                                            }
                                        }

                                        // Smooth spring-damped cursor kinematics
                                        ag.vx += (tx - ag.x) * 0.14;
                                        ag.vy += (ty - ag.y) * 0.14;
                                        ag.vx *= 0.72;
                                        ag.vy *= 0.72;
                                        ag.x += ag.vx;
                                        ag.y += ag.vy;

                                        ag.trail.push({ x: ag.x, y: ag.y });
                                        if (ag.trail.length > 6) ag.trail.shift();

                                        drawAgentCursor(ag, i % 3 === 0);
                                    });

                                    pWin.__spgxAnimFrame = pWin.requestAnimationFrame(frame);

                                } else if (elapsed < TOTAL_MS) {
                                    // PHASE 2: ALL BRICKS BUILT -> CURSORS SCATTER RADIALLY OFF-SCREEN
                                    const scatterP = (elapsed - BUILD_MS) / SCATTER_MS;

                                    bricks.forEach((b) => {
                                        if (!b.revealed) {
                                            b.revealed = true;
                                            b.el.classList.add('spgx-brick-built');
                                        }
                                    });

                                    drawFigmaRulers(Math.max(0, 1 - scatterP * 2.4), -1, -1, numBricks - 1);

                                    agents.forEach((ag, i) => {
                                        ag.x += ag.scatterVx * (0.9 + scatterP * 1.9);
                                        ag.y += ag.scatterVy * (0.9 + scatterP * 1.9);
                                        ag.alpha = Math.max(0, 1 - easeOutCubic(scatterP));
                                        ag.scale = Math.max(0.4, 1 - scatterP * 0.5);

                                        ag.trail.push({ x: ag.x, y: ag.y });
                                        if (ag.trail.length > 5) ag.trail.shift();

                                        drawAgentCursor(ag, i % 4 === 0);
                                    });

                                    pWin.__spgxAnimFrame = pWin.requestAnimationFrame(frame);

                                } else {
                                    // PHASE 3: CLEANUP — MARK BUILD COMPLETE & UNMOUNT OVERLAY CANVAS
                                    bricks.forEach((b) => b.el.classList.add('spgx-brick-built'));
                                    pDoc.body.classList.add('spgx-build-complete');
                                    pWin.__spgxRebuilding = false;
                                    canvas.remove();
                                }
                            }

                            pWin.__spgxAnimFrame = pWin.requestAnimationFrame(frame);
                        };

                        // Run Brick-by-Brick Blank-Canvas Build automatically on initial page load
                        if (!pWin.__spgxInitialBuildDone) {
                            pWin.__spgxInitialBuildDone = true;
                            setTimeout(() => {
                                pWin.runSPGXBrickByBrickRebuild();
                            }, 120);
                        }
                    } catch (err) {}
                })();
                </script>
            </body>
            </html>
            """,
            height=64,
        )

        hub_names = ["Search / Live GPS Query", "Manual GPS Coordinates"] + [h["short_name"] for h in CURATED_NEARBY_HUBS]
        selected_hub_mode = st.selectbox(
            "Target Acquisition Mode / Regional Grid Hub",
            options=hub_names,
            index=0,
            help="Tap 'DETECT MY LIVE GPS LOCATION' above to auto-feed your live coordinates, search any place, or pick a regional hub.",
        )

        c_opt1, c_opt2, c_opt3 = st.columns(3)
        with c_opt1:
            prio_nearby = st.checkbox("Nearby Bias", value=True)
        with c_opt2:
            prio_india = st.checkbox("India Bias", value=True)
        with c_opt3:
            sim_noon = st.checkbox("Peak Noon", value=False)

        if selected_hub_mode == "Manual GPS Coordinates":
            g_lat_col, g_lon_col = st.columns(2)
            with g_lat_col:
                lat_val = st.number_input("GPS Latitude", value=float(st.session_state.gps_lat), format="%.5f", step=0.01)
            with g_lon_col:
                lon_val = st.number_input("GPS Longitude", value=float(st.session_state.gps_lon), format="%.5f", step=0.01)
            short_name = reverse_geocode_coords(lat_val, lon_val)
            active_loc = {
                "label": f"{short_name} ({lat_val:.5f}N, {lon_val:.5f}E)",
                "short_name": short_name,
                "lat": lat_val,
                "lon": lon_val,
                "dist_km": haversine_km(HOME_BASE_LAT, HOME_BASE_LON, lat_val, lon_val),
                "source": "LIVE-GPS",
            }
        elif selected_hub_mode != "Search / Live GPS Query":
            matched_hub = next((h for h in CURATED_NEARBY_HUBS if h["short_name"] == selected_hub_mode), CURATED_NEARBY_HUBS[0])
            lat_val, lon_val, short_name = matched_hub["lat"], matched_hub["lon"], matched_hub["short_name"]
            active_loc = {
                **matched_hub,
                "dist_km": haversine_km(HOME_BASE_LAT, HOME_BASE_LON, lat_val, lon_val),
                "source": "GRID-HUB",
            }
        else:
            search_q = st.text_input(
                "Search Any City, Substation, Landmark, College, or PIN Code",
                key="search_query_box",
                placeholder="e.g., Techno India University, Haldia, or tap Detect Live GPS above...",
            )
            with st.expander("Advanced: Optional Google Maps API Key"):
                gmaps_key = st.text_input("Google Maps Geocoding Key (Leave blank for OSM + Photon)", value="", type="password")

            candidates = search_locations_multi_engine(
                search_q, prioritize_india=prio_india, prioritize_nearby=prio_nearby, gmaps_api_key=gmaps_key
            )
            formatted_options = [f"{c['short_name']} — {c['label'][:55]} [{c.get('dist_km', 0):.0f} km • {c.get('source', 'GEO')}]" for c in candidates]
            selected_disp = st.selectbox(
                f"Matched Spatial Targets ({len(formatted_options)} found):",
                options=formatted_options,
                index=0,
            )
            active_loc = dict(zip(formatted_options, candidates)).get(selected_disp, candidates[0])
            lat_val, lon_val, short_name = active_loc["lat"], active_loc["lon"], active_loc["short_name"]

        is_gps_source = active_loc.get("source") == "LIVE-GPS"

        st.markdown("##### PV Array Hardware Geometry")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            panel_tilt = st.slider("Module Tilt (deg)", 0, 75, 25)
        with g_col2:
            panel_az = st.slider("Module Azimuth (deg)", 90, 270, 180)
        geometry_factor = max(0.75, min(1.08, float(np.cos(np.radians(abs(panel_tilt - max(10.0, abs(lat_val))))))))

        # Multi-Ring Radar Target Lock on OpenStreetMap + CARTO Vector Map
        pin_label = f"LIVE GPS: {short_name}" if is_gps_source else short_name
        core_color = "#10b981" if is_gps_source else "#f59e0b"
        halo_color = "rgba(16, 185, 129, 0.24)" if is_gps_source else "rgba(245, 158, 11, 0.22)"

        map_fig = go.Figure()
        map_fig.add_trace(
            go.Scattermap(
                lat=[lat_val],
                lon=[lon_val],
                mode="markers",
                marker=dict(size=36, color=halo_color),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        map_fig.add_trace(
            go.Scattermap(
                lat=[lat_val],
                lon=[lon_val],
                mode="markers+text",
                marker=dict(size=13, color=core_color),
                text=[f"  {pin_label}"],
                textfont=dict(family="JetBrains Mono, monospace", size=12, color="#ffffff"),
                textposition="top right",
                hovertemplate=f"<b>{html.escape(short_name)}</b><br>Lat: {lat_val:.5f}°N<br>Lon: {lon_val:.5f}°E<extra></extra>",
                showlegend=False,
            )
        )
        map_fig.update_layout(
            map=dict(
                style="carto-darkmatter",
                center=dict(lat=lat_val, lon=lon_val),
                zoom=13.4 if is_gps_source else 10.8,
            ),
            uirevision=f"{lat_val:.5f}_{lon_val:.5f}",
            margin=dict(l=0, r=0, t=0, b=0),
            height=240,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False, "scrollZoom": True})

        st.markdown(
            f"""
            <div class="map-caption-strip">
                <span><strong style="color:#10b981;">&#9679; MAP LOCK:</strong> {html.escape(short_name.upper())} ({lat_val:.4f}&deg;N, {lon_val:.4f}&deg;E)</span>
                <span>&copy; OpenStreetMap contributors &bull; CARTO</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        try:
            meteo_data = fetch_open_meteo_telemetry(lat_val, lon_val)
            tz_name = meteo_data.get("timezone", "UTC")
            current_block = meteo_data.get("current", {})
            hourly_block = meteo_data.get("hourly", {})
        except Exception:
            tz_name, current_block, hourly_block = "UTC", {}, {}

        using_noon_sim = False
        eff_rad = float(current_block.get("shortwave_radiation", 0.0))
        eff_is_day = int(current_block.get("is_day", 0))
        eff_temp = float(current_block.get("temperature_2m", 25.0))
        eff_rh = float(current_block.get("relative_humidity_2m", 60.0))
        eff_cloud = float(current_block.get("cloud_cover", 10.0))
        eff_wind10 = float(current_block.get("wind_speed_10m", 5.0))
        eff_wdir10 = float(current_block.get("wind_direction_10m", 180.0))
        eff_pres = float(current_block.get("pressure_msl", 1013.0))
        eff_precip = float(current_block.get("precipitation", 0.0))
        eff_cl_low = float(current_block.get("cloud_cover_low", 0.0))
        eff_cl_mid = float(current_block.get("cloud_cover_mid", 0.0))
        eff_cl_high = float(current_block.get("cloud_cover_high", 0.0))

        times_list = hourly_block.get("time", [])
        if sim_noon and times_list:
            noon_indices = [i for i, t in enumerate(times_list) if "T12:00" in t]
            if noon_indices:
                idx0 = noon_indices[0]
                using_noon_sim = True
                eff_rad = float(hourly_block["shortwave_radiation"][idx0])
                eff_is_day = 1
                eff_temp = float(hourly_block["temperature_2m"][idx0])
                eff_rh = float(hourly_block["relative_humidity_2m"][idx0])
                eff_cloud = float(hourly_block["cloud_cover"][idx0])
                eff_wind10 = float(hourly_block["wind_speed_10m"][idx0])

        zen_now, az_now, aoi_now = compute_solar_angles(
            lat_val,
            lon_val,
            datetime.now(timezone.utc) if not using_noon_sim else datetime.now(timezone.utc).replace(hour=6, minute=30),
            panel_tilt=panel_tilt,
            panel_azimuth=panel_az,
        )

        active_telemetry = {
            "temperature_2_m_above_gnd": eff_temp,
            "relative_humidity_2_m_above_gnd": eff_rh,
            "mean_sea_level_pressure_MSL": eff_pres,
            "total_precipitation_sfc": eff_precip,
            "snowfall_amount_sfc": 0.0,
            "total_cloud_cover_sfc": eff_cloud,
            "high_cloud_cover_high_cld_lay": eff_cl_high,
            "medium_cloud_cover_mid_cld_lay": eff_cl_mid,
            "low_cloud_cover_low_cld_lay": eff_cl_low,
            "shortwave_radiation_backwards_sfc": eff_rad,
            "wind_speed_10_m_above_gnd": eff_wind10,
            "wind_direction_10_m_above_gnd": eff_wdir10,
            "wind_speed_80_m_above_gnd": eff_wind10 * 1.2,
            "wind_direction_80_m_above_gnd": eff_wdir10,
            "wind_speed_900_mb": eff_wind10 * 1.25,
            "wind_direction_900_mb": eff_wdir10,
            "wind_gust_10_m_above_gnd": eff_wind10 * 1.3,
            "angle_of_incidence": aoi_now,
            "zenith": zen_now,
            "azimuth": az_now,
        }
        pred_kw = predict_power_kw(active_telemetry, is_day=eff_is_day, geometry_scale=geometry_factor)

        status_cls = "status-pill-day" if (eff_is_day == 1 and eff_rad > 5) else "status-pill-night"
        status_txt = (
            "PEAK NOON SIMULATION (12:00 LOCAL)"
            if using_noon_sim
            else ("DAYTIME SOLAR FLUX ACTIVE" if (eff_is_day == 1 and eff_rad > 5) else "NIGHTTIME // ZERO IRRADIANCE")
        )

        st.markdown(
            f"""
        <div class="telemetry-bar">
            <div>
                <strong style="color:#f8fafc;">TARGET:</strong> {html.escape(short_name.upper())} ({active_loc.get('dist_km', 0.0):.0f} km) &nbsp;|&nbsp;
                <strong style="color:#f8fafc;">COORDS:</strong> {lat_val:.4f}&deg;N, {lon_val:.4f}&deg;E &nbsp;|&nbsp;
                <strong style="color:#f8fafc;">TZ:</strong> {html.escape(tz_name)}
            </div>
            <div class="{status_cls}">{status_txt}</div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">SOLAR IRRADIANCE</span></div>
                <div class="kpi-value">{eff_rad:.1f}<span class="kpi-unit">W/m&sup2;</span></div>
                <div class="kpi-sub">AOI: {aoi_now:.1f}&deg; | Zenith: {zen_now:.1f}&deg;</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">AMBIENT TEMP</span></div>
                <div class="kpi-value">{eff_temp:.1f}<span class="kpi-unit">&deg;C</span></div>
                <div class="kpi-sub">MSL Pressure: {eff_pres:.0f} hPa</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">REL. HUMIDITY</span></div>
                <div class="kpi-value">{eff_rh:.0f}<span class="kpi-unit">%</span></div>
                <div class="kpi-sub">Precip: {eff_precip:.1f} mm</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">CLOUD OPACITY</span></div>
                <div class="kpi-value">{eff_cloud:.0f}<span class="kpi-unit">%</span></div>
                <div class="kpi-sub">L/M/H: {eff_cl_low:.0f}/{eff_cl_mid:.0f}/{eff_cl_high:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">WIND VELOCITY</span></div>
                <div class="kpi-value">{eff_wind10:.1f}<span class="kpi-unit">km/h</span></div>
                <div class="kpi-sub">80m Hub: {eff_wind10*1.2:.1f} km/h</div>
            </div>
        </div>

        <div class="yield-hero">
            <div>
                <div class="yield-eyebrow">ESTIMATED ACTIVE PHOTOVOLTAIC GENERATION</div>
                <div class="yield-location">{html.escape(short_name.upper())} // GRID DISPATCH ESTIMATE</div>
                <div class="yield-note">Random Forest ensemble inference scaled by array tilt ({panel_tilt}&deg;) &amp; azimuth ({panel_az}&deg;).</div>
            </div>
            <div class="yield-number-box">
                <span class="yield-number">{pred_kw:,.2f}</span><span class="yield-unit">kW</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if times_list:
            df_48 = pd.DataFrame({"time": pd.to_datetime(times_list[:48])})
            preds_48 = []
            for i in range(min(48, len(times_list))):
                t_row = dict(active_telemetry)
                t_row.update(
                    {
                        "temperature_2_m_above_gnd": float(hourly_block["temperature_2m"][i]),
                        "relative_humidity_2_m_above_gnd": float(hourly_block["relative_humidity_2m"][i]),
                        "total_cloud_cover_sfc": float(hourly_block["cloud_cover"][i]),
                        "shortwave_radiation_backwards_sfc": float(hourly_block["shortwave_radiation"][i]),
                        "wind_speed_10_m_above_gnd": float(hourly_block["wind_speed_10m"][i]),
                    }
                )
                preds_48.append(predict_power_kw(t_row, is_day=int(hourly_block["is_day"][i]), geometry_scale=geometry_factor))
            df_48["power_kw"] = preds_48
            df_48["p90_upper"] = np.array(preds_48) * 1.10
            df_48["p10_lower"] = np.array(preds_48) * 0.90

            fig_48 = go.Figure()
            fig_48.add_trace(
                go.Scatter(
                    x=list(df_48["time"]) + list(df_48["time"])[::-1],
                    y=list(df_48["p90_upper"]) + list(df_48["p10_lower"])[::-1],
                    fill="toself",
                    fillcolor="rgba(14, 165, 233, 0.08)",
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    name="P10-P90 Uncertainty Band",
                )
            )
            fig_48.add_trace(
                go.Scatter(
                    x=df_48["time"],
                    y=df_48["power_kw"],
                    mode="lines",
                    name="Predicted PV Output (kW)",
                    line=dict(color="#f59e0b", width=2.8, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(245, 158, 11, 0.15)",
                    hovertemplate="<b>%{x|%a %H:%M}</b><br>Output: <b>%{y:,.1f} kW</b><extra></extra>",
                )
            )
            fig_48.update_layout(
                title=dict(
                    text="48-HOUR DIURNAL GENERATION PROFILE (SPLINE INTERPOLATION)",
                    font=dict(family="JetBrains Mono, monospace", size=11, color="#94a3b8"),
                ),
                paper_bgcolor="rgba(10, 16, 29, 0.84)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=345,
                margin=dict(l=12, r=12, t=42, b=14),
                hovermode="x unified",
                xaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.08)", tickfont=dict(family="JetBrains Mono", size=10, color="#64748b")),
                yaxis=dict(
                    title="Power (kW)",
                    showgrid=True,
                    gridcolor="rgba(148, 163, 184, 0.08)",
                    tickfont=dict(family="JetBrains Mono", size=10, color="#64748b"),
                    zeroline=False,
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94a3b8")),
            )
            st.plotly_chart(fig_48, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# ------------------------------------------------------------------------------
# TAB 2: MANUAL TELEMETRY CONTROLS & FEATURE MATRIX
# ------------------------------------------------------------------------------
with tab_matrix:
    m_left, m_right = st.columns([2.2, 1.0], gap="large")
    manual_inputs = {}
    with m_left:
        for cat_name, cat_tag in [
            ("Solar Geometry & Flux", "IRRADIANCE & INCIDENCE VECTORS"),
            ("Atmospheric Cloud Layers", "THREE-TIER CLOUD OPACITY"),
            ("Surface Meteorology", "BOUNDARY LAYER THERMODYNAMICS"),
            ("Multi-Altitude Wind Profile", "ANEMOMETER & HUB SHEAR"),
        ]:
            st.markdown(
                f"""<div class="section-strip"><div class="panel-title">{html.escape(cat_name)}</div><span class="panel-tag">{html.escape(cat_tag)}</span></div>""",
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            for idx, (col_key, clean_label, unit_str, default_val, _) in enumerate([i for i in FEATURE_SCHEMA if i[4] == cat_name]):
                with cols[idx % 3]:
                    manual_inputs[col_key] = st.number_input(
                        f"{clean_label} [{unit_str}]", value=float(default_val), step=0.5, format="%.2f", key=f"man_{col_key}"
                    )

    with m_right:
        man_kw = predict_power_kw(manual_inputs, is_day=1)
        st.markdown(
            f"""
        <div class="yield-hero" style="flex-direction:column; align-items:flex-start;">
            <div class="yield-eyebrow">MANUAL TELEMETRY DISPATCH SIMULATION</div>
            <div class="yield-number" style="margin:0.5rem 0;">{man_kw:,.2f}<span class="yield-unit">kW</span></div>
            <div class="yield-note">Real-time Random Forest response across all 20 atmospheric &amp; geometric parameters.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        oob_warnings = [
            f"• **{clean_label}**: `{manual_inputs[col_key]:.1f} {unit_str}` outside training range (`{feature_bounds[col_key][0]:.1f}` – `{feature_bounds[col_key][1]:.1f}`)"
            for col_key, clean_label, unit_str, _, _ in FEATURE_SCHEMA
            if col_key in feature_bounds and (manual_inputs[col_key] < feature_bounds[col_key][0] or manual_inputs[col_key] > feature_bounds[col_key][1])
        ]
        st.markdown(
            """<div class="section-strip"><div class="panel-title">Model Domain Diagnostics</div><span class="panel-tag">20 FEATURES</span></div>""",
            unsafe_allow_html=True,
        )
        if oob_warnings:
            st.warning("Extrapolation detected:\n\n" + "\n".join(oob_warnings[:6]))
        else:
            st.success("All 20 manual inputs reside within historical training distribution bounds.")

# ------------------------------------------------------------------------------
# TAB 3: NASA POWER HISTORICAL VALIDATION WORKBENCH
# ------------------------------------------------------------------------------
with tab_nasa:
    st.markdown(
        f"""
    <div class="telemetry-bar">
        <div>
            <strong style="color:#f8fafc;">NASA LARC POWER ARCHIVE //</strong>
            Validating most recent published 7-day satellite window for <strong>{html.escape(short_name.upper())}</strong> ({lat_val:.4f}&deg;N, {lon_val:.4f}&deg;E)
        </div>
        <span class="panel-tag">TIME STANDARD: UTC</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    df_nasa = fetch_nasa_power_recent(lat_val, lon_val)
    if not df_nasa.empty:
        st.markdown(
            f"""
        <div class="kpi-grid" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
            <div class="kpi-card"><div class="kpi-top"><span class="kpi-name">PEAK SATELLITE IRRADIANCE</span></div><div class="kpi-value">{df_nasa["irradiance_wm2"].max():,.0f}<span class="kpi-unit">W/m&sup2;</span></div><div class="kpi-sub">NASA ALLSKY_SFC_SW_DWN</div></div>
            <div class="kpi-card"><div class="kpi-top"><span class="kpi-name">PEAK MODEL OUTPUT</span></div><div class="kpi-value">{df_nasa["predicted_kw"].max():,.0f}<span class="kpi-unit">kW</span></div><div class="kpi-sub">7-Day Maximum Dispatch</div></div>
            <div class="kpi-card"><div class="kpi-top"><span class="kpi-name">CUMULATIVE 7-DAY YIELD</span></div><div class="kpi-value">{(df_nasa["predicted_kw"].sum() / 1000.0):,.1f}<span class="kpi-unit">MWh</span></div><div class="kpi-sub">Integrated Hourly Generation</div></div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        fig_nasa = go.Figure()
        fig_nasa.add_trace(
            go.Scatter(
                x=df_nasa["timestamp"],
                y=df_nasa["irradiance_wm2"],
                name="NASA Surface Irradiance (W/m2)",
                mode="lines",
                line=dict(color="#f59e0b", width=2.4, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(245, 158, 11, 0.13)",
            )
        )
        fig_nasa.add_trace(
            go.Scatter(
                x=df_nasa["timestamp"],
                y=df_nasa["predicted_kw"],
                name="Model Estimated Power (kW)",
                mode="lines",
                line=dict(color="#0ea5e9", width=2.4, shape="spline"),
                yaxis="y2",
            )
        )
        fig_nasa.update_layout(
            title=dict(
                text="7-DAY SATELLITE IRRADIANCE vs. RANDOM FOREST POWER RECONSTRUCTION",
                font=dict(family="JetBrains Mono, monospace", size=11, color="#94a3b8"),
            ),
            paper_bgcolor="rgba(10, 16, 29, 0.84)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(l=14, r=14, t=46, b=16),
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.08)", tickfont=dict(family="JetBrains Mono", size=10, color="#64748b")),
            yaxis=dict(
                title="Irradiance (W/m2)",
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.08)",
                tickfont=dict(family="JetBrains Mono", size=10, color="#f59e0b"),
            ),
            yaxis2=dict(
                title="Model Output (kW)",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(family="JetBrains Mono", size=10, color="#0ea5e9"),
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94a3b8")),
        )
        st.plotly_chart(fig_nasa, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.download_button(
            "Export 7-Day NASA Validation Dataset (CSV)",
            data=df_nasa.to_csv(index=False).encode("utf-8"),
            file_name=f"spgx_nasa_validation_{short_name.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No valid hourly records returned from NASA POWER for the selected window.")

# ==============================================================================
# 8. CORPORATE ARCHITECTURE & SUPPORTING APIs FOOTER DOCK
# ==============================================================================
st.markdown(
    """
<div class="arch-footer">
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; font-weight:700; color:#94a3b8; letter-spacing:0.12em; text-transform:uppercase; display:flex; align-items:center; gap:8px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
        SYSTEM INFRASTRUCTURE // SUPPORTING APIS &amp; TELEMETRY PIPELINES
    </div>
    <div class="arch-grid">
        <div class="arch-card"><div class="arch-role">METEOROLOGICAL FORECASTING</div><div class="arch-provider">Open-Meteo Weather API</div><div class="arch-desc">Real-time 15-minute &amp; hourly numerical weather prediction (NWP), multi-altitude wind shear (10m/80m), and shortwave radiation flux.</div></div>
        <div class="arch-card"><div class="arch-role">SATELLITE VALIDATION</div><div class="arch-provider">NASA LaRC POWER Archive</div><div class="arch-desc">Prediction Of Worldwide Energy Resources (Agroclimatology &amp; Renewable Energy) surface shortwave downward irradiance.</div></div>
        <div class="arch-card"><div class="arch-role">GEOSPATIAL &amp; LIVE GPS</div><div class="arch-provider">HTML5 Geolocation &amp; CARTO</div><div class="arch-desc">Hardware browser GPS acquisition with reverse geocoding, OpenStreetMap contributors &amp; CARTO DarkMatter vector map lock.</div></div>
        <div class="arch-card"><div class="arch-role">MACHINE LEARNING &amp; VISUALIZATION</div><div class="arch-provider">Scikit-Learn RF &amp; Plotly WebGL</div><div class="arch-desc">20-feature Random Forest regression ensemble paired with solar zenith/AOI geometry synthesis and spline-interpolated diurnal curves.</div></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)