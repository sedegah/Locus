/**
 * Locus Math Engine — Web Client Application Logic
 */

// Application State
const state = {
    currentMode: '2D', // '2D', 'Derivative', 'Integral', 'Riemann', 'Parametric', 'Polar', '3D', 'Vector'
    currentEquation: 'y = x^3 - 3x^2 + x - 19',
    lastData: null,
    animation: {
        isPlaying: false,
        frame: 0,
        totalFrames: 100,
        speed: 1.0,
        mode: 'trace', // 'trace', 'tangent', 'riemann', 'sweep'
        timerId: null,
    },
    activeInput: null,
};

// UI Element References
const elements = {
    eq2D: document.getElementById('eq-2d'),
    paramX: document.getElementById('param-x'),
    paramY: document.getElementById('param-y'),
    polarR: document.getElementById('polar-r'),
    surfZ: document.getElementById('surf-z'),
    colormapSelect: document.getElementById('colormap-select'),
    vectorDx: document.getElementById('vector-dx'),
    vectorDy: document.getElementById('vector-dy'),
    riemannSlider: document.getElementById('riemann-slider'),
    riemannNVal: document.getElementById('riemann-n-val'),
    riemannMethod: document.getElementById('riemann-method'),
    equationDisplay: document.getElementById('equation-display'),
    analysisOutput: document.getElementById('analysis-output'),
    analysisSpinner: document.getElementById('analysis-spinner'),
    graphContainer: document.getElementById('graph-container'),
    animScrubber: document.getElementById('anim-scrubber'),
    frameCounter: document.getElementById('frame-counter'),
    btnPlay: document.getElementById('btn-anim-play'),
    btnReset: document.getElementById('btn-anim-reset'),
    btnStepFw: document.getElementById('btn-anim-step-fw'),
    btnStepBw: document.getElementById('btn-anim-step-bw'),
    animSpeed: document.getElementById('anim-speed'),
    animMode: document.getElementById('anim-mode'),
    btnFullscreen: document.getElementById('btn-fullscreen'),
    btnSnapshot: document.getElementById('btn-snapshot'),
};

// Dark Cyber Plotly Layout Defaults
const darkPlotlyLayout = {
    paper_bgcolor: '#090A0F',
    plot_bgcolor: '#090A0F',
    font: { family: 'IBM Plex Sans, sans-serif', color: '#94A3B8', size: 11 },
    margin: { l: 50, r: 25, t: 30, b: 40 },
    xaxis: {
        gridcolor: '#1C2030',
        zerolinecolor: '#4A5568',
        zerolinewidth: 1.2,
        linecolor: '#262938',
        tickcolor: '#94A3B8',
        autorange: true,
    },
    yaxis: {
        gridcolor: '#1C2030',
        zerolinecolor: '#4A5568',
        zerolinewidth: 1.2,
        linecolor: '#262938',
        tickcolor: '#94A3B8',
        autorange: true,
    },
    hoverlabel: {
        bgcolor: '#11131B',
        bordercolor: '#FFC72C',
        font: { family: 'IBM Plex Sans', color: '#FFFFFF', size: 12 },
    },
    legend: {
        x: 0.02,
        y: 0.98,
        bgcolor: 'rgba(17, 19, 27, 0.85)',
        bordercolor: '#262938',
        borderwidth: 1,
        font: { color: '#FFFFFF', size: 11 },
    },
    showlegend: true,
};

const plotlyConfig = {
    responsive: true,
    displayModeBar: false,
};

// API Helper
async function fetchAPI(endpoint, payload) {
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const json = await res.json();
        if (!res.ok || json.error) {
            throw new Error(json.error || 'Server request failed');
        }
        return json;
    } catch (err) {
        console.error(`API Error on ${endpoint}:`, err);
        showToast(`Error: ${err.message}`, true);
        return null;
    }
}

