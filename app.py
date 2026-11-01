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
# 2. FLUID FULL-SCREEN, MOBILE-LOCKED & 3D SCROLL-POP DESIGN SYSTEM
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
    padding-bottom: 2.5rem !important;
    margin: 0 auto !important;
}

/* ==========================================================================
   3D SCROLL-ROLL, SPRING POP-UP, FLOATING TILE & HOLO-SWEEP KEYFRAMES
   ========================================================================== */
@keyframes rollPopIn3D {
    0% {
        opacity: 0;
        transform: perspective(1000px) rotateX(24deg) translateY(34px) scale(0.92);
    }
    65% {
        opacity: 1;
        transform: perspective(1000px) rotateX(-3deg) translateY(-4px) scale(1.015);
    }
    100% {
        opacity: 1;
        transform: perspective(1000px) rotateX(0deg) translateY(0px) scale(1);
    }
}

@keyframes cardShufflePop {
    0% {
        opacity: 0;
        transform: perspective(900px) rotateY(-16deg) rotateX(12deg) translateY(28px) scale(0.9);
    }
    70% {
        opacity: 1;
        transform: perspective(900px) rotateY(2deg) rotateX(-2deg) translateY(-4px) scale(1.02);
    }
    100% {
        opacity: 1;
        transform: perspective(900px) rotateY(0deg) rotateX(0deg) translateY(0px) scale(1);
    }
}

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

.scroll-roll-card {
    animation: rollPopIn3D 0.7s cubic-bezier(0.22, 1.28, 0.36, 1) both;
    will-change: transform, opacity;
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
   COMPACT SECTION HEADER STRIP (ZERO EMPTY BOX GAP)
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
   KPI TELEMETRY DECK (HOLO-SWEEP + FLOATING TILES + POP-UP HOVER)
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
    animation: cardShufflePop 0.65s cubic-bezier(0.22, 1.28, 0.36, 1) both, tileFloat 5.5s ease-in-out infinite;
}

.kpi-card:nth-child(1) { animation-delay: 0.04s, 0.0s; }
.kpi-card:nth-child(2) { animation-delay: 0.10s, 0.7s; }
.kpi-card:nth-child(3) { animation-delay: 0.16s, 1.4s; }
.kpi-card:nth-child(4) { animation-delay: 0.22s, 2.1s; }
.kpi-card:nth-child(5) { animation-delay: 0.28s, 2.8s; }

/* Holographic Sheen Sweep Across Tiles */
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
    transform: perspective(1000px) rotateX(3deg) translateY(-4px) scale(1.01);
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
    transform: perspective(800px) rotateX(5deg) translateY(-6px) scale(1.02);
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
        padding-bottom: 2rem !important;
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
            headers={"User-Agent": "SPGX-Solar-Workbench/5.0"},
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
    """Parse queries like 'GPS: 22.5867, 88.4750' or '22.5867, 88.4750' directly into coordinates."""
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

    # Direct GPS Coordinate Bridge (Triggered when user clicks Detect My Live GPS Location)
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
<div class="corp-header scroll-roll-card">
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

