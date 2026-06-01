"""Generate mobile-demo.html for FallGuard Edge AI."""
import numpy as np, json, os

# ── 讀取 demo 序列資料 ──────────────────────────────────
windows = np.load('data/demo_windows.npy')  # (13, 6, 200)
sel = np.vstack([windows[:3], windows[5:10]])  # 3 normal + 5 fall
flat = [[round(v, 3) for v in row] for row in sel.reshape(8, -1).tolist()]
demo_json = json.dumps({'w': flat, 'l': [0,0,0,1,1,1,1,1]}, separators=(',', ':'))

# ── HTML ─────────────────────────────────────────────────
CSS = """
:root{
  --bg:#070c18;--bg2:#0c1428;--bg3:#111c35;
  --cyan:#00d4ff;--green:#00e676;--orange:#ff6b35;
  --gold:#ffd060;--red:#ff3b30;--text:#dce8f4;--dim:#7a8fa8;
  --border:rgba(0,212,255,.18);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{
  width:100%;min-height:100dvh;background:var(--bg);color:var(--text);
  font-family:'Space Grotesk','Noto Sans TC',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;overflow-x:hidden;
}
header{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 20px 12px;border-bottom:1px solid var(--border);background:var(--bg2);
}
.logo{font-size:20px;font-weight:700;letter-spacing:-.5px}
.logo span{color:var(--cyan)}
#status-dot{
  width:9px;height:9px;border-radius:50%;background:var(--dim);
  display:inline-block;margin-right:6px;transition:background .3s;
}
#status-dot.ready{background:var(--green);box-shadow:0 0 8px var(--green)}
#status-dot.loading{background:var(--gold);animation:blink 1s infinite}
#status-dot.error{background:var(--red)}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
#status-txt{font-size:11px;color:var(--dim)}
.mode-tabs{
  display:flex;gap:8px;padding:12px 20px;
  background:var(--bg2);border-bottom:1px solid var(--border);
}
.tab{
  flex:1;padding:11px;border-radius:8px;border:1px solid var(--border);
  background:transparent;color:var(--dim);font-size:13px;font-weight:600;
  cursor:pointer;transition:all .2s;letter-spacing:.3px;
}
.tab.active{background:rgba(0,212,255,.12);border-color:var(--cyan);color:var(--cyan)}
main{display:flex;flex-direction:column;align-items:center;padding:20px 18px;gap:16px}
.gauge-wrap{display:flex;flex-direction:column;align-items:center;gap:4px}
.gauge-label{font-size:10px;color:var(--dim);letter-spacing:2px;text-transform:uppercase}
.prob-track{width:200px;height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;margin-top:4px}
.prob-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--green),var(--gold),var(--red));transition:width .3s ease;width:0%}
.sparks-grid{width:100%;display:grid;grid-template-columns:1fr 1fr;gap:8px}
.spark-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px}
.spark-ch{font-size:10px;color:var(--cyan);margin-bottom:4px;font-weight:600}
.spark-canvas{width:100%;height:36px;display:block}
.stats-bar{
  width:100%;display:flex;justify-content:space-around;
  background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px;
}
.stat{display:flex;flex-direction:column;align-items:center;gap:3px}
.stat-v{font-size:16px;font-weight:700;color:var(--cyan)}
.stat-l{font-size:10px;color:var(--dim);letter-spacing:.5px}
.info-box{
  width:100%;padding:10px 14px;border-radius:8px;font-size:12px;line-height:1.6;
}
.info-warn{border:1px solid rgba(255,107,53,.3);background:rgba(255,107,53,.06);color:var(--orange)}
.info-ok{border:1px solid rgba(0,230,118,.25);background:rgba(0,230,118,.05);color:var(--green)}
.infer-log{
  width:100%;background:rgba(0,0,0,.4);border:1px solid var(--border);
  border-radius:8px;padding:10px;font-family:monospace;font-size:11px;
  color:var(--dim);max-height:90px;overflow-y:auto;
}
.log-fall{color:var(--red);font-weight:700}
.log-ok{color:var(--green)}
.btn-row{width:100%;display:flex;gap:10px}
.btn{
  flex:1;padding:14px;border-radius:10px;border:1px solid var(--border);
  background:rgba(0,212,255,.08);color:var(--cyan);
  font-size:14px;font-weight:600;cursor:pointer;transition:all .15s;
}
.btn:active{transform:scale(.96)}
.btn.red{background:rgba(255,59,48,.08);border-color:rgba(255,59,48,.3);color:var(--red)}
.btn.disabled{opacity:.35;pointer-events:none}
#fall-overlay{
  display:none;position:fixed;inset:0;z-index:999;
  background:rgba(200,10,10,.93);backdrop-filter:blur(4px);
  flex-direction:column;align-items:center;justify-content:center;
  gap:16px;text-align:center;padding:30px;
}
#fall-overlay.show{display:flex;animation:flashIn .12s ease}
@keyframes flashIn{from{background:rgba(255,50,50,1)}to{background:rgba(200,10,10,.93)}}
.ov-icon{font-size:64px;animation:shake .4s ease}
@keyframes shake{0%,100%{transform:rotate(0)}25%{transform:rotate(-8deg)}75%{transform:rotate(8deg)}}
.ov-title{font-size:34px;font-weight:800;color:#fff;letter-spacing:-1px}
.ov-sub{font-size:14px;color:rgba(255,255,255,.75)}
.ov-prob{font-size:52px;font-weight:800;color:#fff;line-height:1}
.ov-reset{
  padding:14px 40px;border-radius:10px;
  background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);
  color:#fff;font-size:15px;font-weight:600;cursor:pointer;margin-top:8px;
}
"""