// 1. Plot 2D Cartesian
async function plot2D(equation) {
    state.currentMode = '2D';
    state.currentEquation = equation || elements.eq2D.value;
    pauseAnimation();
    elements.equationDisplay.textContent = state.currentEquation;

    const data = await fetchAPI('/api/eval_2d', { equation: state.currentEquation });
    if (!data) return;
    state.lastData = data;

    const traceGlow = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        line: { color: 'rgba(255, 199, 44, 0.3)', width: 6 },
        hoverinfo: 'none',
        showlegend: false,
    };

    const traceMain = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `f(x) = ${data.equation_latex}`,
        line: { color: '#FFC72C', width: 2.5 },
        hovertemplate: '<b>x:</b> %{x:.2f}<br><b>f(x):</b> %{y:.2f}<extra></extra>',
    };

    Plotly.react(elements.graphContainer, [traceGlow, traceMain], {
        ...darkPlotlyLayout,
        title: { text: `f(x) = ${data.equation_latex}`, font: { color: '#FFFFFF', size: 14 } },
    }, plotlyConfig);
}

// 2. Plot Derivative Overlay
async function plotDerivative() {
    state.currentMode = 'Derivative';
    pauseAnimation();
    const equation = elements.eq2D.value;
    elements.equationDisplay.textContent = `f(x) & f'(x): ${equation}`;

    const data = await fetchAPI('/api/eval_derivative', { equation });
    if (!data) return;
    state.lastData = data;

    const traceF = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `f(x)`,
        line: { color: '#FFC72C', width: 2.2 },
    };

    const traceDf = {
        x: data.x,
        y: data.dy,
        type: 'scatter',
        mode: 'lines',
        name: `f'(x) = ${data.derivative_latex}`,
        line: { color: '#FF2E93', width: 2.2, dash: 'dash' },
    };

    Plotly.react(elements.graphContainer, [traceF, traceDf], {
        ...darkPlotlyLayout,
        title: { text: `f'(x) = ${data.derivative_latex}`, font: { color: '#FF2E93', size: 13 } },
    }, plotlyConfig);
}

// 3. Plot Integral Area
async function plotIntegral() {
    state.currentMode = 'Integral';
    pauseAnimation();
    const equation = elements.eq2D.value;
    const a = -2.0, b = 2.0;
    elements.equationDisplay.textContent = `∫ [${a}, ${b}] of ${equation}`;

    const data = await fetchAPI('/api/eval_integral', { equation, a, b });
    if (!data) return;
    state.lastData = data;

    const traceF = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `f(x)`,
        line: { color: '#FFC72C', width: 2 },
    };

    const traceFill = {
        x: data.x_fill,
        y: data.y_fill,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: 'rgba(16, 185, 129, 0.35)',
        line: { color: '#10B981', width: 1.5 },
        name: `Area [${a}, ${b}] ≈ ${data.exact_value ?? ''}`,
    };

    Plotly.react(elements.graphContainer, [traceF, traceFill], {
        ...darkPlotlyLayout,
        title: { text: `Integral Area [${a}, ${b}] = ${data.exact_value}`, font: { color: '#10B981', size: 13 } },
    }, plotlyConfig);
}

// 4. Plot Riemann Sum
async function plotRiemann() {
    state.currentMode = 'Riemann';
    pauseAnimation();
    const equation = elements.eq2D.value;
    const n = parseInt(elements.riemannSlider.value, 10) || 12;
    const method = elements.riemannMethod.value;
    elements.equationDisplay.textContent = `Riemann Sum (N=${n}, ${method})`;

    const data = await fetchAPI('/api/eval_riemann', { equation, n, method });
    if (!data) return;
    state.lastData = data;

    const shapes = data.rectangles.map(rect => ({
        type: 'rect',
        x0: rect.x0,
        x1: rect.x1,
        y0: rect.y0,
        y1: rect.y1,
        fillcolor: 'rgba(168, 85, 247, 0.45)',
        line: { color: '#00E5FF', width: 1.2 },
    }));

    const traceCurve = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `f(x)`,
        line: { color: '#FFC72C', width: 2 },
    };

    Plotly.react(elements.graphContainer, [traceCurve], {
        ...darkPlotlyLayout,
        shapes: shapes,
        title: { text: `Riemann Sum (${method}, N=${n}) Area ≈ ${data.total_area}`, font: { color: '#00E5FF', size: 13 } },
    }, plotlyConfig);
}

