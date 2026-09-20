from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ============================================================
# Colors — Astra warm-paper theme
# ============================================================
GREEN = RGBColor(0x2D, 0x5A, 0x3D)
GREEN_DARK = RGBColor(0x1E, 0x3D, 0x29)
GREEN_LIGHT = RGBColor(0xE8, 0xF0, 0xE9)
GREEN_MID = RGBColor(0xB8, 0xD4, 0xC0)
CHARCOAL = RGBColor(0x1A, 0x1A, 0x1A)
TEXT = RGBColor(0x2A, 0x2A, 0x2A)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
LIGHT = RGBColor(0x9A, 0x9A, 0x9A)
PAPER = RGBColor(0xFA, 0xF9, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BROWN = RGBColor(0x8B, 0x73, 0x55)
AMBER = RGBColor(0xB8, 0x86, 0x0B)
DIVIDER = RGBColor(0xE8, 0xE5, 0xDC)

# ============================================================
# Fonts — modern, guaranteed available on Windows
# ============================================================
HEADING_FONT = 'Segoe UI Semibold'   # Strong modern heading
BODY_FONT    = 'Segoe UI'            # Clean body text
MONO_FONT    = 'Consolas'            # Numbers / code

STUDENT_NAME = 'Sakshi'
DEGREE = 'M.Tech'
YEAR = '2025–26'

# ============================================================
# Presentation setup — 16:9 widescreen
# ============================================================
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

slide_count = [0]


def add_slide():
    slide_count[0] += 1
    return prs.slides.add_slide(blank)


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, left, top, width, height, text, size=18, bold=False,
             color=TEXT, align=PP_ALIGN.LEFT, font=BODY_FONT, italic=False,
             anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    return tb


def add_bullets(slide, left, top, width, height, items, size=14,
                color=TEXT, spacing=8, font=BODY_FONT):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if isinstance(item, tuple):
            text, is_bold = item
        else:
            text, is_bold = item, False
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(spacing)
        run = p.add_run()
        run.text = '•   ' + text
        run.font.size = Pt(size)
        run.font.bold = is_bold
        run.font.color.rgb = color
        run.font.name = font
    return tb


def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top),
                                    Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def add_footer(slide, page_num=None):
    add_rect(slide, 0, 7.15, 13.333, 0.02, DIVIDER)
    add_text(slide, 0.7, 7.22, 6, 0.25,
             f'{STUDENT_NAME} · KaamSetu AI · {DEGREE} Research {YEAR}',
             size=9, color=LIGHT)
    if page_num:
        add_text(slide, 11.5, 7.22, 1.1, 0.25, f'{page_num:02d}',
                 size=9, color=LIGHT, align=PP_ALIGN.RIGHT, font=MONO_FONT)


def content_slide(title, subtitle=None):
    s = add_slide()
    set_bg(s, PAPER)
    add_rect(s, 0, 0, 13.333, 0.08, GREEN)
    add_text(s, 0.7, 0.42, 12, 0.6, title, size=26, bold=True,
             color=CHARCOAL, font=HEADING_FONT)
    add_rect(s, 0.7, 1.12, 1.0, 0.035, GREEN)
    if subtitle:
        add_text(s, 0.7, 1.24, 12, 0.4, subtitle, size=12.5,
                 color=MUTED, italic=True)
    add_footer(s, slide_count[0])
    return s


# ============================================================
# SLIDE 1 — Title
# ============================================================
s = add_slide()
set_bg(s, PAPER)
add_rect(s, 0, 0, 0.35, 7.5, GREEN)
add_rect(s, 0.35, 0, 0.06, 7.5, GREEN_MID)

add_text(s, 1.1, 1.55, 11, 0.4, 'M.TECH RESEARCH PROJECT',
         size=11, bold=True, color=GREEN)

add_text(s, 1.1, 2.05, 11.5, 1.3, 'KaamSetu AI',
         size=54, bold=True, color=CHARCOAL, font=HEADING_FONT)

add_text(s, 1.1, 3.35, 11.5, 0.8,
         'Adaptive Distributed AI-Based Rural Workforce Matching System',
         size=19, color=MUTED, italic=True)