JS = r"""
/* ─── DEMO 序列（SisFall 測試集，已正規化） ─── */
const DEMO_SEQ = /** DEMO_JSON_PLACEHOLDER **/;

/* ─── 正規化參數（train split 計算） ─── */
const NORM_MEAN = [-1.299, -178.747, -27.916, -9.409, 34.232, -4.739];
const NORM_STD  = [105.654, 150.739, 125.410, 598.633, 496.772, 406.495];
const EPS = 1e-8;

/* ADXL345 ±16g full-res: 256 LSB/g ÷ 9.81 m/s²  = 26.1 LSB/(m/s²) */
/* ITG3200: 14.375 LSB/(deg/s)                                         */
const ADXL_SCALE = 256 / 9.81;
const ITG_SCALE  = 14.375;

/* ─── State ─── */
let session = null;
let mode = 'demo';
let liveOn = false;
let winCount = 0, maxProb = 0;

const BUF = 200, NCH = 6, STRIDE = 100;
const buf = Array.from({length: NCH}, () => new Float32Array(BUF));
let bufPos = 0, bufFull = false, strideC = 0;

const SLEN = 80;
const spk = Array.from({length: NCH}, () => new Float32Array(SLEN));
let spkPos = 0;

let fpsC = 0, fpsT = performance.now();

/* ─── Model loading ─── */
async function loadModel() {
  setStatus('loading', '載入模型中...');
  try {
    ort.env.wasm.numThreads = 1;
    session = await ort.InferenceSession.create('./models/best_1dcnn.onnx', {
      executionProviders: ['wasm'],
      graphOptimizationLevel: 'all',
    });
    setStatus('ready', '模型就緒 ✓');
    log('✓ 模型載入：best_1dcnn.onnx (866 KB)', 'ok');
    log('✓ 推論後端：ONNX Runtime Web (WASM)', 'ok');
    document.querySelectorAll('.btn.disabled').forEach(b => b.classList.remove('disabled'));
  } catch(e) {
    setStatus('error', '載入失敗');
    log('✗ ' + e.message, 'fall');
    console.error(e);
  }
}

function setStatus(s, t) {
  document.getElementById('status-dot').className = s;
  document.getElementById('status-txt').textContent = t;
}

/* ─── Inference ─── */
async function infer(data6x200) {
  if (!session) return null;
  const t0 = performance.now();
  const tensor = new ort.Tensor('float32', data6x200, [1, 6, 200]);
  const res = await session.run({'imu_window': tensor});
  const logit = res['fall_logit'].data[0];
  const p = 1 / (1 + Math.exp(-logit));
  document.getElementById('st-ms').textContent = (performance.now() - t0).toFixed(1);
  return p;
}

/* ─── Normalize (LIVE) ─── */
function normalize(raw) {
  const out = new Float32Array(NCH * BUF);
  for (let c = 0; c < NCH; c++)
    for (let t = 0; t < BUF; t++)
      out[c * BUF + t] = (raw[c * BUF + t] - NORM_MEAN[c]) / (NORM_STD[c] + EPS);
  return out;
}

/* ─── Sample buffer (LIVE) ─── */
function addSample(s) {
  for (let c = 0; c < NCH; c++) {
    buf[c][bufPos] = s[c];
    spk[c][spkPos % SLEN] = s[c] / (NORM_STD[c] + EPS);
  }
  bufPos++; spkPos++;

  fpsC++;
  const now = performance.now();
  if (now - fpsT >= 1000) {
    document.getElementById('st-fps').textContent = fpsC;
    fpsC = 0; fpsT = now;
  }

  drawSparks();

  if (bufPos >= BUF) { bufFull = true; bufPos = 0; }
  if (!bufFull) return;
  if (++strideC < STRIDE) return;
  strideC = 0;

  const ord = new Float32Array(NCH * BUF);
  for (let c = 0; c < NCH; c++)
    for (let t = 0; t < BUF; t++)
      ord[c * BUF + t] = buf[c][(bufPos + t) % BUF];

  infer(normalize(ord)).then(p => { if (p !== null) updateUI(p); });
}

/* ─── Live sensor ─── */
function toggleLive() {
  if (!session) { log('⌛ 等待模型載入', 'fall'); return; }
  liveOn ? stopLive() : tryStartLive();
}

function tryStartLive() {
  if (typeof DeviceMotionEvent !== 'undefined' &&
      typeof DeviceMotionEvent.requestPermission === 'function') {
    DeviceMotionEvent.requestPermission()
      .then(s => { if (s === 'granted') bindSensor(); else log('❌ 感測器權限被拒', 'fall'); })
      .catch(e => log('❌ ' + e.message, 'fall'));
  } else {
    bindSensor();
  }
}

function bindSensor() {
  liveOn = true;
  const btn = document.getElementById('btn-live');
  btn.textContent = '⏹ 停止偵測'; btn.classList.add('red');
  window.addEventListener('devicemotion', onMotion);
  log('🟢 感測器啟動（DeviceMotionEvent）', 'ok');
  if (!navigator.userAgent.match(/Android|iPhone|iPad/i))
    log('⚠ 非行動裝置，可能無感測器資料', 'fall');
}

function stopLive() {
  liveOn = false;
  window.removeEventListener('devicemotion', onMotion);
  const btn = document.getElementById('btn-live');
  btn.textContent = '▶ 開始偵測'; btn.classList.remove('red');
  log('⏹ 停止', 'ok');
}

function onMotion(e) {
  const a = e.accelerationIncludingGravity, r = e.rotationRate;
  if (!a) { log('⚠ 無加速度計', 'fall'); return; }
  addSample([
    (a.x||0)*ADXL_SCALE, (a.y||0)*ADXL_SCALE, (a.z||0)*ADXL_SCALE,
    r?(r.alpha||0)*ITG_SCALE:0, r?(r.beta||0)*ITG_SCALE:0, r?(r.gamma||0)*ITG_SCALE:0
  ]);
}

/* ─── Demo playback ─── */
async function startDemo() {
  if (!session) { log('⌛ 等待模型載入', 'fall'); return; }
  resetProb();
  log('▶ DEMO 播放中（SisFall 測試集視窗）', 'ok');

  for (let i = 0; i < DEMO_SEQ.w.length; i++) {
    const w = new Float32Array(DEMO_SEQ.w[i]);
    const lbl = DEMO_SEQ.l[i];
    updateSparksFromWin(w);
    const p = await infer(w);
    if (p === null) break;
    updateUI(p, false);  // 不自動觸發 alert（讓最後一個有效）
    const pct = (p * 100).toFixed(1);
    log(`${lbl?'🔴':'🟢'} 視窗 ${i+1}：${pct}%  (${lbl?'FALL':'NORMAL'})`, lbl?'fall':'ok');
    await sleep(lbl === 0 ? 900 : 700);
  }

  // 最後一個 fall 視窗觸發 alert
  const lastP = await infer(new Float32Array(DEMO_SEQ.w[DEMO_SEQ.w.length-1]));
  if (lastP && lastP > 0.5) showAlert(Math.round(lastP*100));

  log('✓ DEMO 結束', 'ok');
}

/* ─── UI ─── */
function updateUI(p, doAlert=true) {
  const pct = Math.round(p * 100);
  const arc = document.getElementById('g-arc');
  const fill = Math.min(p, 1) * 252;
  arc.setAttribute('stroke-dasharray', `${fill} ${252-fill}`);
  const col = p < 0.3 ? '#00e676' : p < 0.6 ? '#ffd060' : '#ff3b30';
  arc.setAttribute('stroke', col);
  const pe = document.getElementById('g-pct');
  pe.textContent = pct + '%';
  pe.style.fill = col;
  document.getElementById('prob-fill').style.width = pct + '%';
  winCount++;
  document.getElementById('st-win').textContent = winCount;
  if (p > maxProb) {
    maxProb = p;
    document.getElementById('st-max').textContent = Math.round(maxProb*100) + '%';
  }
  if (doAlert && p > 0.5) showAlert(pct);
}

function resetProb() {
  document.getElementById('g-arc').setAttribute('stroke-dasharray', '0 252');
  const pe = document.getElementById('g-pct');
  pe.textContent = '0%'; pe.style.fill = '#dce8f4';
  document.getElementById('prob-fill').style.width = '0%';
  winCount = 0; maxProb = 0;
  document.getElementById('st-win').textContent = '0';
  document.getElementById('st-max').textContent = '0%';
}

function showAlert(pct) {
  document.getElementById('ov-prob').textContent = pct + '%';
  document.getElementById('fall-overlay').classList.add('show');
}

function resetAll() {
  document.getElementById('fall-overlay').classList.remove('show');
  resetProb();
  bufPos = 0; bufFull = false; strideC = 0;
  if (liveOn) stopLive();
  log('⟳ 已重置', 'ok');
}

/* ─── Sparklines ─── */
function drawSparks() {
  for (let c = 0; c < NCH; c++) {
    const cv = document.getElementById('sp'+c);
    if (!cv) continue;
    const ctx = cv.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const W = cv.offsetWidth || 140, H = cv.offsetHeight || 36;
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = c < 3 ? '#00d4ff' : '#ffd060';
    ctx.lineWidth = 1.2; ctx.globalAlpha = .85;
    ctx.beginPath();
    for (let i = 0; i < SLEN; i++) {
      const x = (i / SLEN) * W;
      const v = spk[c][(spkPos + i) % SLEN];
      const y = Math.max(2, Math.min(H-2, H/2 - (v/2.5)*(H/2-4)));
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

function updateSparksFromWin(w) {
  const step = Math.floor(200 / SLEN);
  for (let c = 0; c < NCH; c++)
    for (let i = 0; i < SLEN; i++)
      spk[c][(spkPos + i) % SLEN] = w[c*200 + Math.min(i*step, 199)];
  spkPos += SLEN;
  drawSparks();
}

/* ─── Mode switch ─── */
function switchMode(m) {
  mode = m;
  document.getElementById('tl').classList.toggle('active', m==='live');
  document.getElementById('td').classList.toggle('active', m==='demo');
  document.getElementById('live-panel').style.display = m==='live' ? '' : 'none';
  document.getElementById('demo-panel').style.display = m==='demo' ? '' : 'none';
  if (liveOn) stopLive();
  resetAll();
}

/* ─── Helper ─── */
function log(msg, type) {
  const el = document.getElementById('infer-log');
  const d = document.createElement('div');
  d.textContent = msg;
  d.className = type === 'fall' ? 'log-fall' : type === 'ok' ? 'log-ok' : '';
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
  while (el.children.length > 25) el.removeChild(el.firstChild);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

window.onload = () => {
  switchMode('demo');
  loadModel();
};
"""