// 5. Plot Parametric
async function plotParametric() {
    state.currentMode = 'Parametric';
    pauseAnimation();
    const expr_x = elements.paramX.value;
    const expr_y = elements.paramY.value;
    elements.equationDisplay.textContent = `x(t)=${expr_x}, y(t)=${expr_y}`;

    const data = await fetchAPI('/api/eval_parametric', { expr_x, expr_y });
    if (!data) return;
    state.lastData = data;

    const traceGlow = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        line: { color: 'rgba(255, 46, 147, 0.3)', width: 6 },
        showlegend: false,
    };

    const trace = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `x(t), y(t)`,
        line: { color: '#FF2E93', width: 2.5 },
    };

    Plotly.react(elements.graphContainer, [traceGlow, trace], {
        ...darkPlotlyLayout,
        yaxis: { ...darkPlotlyLayout.yaxis, scaleanchor: 'x', scaleratio: 1 },
        title: { text: `Parametric: x(t)=${data.latex_x}, y(t)=${data.latex_y}`, font: { color: '#FFFFFF', size: 13 } },
    }, plotlyConfig);
}

// 6. Plot Polar
async function plotPolar() {
    state.currentMode = 'Polar';
    pauseAnimation();
    const expr_r = elements.polarR.value;
    elements.equationDisplay.textContent = `r(θ) = ${expr_r}`;

    const data = await fetchAPI('/api/eval_polar', { expr_r });
    if (!data) return;
    state.lastData = data;

    const trace = {
        x: data.x,
        y: data.y,
        type: 'scatter',
        mode: 'lines',
        name: `r(θ)`,
        line: { color: '#10B981', width: 2.5 },
        fill: 'toself',
        fillcolor: 'rgba(16, 185, 129, 0.1)',
    };

    Plotly.react(elements.graphContainer, [trace], {
        ...darkPlotlyLayout,
        yaxis: { ...darkPlotlyLayout.yaxis, scaleanchor: 'x', scaleratio: 1 },
        title: { text: `Polar: r(θ) = ${data.latex_r}`, font: { color: '#10B981', size: 13 } },
    }, plotlyConfig);
}

// 7. Plot 3D Surface
async function plot3D() {
    state.currentMode = '3D';
    pauseAnimation();
    const expr_z = elements.surfZ.value;
    const colormap = elements.colormapSelect.value;
    elements.equationDisplay.textContent = `z = ${expr_z}`;

    const data = await fetchAPI('/api/eval_3d', { expr_z });
    if (!data) return;
    state.lastData = data;

    const trace3D = {
        x: data.x,
        y: data.y,
        z: data.z,
        type: 'surface',
        colorscale: colormap,
        contours: {
            z: { show: true, usecolormap: true, highlightcolor: '#FFC72C', project: { z: true } },
        },
        showscale: false,
    };

    const layout3D = {
        paper_bgcolor: '#090A0F',
        font: { family: 'IBM Plex Sans, sans-serif', color: '#94A3B8' },
        margin: { l: 0, r: 0, t: 30, b: 0 },
        scene: {
            xaxis: { backgroundcolor: '#0D0F18', gridcolor: '#1E2333', color: '#94A3B8' },
            yaxis: { backgroundcolor: '#0D0F18', gridcolor: '#1E2333', color: '#94A3B8' },
            zaxis: { backgroundcolor: '#0D0F18', gridcolor: '#1E2333', color: '#94A3B8' },
            camera: { eye: { x: 1.5, y: 1.5, z: 1.2 } },
        },
        title: { text: `z = ${data.latex_z}`, font: { color: '#FFFFFF', size: 13 } },
    };

    Plotly.react(elements.graphContainer, [trace3D], layout3D, plotlyConfig);
}