<div class="marquee-shell scroll-roll-card">
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
            <span class="api-badge"><span class="api-dot"></span>Komoot Photon Spatial Search</span>
            <span class="api-badge"><span class="api-dot"></span>Scikit-Learn Random Forest (20-Feature Ensemble)</span>
            <span class="api-badge"><span class="api-dot"></span>Open-Meteo NWP Weather API</span>
            <span class="api-badge"><span class="api-dot"></span>NASA LaRC POWER Satellite Archive</span>
            <span class="api-badge"><span class="api-dot"></span>HTML5 Browser GPS Geolocation</span>
            <span class="api-badge"><span class="api-dot"></span>OpenStreetMap Contributors &amp; CARTO Maps</span>
            <span class="api-badge"><span class="api-dot"></span>Komoot Photon Spatial Search</span>
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
# TAB 1: FULL-SCREEN BENTO TELEMETRY, LIVE GPS & CARTO MAP WORKBENCH
# ------------------------------------------------------------------------------
with tab_live:
    col_left, col_right = st.columns([1.05, 2.15], gap="large")

    with col_left:
        st.markdown(
            """
        <div class="section-strip scroll-roll-card">
            <div class="panel-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                Spatial Target &amp; Live GPS Lock
            </div>
            <span class="panel-tag">GPS + CARTO MAP</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Unclipped Full-Width Mobile/Desktop GPS Button + Dynamic 3D Scroll-Pop Engine
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
                .gps-btn {
                    width: 100%;
                    min-height: 48px;
                    padding: 10px 14px;
                    border-radius: 10px;
                    border: 1.5px solid rgba(16, 185, 129, 0.65);
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(14, 165, 233, 0.18) 100%);
                    color: #f8fafc;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: clamp(10.5px, 2.7vw, 12px);
                    font-weight: 700;
                    letter-spacing: 0.05em;
                    line-height: 1.3;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    gap: 9px;
                    box-shadow: 0 6px 18px -4px rgba(16, 185, 129, 0.28);
                    transition: all 0.25s cubic-bezier(0.22, 1.28, 0.36, 1);
                }
                .gps-btn:hover, .gps-btn:active {
                    border-color: #f59e0b;
                    transform: translateY(-2px) scale(1.01);
                    box-shadow: 0 10px 22px -4px rgba(245, 158, 11, 0.35);
                }
                .gps-dot {
                    width: 9px;
                    height: 9px;
                    min-width: 9px;
                    border-radius: 50%;
                    background: #10b981;
                    box-shadow: 0 0 10px #10b981;
                }
            </style>
            </head>
            <body>
                <button id="gpsBtn" class="gps-btn" onclick="requestLiveGPS()">
                    <span id="gpsDot" class="gps-dot"></span>
                    <span id="gpsBtnText">DETECT MY LIVE GPS LOCATION (AUTO-FEED)</span>
                </button>

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
                        btnText.innerText = 'GPS NOT SUPPORTED BY BROWSER';
                        return;
                    }

                    btnText.innerText = 'ACQUIRING SATELLITE / BROWSER GPS...';
                    dot.style.background = '#f59e0b';
                    dot.style.boxShadow = '0 0 12px #f59e0b';

                    geo.getCurrentPosition(
                        function(pos) {
                            const lat = pos.coords.latitude.toFixed(5);
                            const lon = pos.coords.longitude.toFixed(5);
                            dot.style.background = '#10b981';
                            btnText.innerText = 'LIVE GPS LOCKED: ' + lat + '°N, ' + lon + '°E';
                            feedCoordsToStreamlit(lat, lon);
                        },
                        function(err) {
                            dot.style.background = '#ef4444';
                            btnText.innerText = 'LOCATION BLOCKED // ENABLE PERMISSION IN BROWSER';
                        },
                        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
                    );
                }

                // Dynamic 3D Scroll-Roll & Pop-Up Physics Engine on Parent Page
                try {
                    const parentDoc = window.parent.document;
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach((entry) => {
                            if (entry.isIntersecting) {
                                entry.target.style.opacity = '1';
                                entry.target.style.transform = 'perspective(950px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)';
                            } else {
                                const rect = entry.boundingClientRect;
                                const tiltDir = rect.top > 0 ? 14 : -12;
                                entry.target.style.opacity = '0.72';
                                entry.target.style.transform = 'perspective(950px) rotateX(' + tiltDir + 'deg) translateY(' + (rect.top > 0 ? '20px' : '-14px') + ') scale(0.95)';
                            }
                        });
                    }, { threshold: [0.08, 0.25] });

                    const attachAnimations = () => {
                        const selector = '.section-strip, .kpi-card, .yield-hero, .arch-card, .telemetry-bar, [data-testid="stPlotlyChart"], [data-testid="stNumberInput"], [data-testid="stSelectbox"], [data-testid="stTextInput"]';
                        parentDoc.querySelectorAll(selector).forEach((el) => {
                            if (!el.dataset.rollAttached) {
                                el.dataset.rollAttached = '1';
                                el.style.transition = 'transform 0.52s cubic-bezier(0.22, 1.28, 0.36, 1), opacity 0.45s ease, border-color 0.3s ease, box-shadow 0.35s ease';
                                observer.observe(el);
                            }
                        });
                    };

                    setTimeout(attachAnimations, 250);
                    setInterval(attachAnimations, 1500);
                } catch (e) {}
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
        # Outer Radar Pulse Halo
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
        # Inner Target Ring + Label
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
        <div class="telemetry-bar scroll-roll-card">
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

        <div class="yield-hero scroll-roll-card">
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
                f"""<div class="section-strip scroll-roll-card"><div class="panel-title">{html.escape(cat_name)}</div><span class="panel-tag">{html.escape(cat_tag)}</span></div>""",
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
        <div class="yield-hero scroll-roll-card" style="flex-direction:column; align-items:flex-start;">
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
            """<div class="section-strip scroll-roll-card"><div class="panel-title">Model Domain Diagnostics</div><span class="panel-tag">20 FEATURES</span></div>""",
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
    <div class="telemetry-bar scroll-roll-card">
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
<div class="arch-footer scroll-roll-card">
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