JS = JS.replace('/** DEMO_JSON_PLACEHOLDER **/', demo_json)

HTML = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>FallGuard — 即時跌倒偵測</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header>
  <div class="logo">Fall<span>Guard</span></div>
  <div style="display:flex;align-items:center;gap:5px">
    <span id="status-dot" class="loading"></span>
    <span id="status-txt">載入中...</span>
  </div>
</header>

<div class="mode-tabs">
  <button class="tab" id="tl" onclick="switchMode('live')">📡 LIVE 感測器</button>
  <button class="tab active" id="td" onclick="switchMode('demo')">▶ DEMO 模擬</button>
</div>

<main>

  <!-- Gauge -->
  <div class="gauge-wrap">
    <div class="gauge-label">Fall Probability</div>
    <svg viewBox="0 0 200 130" width="210">
      <path d="M 20 110 A 80 80 0 0 1 180 110" stroke="#1a2a3a" stroke-width="16" fill="none"/>
      <path id="g-arc" d="M 20 110 A 80 80 0 0 1 180 110"
        stroke="#00d4ff" stroke-width="16" fill="none" stroke-linecap="round"
        stroke-dasharray="0 252"/>
      <text x="100" y="90" text-anchor="middle" fill="#dce8f4"
        font-size="32" font-weight="700" id="g-pct">0%</text>
      <text x="100" y="110" text-anchor="middle" fill="#7a8fa8" font-size="10">FALL RISK</text>
    </svg>
    <div class="prob-track"><div class="prob-fill" id="prob-fill"></div></div>
  </div>

  <!-- Sparklines -->
  <div class="sparks-grid">
    <div class="spark-card"><div class="spark-ch">acc_x</div><canvas class="spark-canvas" id="sp0"></canvas></div>
    <div class="spark-card"><div class="spark-ch">acc_y</div><canvas class="spark-canvas" id="sp1"></canvas></div>
    <div class="spark-card"><div class="spark-ch">acc_z</div><canvas class="spark-canvas" id="sp2"></canvas></div>
    <div class="spark-card"><div class="spark-ch" style="color:var(--gold)">gyro_x</div><canvas class="spark-canvas" id="sp3"></canvas></div>
    <div class="spark-card"><div class="spark-ch" style="color:var(--gold)">gyro_y</div><canvas class="spark-canvas" id="sp4"></canvas></div>
    <div class="spark-card"><div class="spark-ch" style="color:var(--gold)">gyro_z</div><canvas class="spark-canvas" id="sp5"></canvas></div>
  </div>

  <!-- Stats -->
  <div class="stats-bar">
    <div class="stat"><span class="stat-v" id="st-fps">—</span><span class="stat-l">Hz</span></div>
    <div class="stat"><span class="stat-v" id="st-ms">—</span><span class="stat-l">推論 ms</span></div>
    <div class="stat"><span class="stat-v" id="st-win">0</span><span class="stat-l">視窗數</span></div>
    <div class="stat"><span class="stat-v" id="st-max">0%</span><span class="stat-l">最高機率</span></div>
  </div>

  <!-- LIVE panel -->
  <div id="live-panel" style="display:none;width:100%;display:flex;flex-direction:column;gap:12px">
    <div class="info-box info-warn">
      ⚠️ LIVE 模式：手機感測器（m/s²）透過 ADC 換算後輸入模型。
      因感測器硬體差異與採樣率（≈50Hz vs 200Hz），偵測效果因設備而異。
      建議先用 <strong>DEMO 模式</strong>確認效果。
    </div>
    <div class="btn-row">
      <button class="btn disabled" id="btn-live" onclick="toggleLive()">▶ 開始偵測</button>
      <button class="btn red disabled" onclick="startDemo()">⚠ 模擬跌倒</button>
    </div>
  </div>

  <!-- DEMO panel -->
  <div id="demo-panel" style="width:100%;display:flex;flex-direction:column;gap:12px">
    <div class="info-box info-ok">
      ✓ DEMO 模式：使用 SisFall 測試集真實視窗（已正規化）直接輸入 ONNX 模型推論，
      3 個日常活動視窗 → 5 個跌倒視窗，呈現完整跌倒偵測流程。
    </div>
    <div class="btn-row">
      <button class="btn disabled" id="btn-demo" onclick="startDemo()">▶ 執行 DEMO</button>
      <button class="btn red" onclick="resetAll()">⟳ 重置</button>
    </div>
  </div>

  <!-- Log -->
  <div class="infer-log" id="infer-log">等待模型載入...</div>

</main>

<!-- Fall Alert Overlay -->
<div id="fall-overlay">
  <div class="ov-icon">⚠️</div>
  <div class="ov-title">FALL DETECTED</div>
  <div class="ov-sub">跌倒偵測警報觸發</div>
  <div class="ov-prob" id="ov-prob">—%</div>
  <button class="ov-reset" onclick="resetAll()">⟳ 重置</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/onnxruntime-web@1.19.0/dist/ort.min.js"></script>
<script>{JS}</script>
</body>
</html>"""

with open('mobile-demo.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print('Written mobile-demo.html')
print('Size:', os.path.getsize('mobile-demo.html'), 'bytes =', os.path.getsize('mobile-demo.html')//1024, 'KB')