// 8. Plot Vector Field
async function plotVectorField() {
    state.currentMode = 'Vector';
    pauseAnimation();
    const dx = elements.vectorDx.value;
    const dy = elements.vectorDy.value;
    elements.equationDisplay.textContent = `dx/dt=${dx}, dy/dt=${dy}`;

    const data = await fetchAPI('/api/eval_vector', { dx, dy });
    if (!data) return;
    state.lastData = data;

    // Build vector arrow lines
    const arrowX = [], arrowY = [], speeds = [];
    const scale = 0.28;

    data.vectors.forEach(v => {
        const uNorm = v.speed > 0 ? (v.u / v.speed) * scale : 0;
        const vNorm = v.speed > 0 ? (v.v / v.speed) * scale : 0;
        arrowX.push(v.x, v.x + uNorm, null);
        arrowY.push(v.y, v.y + vNorm, null);
        speeds.push(v.speed);
    });

    const traceVectors = {
        x: arrowX,
        y: arrowY,
        type: 'scatter',
        mode: 'lines',
        line: { color: '#FFC72C', width: 1.8 },
        hoverinfo: 'none',
        showlegend: false,
    };

    Plotly.react(elements.graphContainer, [traceVectors], {
        ...darkPlotlyLayout,
        title: { text: `Vector Field: dx/dt=${data.latex_dx}, dy/dt=${data.latex_dy}`, font: { color: '#FF2E93', size: 13 } },
    }, plotlyConfig);
}

// 9. Symbolic Analysis (KaTeX)
async function runAnalysis() {
    const equation = elements.eq2D.value;
    elements.analysisSpinner.classList.remove('hidden');
    elements.analysisOutput.innerHTML = '<p class="placeholder-text">Computing symbolic analysis...</p>';

    const res = await fetchAPI('/api/analyze', { equation });
    elements.analysisSpinner.classList.add('hidden');
    if (!res || !res.data || res.data.error) {
        elements.analysisOutput.innerHTML = `<p style="color:#FF2E93;">${res?.data?.error || 'Analysis failed'}</p>`;
        return;
    }

    const d = res.data;
    const items = [
        { label: 'Function f(x)', tex: `f(x) = ${d.original}` },
        { label: "1st Derivative f'(x)", tex: `f'(x) = ${d.derivative}` },
        { label: "2nd Derivative f''(x)", tex: `f''(x) = ${d.second_derivative}` },
        { label: 'Real Roots', tex: `x \\in ${d.real_roots}` },
        { label: 'Critical Points', tex: `x \\in ${d.critical_points}` },
        { label: 'Concavity & Extrema', tex: d.concavity },
        { label: 'Indefinite Integral', tex: `\\int f(x)\\,dx = ${d.integral} + C` },
        { label: 'Domain', tex: `D_f = ${d.domain}` },
    ];

    elements.analysisOutput.innerHTML = items.map(item => `
        <div class="analysis-item">
            <span class="analysis-label">${item.label}</span>
            <div class="analysis-math" id="katex-${Math.random().toString(36).substr(2, 9)}"></div>
        </div>
    `).join('');

    // Render KaTeX for each item
    const containers = elements.analysisOutput.querySelectorAll('.analysis-math');
    items.forEach((item, i) => {
        if (window.katex && containers[i]) {
            try {
                katex.render(item.tex, containers[i], { throwOnError: false, displayMode: false });
            } catch (e) {
                containers[i].textContent = item.tex;
            }
        }
    });
}

// Animation Loop
function startAnimation() {
    if (state.animation.isPlaying) return;
    state.animation.isPlaying = true;
    elements.btnPlay.textContent = '⏸ Pause';
    elements.btnPlay.classList.add('playing');
    stepAnimation();
}

function pauseAnimation() {
    state.animation.isPlaying = false;
    elements.btnPlay.textContent = '▶ Play';
    elements.btnPlay.classList.remove('playing');
    if (state.animation.timerId) {
        clearTimeout(state.animation.timerId);
        state.animation.timerId = null;
    }
}

function stepAnimation() {
    if (!state.animation.isPlaying) return;

    state.animation.frame = (state.animation.frame + 1) % state.animation.totalFrames;
    updateAnimationFrame(state.animation.frame);

    const interval = Math.max(16, 40 / state.animation.speed);
    state.animation.timerId = setTimeout(stepAnimation, interval);
}