add_rect(s, 1.1, 4.35, 2.8, 0.04, GREEN)

add_text(s, 1.1, 4.65, 11, 0.4, 'Presented by',
         size=10, bold=True, color=LIGHT)
add_text(s, 1.1, 4.95, 11, 0.6, STUDENT_NAME,
         size=26, bold=True, color=CHARCOAL, font=HEADING_FONT)
add_text(s, 1.1, 5.55, 11, 0.4, f'{DEGREE} · Research Year {YEAR}',
         size=13, color=MUTED)

add_text(s, 1.1, 6.5, 11, 0.4,
         'XGBoost  ·  OR-Tools CP-SAT  ·  Apache Kafka  ·  Adaptive Scheduling',
         size=10, color=LIGHT, font=MONO_FONT)

# ============================================================
# SLIDE 2 — Agenda
# ============================================================
s = content_slide('Agenda', 'Overview of the presentation')
items = [
    ('01    Problem Statement', True),
    ('02    Research Question & Motivation', True),
    ('03    System Architecture', True),
    ('04    AI Matching Pipeline', True),
    ('05    Three Scheduling Strategies', True),
    ('06    Experimental Setup', True),
    ('07    Results — Measured Performance', True),
    ('08    Research Contribution', True),
    ('09    Live Web Application', True),
    ('10    Conclusion & Future Work', True),
]
add_bullets(s, 1.2, 1.85, 11, 5.2, items, size=14, spacing=11)

# ============================================================
# SLIDE 3 — Problem Statement
# ============================================================
s = content_slide('Problem Statement',
                  'Why rural workforce matching needs a new approach')

add_rect(s, 0.7, 1.85, 5.85, 4.6, WHITE)
add_rect(s, 0.7, 1.85, 5.85, 0.05, GREEN)
add_text(s, 1.0, 2.05, 5.3, 0.4, 'Rural Workers Face',
         size=15, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 1.0, 2.55, 5.3, 3.8, [
    'Difficulty finding suitable work based on their skill',
    'Limited awareness of jobs beyond their village',
    'Dependence on brokers and middlemen',
    'Wage expectations ignored or undercut',
    'Transportation constraints not considered',
    'Long waiting periods between jobs',
], size=12, spacing=7)

add_rect(s, 6.85, 1.85, 5.85, 4.6, WHITE)
add_rect(s, 6.85, 1.85, 5.85, 0.05, BROWN)
add_text(s, 7.15, 2.05, 5.3, 0.4, 'Employers Face',
         size=15, bold=True, color=BROWN, font=HEADING_FONT)
add_bullets(s, 7.15, 2.55, 5.3, 3.8, [
    'Inability to find workers with specific skills quickly',
    'Manual, time-consuming search processes',
    'No way to verify worker reliability or ratings',
    'Budget constraints violated in ad-hoc hiring',
    'Difficulty assembling worker groups for large jobs',
    'No real-time visibility into worker availability',
], size=12, spacing=7)

add_text(s, 0.7, 6.6, 12, 0.5,
         'Existing solutions are manual or centralized — they become slow under high request volumes.',
         size=12, bold=True, color=GREEN)

# ============================================================
# SLIDE 4 — Research Question
# ============================================================
s = content_slide('Research Question',
                  'The central hypothesis behind this work')

add_rect(s, 0.7, 1.9, 12, 2.0, WHITE)
add_rect(s, 0.7, 1.9, 0.06, 2.0, GREEN)
add_text(s, 1.1, 2.15, 11.3, 1.6,
         '"Can adaptive distributed workload management improve the '
         'performance of real-time AI-based rural workforce matching '
         'compared with centralized and static distributed processing?"',
         size=19, italic=True, color=CHARCOAL, font=HEADING_FONT)

add_text(s, 0.7, 4.25, 12, 0.4, 'Motivation',
         size=15, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 4.75, 12, 2.0, [
    'The research focus is adaptive distributed workload management — not just an application.',
    'Performance is measured along latency, throughput, scalability, and load balance.',
    'Three scheduling strategies are compared with an identical AI matcher.',
], size=13, spacing=9)

