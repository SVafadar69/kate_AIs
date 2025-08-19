import streamlit as st
from functools import partial
import html
import json
import time
import re
from html import escape as html_escape

# (Optional) helpers you already use elsewhere
from helper_functions import retrieve_prompt, retrieve_template  # not used here, safe to keep

# ── Import the existing run() functions (unchanged in other files) ────────────
from treatment_options import run as treatment_options_run
from treatment_options_dr import run as treatment_options_dr_run
from diagnosis import run as diagnosis_run
from diagnosis_dr import run as diagnosis_dr_run
from recommendations import run as recommendations_run
from recommendations_dr import run as recommendations_dr_run
from follow_up import run as follow_up_run
from follow_up_dr import run as follow_up_dr_run
from soap_notes import run as soap_notes_run
from soap_notes_dr import run as soap_notes_dr_run
from all_in_one import run as all_in_one_run            # ✅ non-DR All-In-One
from all_in_one_dr import run as all_in_one_dr_run      # ✅ DR All-In-One

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Medical Documentation", layout="wide")

# ----------------- Unified Medical Theme -----------------
st.markdown("""
<style>
:root{
  --bg: #ffffff;
  --surface: #ffffff;
  --surface-2: #f8fafc;
  --border: #e5e7eb;
  --text: #0f172a;
  --muted: #475569;
  --accent: #14b8a6;
  --accent-hover: #0fa29a;
  --accent-weak: #a7f3d0;
  --accent-contrast: #ffffff;
}
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background: var(--bg) !important; color: var(--text) !important;
}
h1,h2,h3,h4,h5,h6,p,span,label,div{ color: var(--text) !important; }
.main { padding: 2rem; }

/* Cards */
.section-card{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 18px 18px 12px 18px;
  box-shadow: 0 2px 12px rgba(15,23,42,0.06); margin-bottom: 18px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  display:flex; gap:10px; padding:8px;
  border-radius:14px; background: var(--surface-2);
  border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"]{
  border-radius:10px; font-weight:600;
  padding:10px 16px; transition:all .15s ease;
  background: var(--surface); color: var(--text);
  border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"]:hover{
  border-color: var(--accent);
  box-shadow: 0 2px 10px rgba(20,184,166,0.15);
}
.stTabs [aria-selected="true"]{
  background: var(--accent);
  color: var(--accent-contrast) !important;
  border-color: var(--accent);
  box-shadow: 0 4px 16px rgba(20,184,166,0.30);
}

.stRadio label{ font-weight:600; }

/* Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: var(--accent-contrast) !important;
  border: 1px solid var(--accent) !important;
  border-radius: 12px !important;
  padding: .6rem 1rem !important;
  font-weight: 700 !important;
  box-shadow: 0 6px 18px rgba(20,184,166,0.28) !important;
  transition: transform .12s ease, filter .12s ease;
}
.stButton > button:hover { filter: brightness(1.03); transform: translateY(-1px); }
.stButton > button:focus { outline: 3px solid var(--accent-weak) !important; }

/* Read-only output panel (force light theme) */
.pre-block{
  white-space: pre-wrap;
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  line-height: 1.5;
  box-shadow: 0 1px 6px rgba(15,23,42,0.06);
}
.placeholder { color: #64748b; font-style: italic; }

/* Pretty SOAP styling */
.soap-wrap{ display:flex; flex-direction:column; gap:14px; }
.soap-card{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 2px 10px rgba(15,23,42,0.06);
}
.soap-title{ margin:0 0 8px 0; font-size:1.05rem; line-height:1.4; }
.soap-body ul, .soap-body ol{ margin:0 0 4px 1.25rem; }
.soap-body li{ margin:2px 0; }
.soap-body b{ font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ----------------- State -----------------
def init_tab_state(tab_name: str):
  mode_key = f"{tab_name}_mode"
  out_key  = f"{tab_name}_output"
  if mode_key not in st.session_state:
    st.session_state[mode_key] = "Detailed"
  if out_key not in st.session_state:
    st.session_state[out_key] = ""

def on_mode_change(tab_name: str):
  radio_key = f"radio_{tab_name}"
  mode_key  = f"{tab_name}_mode"
  st.session_state[mode_key] = st.session_state[radio_key]

# ----------------- Helpers -----------------
def stringify_result(res):
  """Normalize whatever the AI returns to a string."""
  if res is None:
    return ""
  if isinstance(res, str):
    return res
  if isinstance(res, dict):
    for k in ("text", "output", "result", "content"):
      v = res.get(k)
      if isinstance(v, str):
        return v
    return json.dumps(res, indent=2, ensure_ascii=False)
  return str(res)

def stream_chunks_to_panel(chunks_iter, placeholder, pretty_renderer=None):
  """
  Consume a generator/iterator yielding text chunks and update the UI on each.
  Returns the concatenated final text.
  """
  acc = ""
  for chunk in chunks_iter:
    if chunk is None:
      continue
    s = str(chunk)
    if not s:
      continue
    acc += s
    placeholder.markdown(
      f'<pre class="pre-block">{html_escape(acc)}</pre>',
      unsafe_allow_html=True
    )
  if pretty_renderer:
    pretty_renderer(acc, placeholder)
  return acc

def stream_text_to_panel(text: str, placeholder, delay: float = 0.0):
  """
  If run() returns a full string, simulate streaming by pushing larger slices.
  """
  text = text or ""
  step = max(64, len(text)//60)  # ~60 updates
  for i in range(0, len(text), step):
    placeholder.markdown(
      f'<pre class="pre-block">{html_escape(text[:i+step])}</pre>',
      unsafe_allow_html=True
    )
    if delay:
      time.sleep(delay)
  return text

# --------- Pretty SOAP renderer (cards & lists) ----------
def _card(title: str, body_html: str) -> str:
  return f"""
  <div class="soap-card">
    <h3 class="soap-title">{html_escape(title)}</h3>
    <div class="soap-body">{body_html}</div>
  </div>
  """

def _kv_to_list_html(lines):
  items = []
  for ln in lines:
    ln = ln.strip()
    if not ln:
      continue
    if ":" in ln:
      k, v = ln.split(":", 1)
      items.append(f"<li><b>{html_escape(k.strip())}:</b> {html_escape(v.strip())}</li>")
    else:
      items.append(f"<li>{html_escape(ln)}</li>")
  return "<ul>" + "".join(items) + "</ul>" if items else ""

def _numbered_to_ol_html(lines):
  items = []
  for ln in lines:
    m = re.match(r"\s*\d+\.\s*(.*)", ln)
    if m and m.group(1).strip():
      items.append(f"<li>{html_escape(m.group(1).strip())}</li>")
  return "<ol>" + "".join(items) + "</ol>" if items else ""

def _star_list_to_ul_html(lines):
  items = []
  for ln in lines:
    m = re.match(r"\s*\*\s*(.*)", ln)
    if m and m.group(1).strip():
      items.append(f"<li>{html_escape(m.group(1).strip())}</li>")
  return "<ul>" + "".join(items) + "</ul>" if items else ""

def render_soap_pretty(text: str, placeholder):
  raw = (text or "").strip()
  raw = re.sub(r"[ \t]+", " ", raw)
  raw = re.sub(r"\n{3,}", "\n\n", raw)

  sections = [
    "SOAP Chart Note",
    "Presenting Concerns",
    "Medical History",
    "Lifestyle Snapshot",
    "Wellbeing Scores",
    "Women’s Health",
    "Women's Health",
    "Family History",
    "Review of Symptoms",
    "Latest Lab Test",
  ]
  pattern = r"(?m)^(%s)\s*$" % "|".join([re.escape(s) for s in sections])
  parts = re.split(pattern, raw)

  if len(parts) == 1:
    placeholder.markdown(
      f'<div class="soap-card"><div class="soap-body">{html_escape(raw).replace("\\n","<br/>")}</div></div>',
      unsafe_allow_html=True
    )
    return

  it = iter(parts)
  leading = next(it)
  cards_html = []
  if leading.strip():
    cards_html.append(_card("Summary", html_escape(leading).replace("\n","<br/>")))

  for title, content in zip(it, it):
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if title in ("SOAP Chart Note",):
      body_html = _kv_to_list_html(lines) or html_escape(content).replace("\n","<br/>")
    elif title in ("Presenting Concerns", "Medical History", "Lifestyle Snapshot",
                   "Women’s Health", "Women's Health", "Latest Lab Test"):
      bullets = _kv_to_list_html(lines)
      nums    = _numbered_to_ol_html(lines)
      stars   = _star_list_to_ul_html(lines)
      combined = "".join([b for b in (bullets, nums, stars) if b])
      body_html = combined or html_escape(content).replace("\n","<br/>")
    elif title in ("Wellbeing Scores", "Family History", "Review of Symptoms"):
      nums    = _numbered_to_ol_html(lines)
      bullets = _kv_to_list_html(lines)
      stars   = _star_list_to_ul_html(lines)
      combined = "".join([b for b in (nums, bullets, stars) if b])
      body_html = combined or html_escape(content).replace("\n","<br/>")
    else:
      body_html = html_escape(content).replace("\n","<br/>")
    cards_html.append(_card(title, body_html))

  html_out = f"""<div class="soap-wrap">{''.join(cards_html)}</div>"""
  placeholder.markdown(html_out, unsafe_allow_html=True)

# ----------------- Mode dispatch using ONLY existing run() --------------------
def call_runner(standard_run, dr_run, mode: str):
  """
  Call your existing run() function. If it returns a generator/iterator,
  we stream chunks; if it returns a string, we handle it as a full string.
  (No changes to other files are required.)
  """
  func = dr_run if mode == "Detailed" else standard_run
  try:
    result = func()           # your existing run()
  except TypeError:
    result = func("")         # some of your runs accept an optional arg
  return result

def run_diagnoses_ai(mode: str):
  return call_runner(diagnosis_run, diagnosis_dr_run, mode)

def run_follow_up_ai(mode: str):
  return call_runner(follow_up_run, follow_up_dr_run, mode)

def run_treatment_ai(mode: str):
  return call_runner(treatment_options_run, treatment_options_dr_run, mode)

def run_recommendations_ai(mode: str):
  return call_runner(recommendations_run, recommendations_dr_run, mode)

def run_soap_notes_ai(mode: str):
  return call_runner(soap_notes_run, soap_notes_dr_run, mode)

# ✅ All-In-One runner with SAME UI pattern as other tabs:
#    - "Detailed" → non-DR all_in_one_run
#    - "General"  → DR all_in_one_dr_run
def run_all_in_one_ai(mode: str):
  func = all_in_one_run if mode == "Detailed" else all_in_one_dr_run
  try:
    result = func()
  except TypeError:
    result = func("")
  return result

# ----------------- Tabs -----------------
tabs = st.tabs([
  "Transcript",
  "Diagnoses",
  "Follow-up Questions",
  "Treatment Options",
  "Recommendations",
  "SOAP Notes",
  "All-In-One",   # ✅ uses the exact same radio + 'Run AI' button UI
])

# ----------------- Transcript Tab (read-only) -----------------
with tabs[0]:
  st.markdown('<div class="section-card">', unsafe_allow_html=True)
  st.header("🗒 Transcript")
  try:
    transcript_text = retrieve_template("transcript.txt")
  except Exception:
    transcript_text = "Transcript unavailable."
  st.markdown(f'<pre class="pre-block">{html_escape(transcript_text)}</pre>', unsafe_allow_html=True)
  st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Reusable Tab Builder -----------------
def create_content_tab(tab_name, icon, runner, pretty_renderer=None, show_mode=True):
  init_tab_state(tab_name)
  mode_key = f"{tab_name}_mode"
  out_key  = f"{tab_name}_output"
  radio_key = f"radio_{tab_name}"

  st.markdown('<div class="section-card">', unsafe_allow_html=True)
  st.header(f"{icon} {tab_name}")

  # Mode toggle (same across tabs)
  if show_mode:
    st.radio(
      "Mode:",
      ["Detailed", "General"],
      index=0 if st.session_state[mode_key] == "Detailed" else 1,
      key=radio_key,
      on_change=partial(on_mode_change, tab_name),
      horizontal=True,
      help="Switch between a detailed or general writing mode."
    )
  else:
    st.session_state[mode_key] = "Detailed"

  # Output panel placeholder
  panel = st.empty()
  existing = st.session_state[out_key]
  if existing and pretty_renderer:
    pretty_renderer(existing, panel)
  elif existing:
    panel.markdown(f'<pre class="pre-block">{html_escape(existing)}</pre>', unsafe_allow_html=True)
  else:
    panel.markdown('<pre class="pre-block placeholder">AI output will stream here…</pre>', unsafe_allow_html=True)

  # Run AI (same single button label & style as other tabs)
  btn_key = f"run_ai_{tab_name.lower().replace(' ', '_')}"
  if st.button("Run AI", key=btn_key):
    mode = st.session_state[mode_key]
    with st.spinner(f"Running AI for {tab_name}…"):
      result = runner(mode)

    # Stream if generator/iterator, else simulate streaming
    if hasattr(result, "__iter__") and not isinstance(result, (str, bytes, dict)):
      final_text = stream_chunks_to_panel(result, panel, pretty_renderer=pretty_renderer)
      st.session_state[out_key] = final_text
    else:
      final_text = stringify_result(result)
      st.session_state[out_key] = stream_text_to_panel(final_text, panel, delay=0.0)
      if pretty_renderer:
        pretty_renderer(final_text, panel)

  st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Content Tabs -----------------
with tabs[1]:
  create_content_tab("Diagnoses", "🩺", run_diagnoses_ai)

with tabs[2]:
  create_content_tab("Follow-up Questions", "❓", run_follow_up_ai)

with tabs[3]:
  create_content_tab("Treatment Options", "💊", run_treatment_ai)

with tabs[4]:
  create_content_tab("Recommendations", "📋", run_recommendations_ai)

with tabs[5]:
  create_content_tab("SOAP Notes", "🧾", run_soap_notes_ai, pretty_renderer=render_soap_pretty)

with tabs[6]:
  # ✅ EXACT SAME UI as other tabs (radio + single 'Run AI' button)
  create_content_tab("All-In-One", "📊", run_all_in_one_ai)