function updateAnimationFrame(frame) {
    elements.animScrubber.value = frame;
    elements.frameCounter.textContent = `Frame: ${frame}/100`;

    if (!state.lastData || !state.lastData.x) return;

    const mode = elements.animMode.value;
    const totalPts = state.lastData.x.length;

    if (mode === 'trace') {
        // Reveal curve up to current frame percentage
        const count = Math.max(2, Math.floor((frame / 100) * totalPts));
        const subX = state.lastData.x.slice(0, count);
        const subY = state.lastData.y ? state.lastData.y.slice(0, count) : null;

        if (subY) {
            Plotly.restyle(elements.graphContainer, { x: [subX], y: [subY] }, [1]);
        }
    } else if (mode === 'tangent' && state.lastData.y) {
        // Glide tangent line
        const idx = Math.min(totalPts - 2, Math.floor((frame / 100) * totalPts));
        const x0 = state.lastData.x[idx];
        const y0 = state.lastData.y[idx];
        const x1 = state.lastData.x[idx + 1];
        const y1 = state.lastData.y[idx + 1];
        if (y0 !== null && y1 !== null) {
            const slope = (y1 - y0) / (x1 - x0);
            const tanX = [x0 - 2, x0 + 2];
            const tanY = [y0 - 2 * slope, y0 + 2 * slope];

            const traceTan = {
                x: tanX,
                y: tanY,
                type: 'scatter',
                mode: 'lines+markers',
                marker: { size: [0, 8], color: '#00E5FF' },
                line: { color: '#00E5FF', width: 2, dash: 'dot' },
                name: 'Tangent',
            };
            Plotly.react(elements.graphContainer, [
                { x: state.lastData.x, y: state.lastData.y, type: 'scatter', mode: 'lines', line: { color: '#FFC72C', width: 2 } },
                traceTan,
            ], darkPlotlyLayout, plotlyConfig);
        }
    } else if (mode === 'riemann') {
        // Animate N from 1 to 50
        const n = 1 + Math.floor((frame / 100) * 49);
        elements.riemannSlider.value = n;
        elements.riemannNVal.textContent = n;
        plotRiemann();
    }
}

// Preset Loader
const PRESETS = {
    cubic: { tab: 'tab-2d', eq: 'y = x^3 - 3x^2 + x - 19', fn: () => plot2D('y = x^3 - 3x^2 + x - 19') },
    gaussian: { tab: 'tab-2d', eq: 'y = exp(-x^2 / 2) / sqrt(2*pi)', fn: () => plot2D('y = exp(-x^2 / 2) / sqrt(2*pi)') },
    damped: { tab: 'tab-2d', eq: 'y = exp(-0.3*x) * cos(3*x)', fn: () => plot2D('y = exp(-0.3*x) * cos(3*x)') },
    butterfly: { tab: 'tab-param', r: 'exp(cos(theta)) - 2*cos(4*theta) + sin(theta/12)^5', fn: () => { elements.polarR.value = 'exp(cos(theta)) - 2*cos(4*theta) + sin(theta/12)^5'; plotPolar(); } },
    saddle: { tab: 'tab-3d', z: 'x^2 - y^2', fn: () => { elements.surfZ.value = 'x^2 - y^2'; plot3D(); } },
    sombrero: { tab: 'tab-3d', z: 'sin(sqrt(x^2 + y^2)) / sqrt(x^2 + y^2 + 0.01)', fn: () => { elements.surfZ.value = 'sin(sqrt(x^2 + y^2)) / sqrt(x^2 + y^2 + 0.01)'; plot3D(); } },
    spiral: { tab: 'tab-3d', dx: 'y', dy: '-x - 0.2*y', fn: () => { elements.vectorDx.value = 'y'; elements.vectorDy.value = '-x - 0.2*y'; plotVectorField(); } },
    circle: { tab: 'tab-param', x: '5*cos(t)', y: '5*sin(t)', fn: () => { elements.paramX.value = '5*cos(t)'; elements.paramY.value = '5*sin(t)'; plotParametric(); } },
};

function loadPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    if (p.eq) elements.eq2D.value = p.eq;
    p.fn();
}

// UI Event Listeners
function setupEventListeners() {
    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.dataset.tab;
            document.getElementById(targetId)?.classList.add('active');
        });
    });

    // Virtual Math Keyboard
    document.querySelectorAll('.kb-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const ins = btn.dataset.insert;
            const targetInput = state.activeInput || elements.eq2D;
            const pos = targetInput.selectionStart || targetInput.value.length;
            targetInput.value = targetInput.value.slice(0, pos) + ins + targetInput.value.slice(pos);
            targetInput.focus();
            targetInput.setSelectionRange(pos + ins.length, pos + ins.length);
        });
    });

    // Track active focused input
    document.querySelectorAll('.math-input').forEach(inp => {
        inp.addEventListener('focus', () => { state.activeInput = inp; });
        inp.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                if (inp === elements.eq2D) plot2D();
                else if (inp === elements.paramX || inp === elements.paramY) plotParametric();
                else if (inp === elements.polarR) plotPolar();
                else if (inp === elements.surfZ) plot3D();
                else if (inp === elements.vectorDx || inp === elements.vectorDy) plotVectorField();
            }
        });
    });

    // 2D Tab Buttons
    document.getElementById('btn-plot-2d').addEventListener('click', () => plot2D());
    document.getElementById('btn-analyze').addEventListener('click', runAnalysis);
    document.getElementById('btn-derivative').addEventListener('click', plotDerivative);
    document.getElementById('btn-integral').addEventListener('click', plotIntegral);
    document.getElementById('btn-riemann').addEventListener('click', plotRiemann);

    elements.riemannSlider.addEventListener('input', (e) => {
        elements.riemannNVal.textContent = e.target.value;
    });

    // Parametric & Polar Buttons
    document.getElementById('btn-plot-param').addEventListener('click', plotParametric);
    document.getElementById('btn-plot-polar').addEventListener('click', plotPolar);

    // 3D & Vector Buttons
    document.getElementById('btn-plot-3d').addEventListener('click', plot3D);
    elements.colormapSelect.addEventListener('change', plot3D);
    document.getElementById('btn-plot-vector').addEventListener('click', plotVectorField);

    // Presets
    document.querySelectorAll('.preset-card').forEach(card => {
        card.addEventListener('click', () => loadPreset(card.dataset.preset));
    });

    // Animation Controls
    elements.btnPlay.addEventListener('click', () => {
        if (state.animation.isPlaying) pauseAnimation();
        else startAnimation();
    });
    elements.btnReset.addEventListener('click', () => {
        pauseAnimation();
        state.animation.frame = 0;
        updateAnimationFrame(0);
    });
    elements.btnStepFw.addEventListener('click', () => {
        pauseAnimation();
        state.animation.frame = (state.animation.frame + 1) % 100;
        updateAnimationFrame(state.animation.frame);
    });
    elements.btnStepBw.addEventListener('click', () => {
        pauseAnimation();
        state.animation.frame = (state.animation.frame - 1 + 100) % 100;
        updateAnimationFrame(state.animation.frame);
    });
    elements.animScrubber.addEventListener('input', (e) => {
        pauseAnimation();
        state.animation.frame = parseInt(e.target.value, 10);
        updateAnimationFrame(state.animation.frame);
    });
    elements.animSpeed.addEventListener('change', (e) => {
        state.animation.speed = parseFloat(e.target.value);
    });

    // Snapshot & Fullscreen
    elements.btnSnapshot.addEventListener('click', () => {
        Plotly.downloadImage(elements.graphContainer, {
            format: 'png',
            width: 1600,
            height: 1000,
            filename: 'locus_plot',
        });
    });

    elements.btnFullscreen.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    });

    // Auto-resize Plotly on window resize
    window.addEventListener('resize', () => {
        Plotly.Plots.resize(elements.graphContainer);
    });
}

function showToast(msg, isError = false) {
    console.log(`[Toast] ${msg}`);
}

// Initial Boot
window.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    plot2D();
    runAnalysis();
});