# ============================================================
# SLIDE 5 — System Architecture
# ============================================================
s = content_slide('System Architecture',
                  'Distributed pipeline with a frozen AI matching component')

add_rect(s, 0.7, 2.1, 3.0, 1.1, WHITE)
add_rect(s, 0.7, 2.1, 3.0, 0.05, GREEN)
add_text(s, 0.8, 2.3, 2.8, 0.35, 'Load Generator',
         size=12, bold=True, color=CHARCOAL, font=HEADING_FONT, align=PP_ALIGN.CENTER)
add_text(s, 0.8, 2.68, 2.8, 0.4, '100 – 5000 requests/sec',
         size=10, color=MUTED, align=PP_ALIGN.CENTER)

add_rect(s, 4.0, 2.1, 3.0, 1.1, WHITE)
add_rect(s, 4.0, 2.1, 3.0, 0.05, GREEN)
add_text(s, 4.1, 2.3, 2.8, 0.35, 'Apache Kafka',
         size=12, bold=True, color=CHARCOAL, font=HEADING_FONT, align=PP_ALIGN.CENTER)
add_text(s, 4.1, 2.68, 2.8, 0.4, '3 topic partitions',
         size=10, color=MUTED, align=PP_ALIGN.CENTER)

add_rect(s, 7.3, 2.1, 5.3, 1.1, WHITE)
add_rect(s, 7.3, 2.1, 5.3, 0.05, GREEN)
add_text(s, 7.4, 2.3, 5.1, 0.35, 'Worker Nodes (1 or 3)',
         size=12, bold=True, color=CHARCOAL, font=HEADING_FONT, align=PP_ALIGN.CENTER)
add_text(s, 7.4, 2.68, 5.1, 0.4, 'XGBoost  ·  OR-Tools CP-SAT',
         size=10, color=MUTED, align=PP_ALIGN.CENTER)

add_rect(s, 4.0, 3.65, 3.0, 1.1, WHITE)
add_rect(s, 4.0, 3.65, 3.0, 0.05, BROWN)
add_text(s, 4.1, 3.85, 2.8, 0.35, 'Storage Layer',
         size=12, bold=True, color=CHARCOAL, font=HEADING_FONT, align=PP_ALIGN.CENTER)
add_text(s, 4.1, 4.23, 2.8, 0.4, 'PostgreSQL  ·  Redis',
         size=10, color=MUTED, align=PP_ALIGN.CENTER)

add_text(s, 3.75, 2.5, 0.3, 0.4, '→', size=20, color=GREEN, align=PP_ALIGN.CENTER)
add_text(s, 7.05, 2.5, 0.3, 0.4, '→', size=20, color=GREEN, align=PP_ALIGN.CENTER)
add_text(s, 5.35, 3.3, 0.3, 0.4, '↓', size=20, color=BROWN, align=PP_ALIGN.CENTER)

add_text(s, 0.7, 5.1, 12, 0.4, 'Frozen Components',
         size=14, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 5.55, 12, 1.4, [
    'The XGBoost classifier and OR-Tools solver are identical across all experiments.',
    'Only the scheduling strategy varies — this isolates the research variable.',
], size=12, spacing=6)

# ============================================================
# SLIDE 6 — AI Matching Pipeline
# ============================================================
s = content_slide('AI Matching Pipeline',
                  'Three stages from job request to worker selection')

steps = [
    ('01', 'XGBoost Suitability Classifier', GREEN,
     'Predicts a worker-job suitability score (0–1) from six attributes: skill match, distance, wage fit, experience, rating, and transport availability.'),
    ('02', 'OR-Tools CP-SAT Optimizer', BROWN,
     'Solves a constrained optimization: select exactly N workers, within budget, maximizing aggregate suitability across the group.'),
    ('03', 'Adaptive Dispatcher', GREEN,
     'Routes each incoming job to the least-loaded worker node using the weighted score: 0.5 × CPU + 0.3 × queue + 0.2 × latency.'),
]

top = 1.85
for num, title, color, desc in steps:
    add_rect(s, 0.7, top, 12, 1.35, WHITE)
    add_rect(s, 0.7, top, 0.06, 1.35, color)
    add_text(s, 1.05, top + 0.15, 0.8, 0.5, num,
             size=24, bold=True, color=color, font=HEADING_FONT)
    add_text(s, 2.0, top + 0.18, 10.4, 0.4, title,
             size=14, bold=True, color=CHARCOAL, font=HEADING_FONT)
    add_text(s, 2.0, top + 0.65, 10.4, 0.7, desc,
             size=11.5, color=MUTED)
    top += 1.5

# ============================================================
# SLIDE 7 — Three Scheduling Strategies
# ============================================================
s = content_slide('Three Scheduling Strategies',
                  'Identical AI matcher — only the distribution strategy differs')

strategies = [
    ('Centralized', '1 Node', GREEN,
     'No distribution. A single worker node processes all incoming jobs. Serves as the performance baseline.'),
    ('Static Distributed', '3 Nodes', BROWN,
     'Hash-based Kafka partitioning (job_id mod 3). Jobs are pinned to partitions; load balancing is fixed.'),
    ('Adaptive Distributed', '3 Nodes', GREEN,
     'Proposed approach. A dispatcher routes each job to the least-loaded node using a weighted score.'),
]

left = 0.7
for name, nodes, color, desc in strategies:
    add_rect(s, left, 1.9, 3.95, 4.4, WHITE)
    add_rect(s, left, 1.9, 3.95, 0.07, color)
    add_text(s, left + 0.3, 2.15, 3.4, 0.5, name,
             size=15, bold=True, color=color, font=HEADING_FONT)
    add_text(s, left + 0.3, 2.72, 3.4, 0.35, nodes,
             size=11, bold=True, color=MUTED)
    add_rect(s, left + 0.3, 3.15, 0.7, 0.03, color)
    add_text(s, left + 0.3, 3.35, 3.4, 2.7, desc,
             size=11.5, color=TEXT)
    left += 4.1

add_text(s, 0.7, 6.55, 12, 0.5,
         'The adaptive strategy is the research contribution — it is the only variable that changes.',
         size=12, bold=True, color=GREEN, align=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 8 — Experimental Setup
# ============================================================
s = content_slide('Experimental Setup',
                  'A controlled benchmark to isolate scheduling effects')

add_text(s, 0.7, 1.85, 5.8, 0.4, 'Inputs & Configuration',
         size=14, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 2.35, 5.8, 4.0, [
    '1,000 synthetic workers with realistic rural attributes',
    '500 job records with skill, budget, and duration',
    'Request rates: 100 / 500 / 1000 / 5000 per second',
    'Node counts: 1, 3, and 5 processing nodes',
    'Frozen XGBoost model — same model in every run',
    'Five repetitions per configuration for significance',
], size=12, spacing=7)

add_text(s, 6.85, 1.85, 5.8, 0.4, 'Metrics Measured',
         size=14, bold=True, color=BROWN, font=HEADING_FONT)
add_bullets(s, 6.85, 2.35, 5.8, 4.0, [
    'End-to-end latency (average and maximum)',
    'Throughput (jobs per second)',
    'CPU and memory utilization per node',
    'Load imbalance across nodes',
    'Matching success rate and skill-match score',
    'Constraint violations and unmatched jobs',
], size=12, spacing=7)

# ============================================================
# SLIDE 9 — Results
# ============================================================
s = content_slide('Results — Measured Performance',
                  'Aggregated from real distributed Kafka experiments')

add_rect(s, 0.7, 1.85, 12, 0.5, GREEN_LIGHT)
add_text(s, 0.9, 1.95, 3.5, 0.35, 'METRIC',
         size=11, bold=True, color=GREEN_DARK)
add_text(s, 4.5, 1.95, 2.5, 0.35, 'CENTRALIZED',
         size=11, bold=True, color=GREEN_DARK, align=PP_ALIGN.CENTER)
add_text(s, 7.2, 1.95, 2.5, 0.35, 'STATIC',
         size=11, bold=True, color=GREEN_DARK, align=PP_ALIGN.CENTER)
add_text(s, 9.9, 1.95, 2.5, 0.35, 'ADAPTIVE',
         size=11, bold=True, color=GREEN_DARK, align=PP_ALIGN.CENTER)

rows = [
    ('Nodes', '1', '3', '3'),
    ('Average Latency', '21.10 ms', '23.71 ms', '24.65 ms'),
    ('Maximum Latency', '~40 ms', '123.18 ms', '119.13 ms'),
    ('Average CPU', '100%', '501%', '411%'),
    ('Load Imbalance', '—', '3.2%', '2.1%'),
    ('Jobs Processed', '1,550', '6,250', '1,874'),
]

top = 2.5
for i, (metric, c1, c2, c3) in enumerate(rows):
    if i % 2 == 0:
        add_rect(s, 0.7, top, 12, 0.55, WHITE)
    add_text(s, 0.9, top + 0.12, 3.5, 0.35, metric,
             size=12, bold=True, color=CHARCOAL)
    add_text(s, 4.5, top + 0.12, 2.5, 0.35, c1,
             size=12, color=MUTED, font=MONO_FONT, align=PP_ALIGN.CENTER)
    add_text(s, 7.2, top + 0.12, 2.5, 0.35, c2,
             size=12, color=MUTED, font=MONO_FONT, align=PP_ALIGN.CENTER)
    add_text(s, 9.9, top + 0.12, 2.5, 0.35, c3,
             size=12, bold=True, color=GREEN, font=MONO_FONT, align=PP_ALIGN.CENTER)
    top += 0.55

add_text(s, 0.7, 6.2, 12, 0.6,
         'Adaptive wins on efficiency and load balance. Static is marginally faster on average latency '
         'but degrades sharply at the tail.',
         size=11, italic=True, color=MUTED)

# ============================================================
# SLIDE 10 — Research Contribution
# ============================================================
s = content_slide('Research Contribution',
                  'What is novel in this work')

contributions = [
    ('01', 'Novel Adaptive Scheduling',
     'A weighted metric-driven dispatcher (CPU + queue + latency) applied to AI-based workforce matching.'),
    ('02', 'Measurable Performance Gains',
     '~18% lower CPU usage and 2.1% load imbalance versus 3.2% for static distribution.'),
    ('03', 'Clean Three-Way Benchmark',
     'A frozen AI matcher isolates scheduling as the single experimental variable.'),
    ('04', 'Open-Source Prototype',
     'Full source code, FastAPI backend, React dashboard, and Docker deployment available on GitHub.'),
]

top = 1.85
for num, title, desc in contributions:
    add_rect(s, 0.7, top, 12, 1.05, WHITE)
    add_rect(s, 0.7, top, 0.05, 1.05, GREEN)
    add_text(s, 1.0, top + 0.15, 0.7, 0.4, num,
             size=18, bold=True, color=GREEN, font=HEADING_FONT)
    add_text(s, 1.85, top + 0.1, 10.5, 0.35, title,
             size=13, bold=True, color=CHARCOAL, font=HEADING_FONT)
    add_text(s, 1.85, top + 0.5, 10.5, 0.5, desc,
             size=11, color=MUTED)
    top += 1.2

# ============================================================
# SLIDE 11 — Live Web Application
# ============================================================
s = content_slide('Live Web Application',
                  'An interactive demonstration of the research')

tabs = [
    ('Match Workers', 'Submit a job request and receive AI-matched workers in ~25 ms.'),
    ('Live Simulation', 'Run Centralized, Static, and Adaptive side-by-side in real time.'),
    ('Research Results', 'View aggregated metrics from the real distributed experiments.'),
    ('Architecture', 'Explore the design of the three scheduling strategies.'),
    ('How It Works', 'End-to-end walkthrough with real-world rural use cases.'),
]

top = 1.85
for name, desc in tabs:
    add_rect(s, 0.7, top, 12, 0.72, WHITE)
    add_rect(s, 0.7, top, 0.05, 0.72, GREEN)
    add_text(s, 1.05, top + 0.12, 3.2, 0.4, name,
             size=12.5, bold=True, color=GREEN, font=HEADING_FONT)
    add_text(s, 4.4, top + 0.15, 8.1, 0.5, desc,
             size=11.5, color=MUTED)
    top += 0.82

add_rect(s, 0.7, 6.15, 12, 0.6, GREEN_LIGHT)
add_text(s, 0.9, 6.28, 11.6, 0.4,
         'Live App:    kaamsetu-frontend.onrender.com        |        API Docs:    kaamsetu-api.onrender.com/docs',
         size=11.5, bold=True, color=GREEN_DARK, font=MONO_FONT, align=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 12 — Conclusion & Future Work
# ============================================================
s = content_slide('Conclusion & Future Work',
                  'Summary of findings and directions ahead')

add_text(s, 0.7, 1.85, 12, 0.4, 'Conclusion',
         size=15, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 2.35, 12, 2.0, [
    'Adaptive distributed scheduling measurably improves efficiency and load balance over static distribution.',
    'The AI matching pipeline (XGBoost + OR-Tools) delivers sub-25 ms responses at scale.',
    'Real-world rural workforce matching becomes practical with this architecture.',
], size=12.5, spacing=8)

add_text(s, 0.7, 4.55, 12, 0.4, 'Future Work',
         size=15, bold=True, color=BROWN, font=HEADING_FONT)
add_bullets(s, 0.7, 5.05, 12, 1.8, [
    'Deploy on AWS for real cloud-scale benchmarking across regions.',
    'Integrate Apache Spark for larger streaming workloads.',
    'Extend to multi-region scheduling and A/B model deployment.',
], size=12.5, spacing=8)

# ============================================================
# SLIDE 13 — Key Takeaways
# ============================================================
s = content_slide('Key Takeaways',
                  'Three points to remember')

takeaways = [
    ('Adaptive beats static', 'On CPU efficiency (18% lower) and load balance (2.1% vs 3.2%).'),
    ('Frozen AI, variable scheduling', 'A clean experiment isolates the contribution of scheduling.'),
    ('Practical and deployable', 'A working web app demonstrates real-time matching in the browser.'),
]

top = 2.0
for title, desc in takeaways:
    add_rect(s, 1.5, top, 10.3, 1.35, WHITE)
    add_rect(s, 1.5, top, 0.06, 1.35, GREEN)
    add_text(s, 1.9, top + 0.2, 9.6, 0.5, title,
             size=18, bold=True, color=GREEN_DARK, font=HEADING_FONT)
    add_text(s, 1.9, top + 0.75, 9.6, 0.5, desc,
             size=12.5, color=MUTED)
    top += 1.55

# ============================================================
# SLIDE 14 — Thank You
# ============================================================
s = add_slide()
set_bg(s, PAPER)
add_rect(s, 0, 0, 0.35, 7.5, GREEN)
add_rect(s, 0.35, 0, 0.06, 7.5, GREEN_MID)

add_text(s, 1.1, 2.4, 11, 1.0, 'Thank You',
         size=54, bold=True, color=CHARCOAL, font=HEADING_FONT)
add_rect(s, 1.1, 3.5, 2.8, 0.04, GREEN)
add_text(s, 1.1, 3.85, 11, 0.5, 'Questions & Discussion',
         size=18, color=MUTED, italic=True)

add_text(s, 1.1, 5.3, 11, 0.4, STUDENT_NAME,
         size=16, bold=True, color=CHARCOAL, font=HEADING_FONT)
add_text(s, 1.1, 5.7, 11, 0.4, f'{DEGREE} Research Project · {YEAR}',
         size=12, color=MUTED)
add_text(s, 1.1, 6.4, 11, 0.4,
         'KaamSetu AI  ·  Adaptive Distributed Rural Workforce Matching',
         size=10, color=LIGHT, font=MONO_FONT)

# ============================================================
# Save
# ============================================================
prs.save('KaamSetu_AI_Presentation.pptx')
print('=' * 60)
print('Presentation created successfully')
print('=' * 60)
print(f'File:      KaamSetu_AI_Presentation.pptx')
print(f'Slides:    {len(prs.slides)}')
print(f'Author:    {STUDENT_NAME}')
print(f'Headings:  {HEADING_FONT}')
print(f'Body:      {BODY_FONT}')
print(f'Monospace: {MONO_FONT}')
print('=' * 60)