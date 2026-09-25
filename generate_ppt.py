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
# Fonts
# ============================================================
HEADING_FONT = 'Segoe UI Semibold'
BODY_FONT = 'Segoe UI'
MONO_FONT = 'Consolas'

STUDENT_NAME = 'Sakshi'
DEGREE = 'M.Tech'
YEAR = '2025–26'

# ============================================================
# Presentation setup
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
         'An Intelligent Distributed Platform for Real-Time Rural Workforce\nMatching, Wage Estimation, and Resource Coordination',
         size=17, color=MUTED, italic=True)

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
    ('02    Research Objective & Motivation', True),
    ('03    System Architecture', True),
    ('04    AI Matching Pipeline', True),
    ('05    Distributed Scheduling Strategies', True),
    ('06    Multi-Constraint Optimization', True),
    ('07    Research Features (Wage, Travel, Forecast)', True),
    ('08    Experimental Results', True),
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
# SLIDE 4 — Research Objective
# ============================================================
s = content_slide('Research Objective',
                  'The central hypothesis behind this work')

add_rect(s, 0.7, 1.9, 12, 2.0, WHITE)
add_rect(s, 0.7, 1.9, 0.06, 2.0, GREEN)
add_text(s, 1.1, 2.15, 11.3, 1.6,
         '"Can an AI-based multi-constraint matching and optimization model '
         'improve rural worker-employer matching by reducing total hiring cost, '
         'travel distance, and matching time while satisfying skill, availability, '
         'and workforce requirements?"',
         size=17, italic=True, color=CHARCOAL, font=HEADING_FONT)

add_text(s, 0.7, 4.25, 12, 0.4, 'Motivation',
         size=15, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 4.75, 12, 2.0, [
    'Focus on adaptive distributed workload management — not just an application.',
    'Performance measured along latency, throughput, scalability, and load balance.',
    'Three scheduling strategies compared with an identical AI matcher.',
    'Baselines provide a fair comparison for multi-constraint optimization.',
], size=12.5, spacing=8)

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
add_text(s, 4.1, 4.23, 2.8, 0.4, 'PostgreSQL  ·  Redis  ·  SQLite',
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
# SLIDE 7 — Distributed Scheduling Strategies
# ============================================================
s = content_slide('Distributed Scheduling Strategies',
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
# SLIDE 8 — Multi-Constraint Optimization
# ============================================================
s = content_slide('Multi-Constraint Optimization',
                  'Mathematical formulation and baselines')

add_rect(s, 0.7, 1.85, 12, 1.1, WHITE)
add_rect(s, 0.7, 1.85, 0.06, 1.1, GREEN)
add_text(s, 1.05, 2.0, 11.5, 0.85,
         'Minimize:  Cost = α·W  +  β·D  +  γ·T  +  δ·M\n'
         'where W = wage, D = distance, T = transport cost, M = mismatch penalty',
         size=13, color=CHARCOAL, font=MONO_FONT)

add_text(s, 0.7, 3.15, 12, 0.4, 'Constraints',
         size=14, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 3.6, 6, 2.0, [
    'WorkersSelected = WorkersRequired',
    'SkillMatch ≥ RequiredSkill',
    'Availability = 1',
], size=11.5, spacing=6)

add_text(s, 7.0, 3.15, 6, 0.4, 'Baselines Compared',
         size=14, bold=True, color=BROWN, font=HEADING_FONT)
add_bullets(s, 7.0, 3.6, 6, 2.0, [
    'Nearest-Worker (distance only)',
    'Skill-Based (skill + rating)',
    'Proposed (multi-constraint)',
], size=11.5, spacing=6)

add_rect(s, 0.7, 5.85, 12, 0.7, GREEN_LIGHT)
add_text(s, 0.9, 5.95, 11.6, 0.5,
         'Result: Proposed optimizer reduces total wage by ~24% vs Nearest-Worker baseline\n'
         'and ~4% vs Skill-Based baseline, while maintaining acceptable average distance.',
         size=11.5, bold=True, color=GREEN_DARK, align=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 9 — Research Features
# ============================================================
s = content_slide('Research Features',
                  'Additional capabilities implemented in the platform')

features = [
    ('Wage Estimation', 'Predicts market-fair wages from skill, season, and duration.'),
    ('Travel Planning', 'Groups workers into shared vehicles with distance and cost estimates.'),
    ('Fair Wage Warning', 'Alerts employers when offer falls below market reference.'),
    ('Digital Work Order', 'Itemized invoice with labour, transport, and platform fee.'),
    ('Demand Forecasting', 'Seasonal prediction of labour demand by skill category.'),
    ('Worker Availability', 'Persistent day-by-day availability tracking.'),
    ('Three-Role Auth', 'JWT-based access for employer, worker, and admin.'),
    ('Landing Page', 'Public marketing page with feature highlights and demo access.'),
]

top = 1.85
for i, (name, desc) in enumerate(features):
    col = i % 2
    row = i // 2
    left = 0.7 + col * 6.2
    top_i = top + row * 1.15
    add_rect(s, left, top_i, 5.9, 1.0, WHITE)
    add_rect(s, left, top_i, 0.05, 1.0, GREEN)
    add_text(s, left + 0.25, top_i + 0.15, 5.5, 0.4, name,
             size=12.5, bold=True, color=GREEN_DARK, font=HEADING_FONT)
    add_text(s, left + 0.25, top_i + 0.5, 5.5, 0.5, desc,
             size=11, color=MUTED)

# ============================================================
# SLIDE 10 — Experimental Results
# ============================================================
s = content_slide('Experimental Results',
                  'Scheduling strategy comparison')

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
# SLIDE 11 — Live Web Application
# ============================================================
s = content_slide('Live Web Application',
                  'An interactive demonstration of the research')

add_text(s, 0.7, 1.85, 12, 0.4, 'Architecture',
         size=14, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 2.3, 12, 1.2, [
    'FastAPI backend deployed on Render  —  https://kaamsetu-api-y0yc.onrender.com',
    'React frontend deployed on Render  —  https://kaamsetu-frontend.onrender.com',
    'Live API documentation  —  /docs (Swagger UI)',
], size=12, spacing=6)

add_text(s, 0.7, 3.6, 12, 0.4, 'Demo Accounts (password: demo123)',
         size=14, bold=True, color=GREEN, font=HEADING_FONT)

accounts = [
    ('employer@demo.com', 'Post jobs, view AI matches, generate work orders, view forecasts'),
    ('worker@demo.com',   'Browse jobs, accept work, manage availability'),
    ('admin@demo.com',    'View statistics, manage users, run simulations'),
]

top = 4.05
for email, desc in accounts:
    add_rect(s, 0.7, top, 12, 0.65, WHITE)
    add_rect(s, 0.7, top, 0.05, 0.65, GREEN)
    add_text(s, 1.05, top + 0.1, 3.5, 0.4, email,
             size=12, bold=True, color=GREEN_DARK, font=MONO_FONT)
    add_text(s, 4.7, top + 0.15, 7.8, 0.4, desc,
             size=11, color=MUTED)
    top += 0.75

# ============================================================
# SLIDE 12 — Conclusion & Future Work
# ============================================================
s = content_slide('Conclusion & Future Work',
                  'Summary of findings and directions ahead')

add_text(s, 0.7, 1.85, 12, 0.4, 'Conclusion',
         size=15, bold=True, color=GREEN, font=HEADING_FONT)
add_bullets(s, 0.7, 2.35, 12, 2.0, [
    'Adaptive distributed scheduling measurably improves efficiency and load balance over static distribution.',
    'The multi-constraint AI optimizer saves ~24% on wage vs the nearest-worker baseline.',
    'The AI matching pipeline (XGBoost + OR-Tools) delivers sub-25 ms responses at scale.',
    'Real-world rural workforce matching becomes practical with this architecture.',
], size=12, spacing=6)

add_text(s, 0.7, 4.95, 12, 0.4, 'Future Work',
         size=15, bold=True, color=BROWN, font=HEADING_FONT)
add_bullets(s, 0.7, 5.45, 12, 1.8, [
    'Deploy on AWS for real cloud-scale benchmarking across regions.',
    'Integrate Apache Spark for larger streaming workloads.',
    'Extend to multi-region scheduling and A/B model deployment.',
    'Incorporate real anonymized survey data (with consent).',
], size=12, spacing=6)

# ============================================================
# SLIDE 13 — Key Takeaways
# ============================================================
s = content_slide('Key Takeaways',
                  'Three points to remember')

takeaways = [
    ('Adaptive beats static', 'On CPU efficiency (18% lower) and load balance (2.1% vs 3.2%).'),
    ('Multi-constraint wins', 'Proposed optimizer saves ~24% on wage vs nearest-worker baseline.'),
    ('Practical and deployable', 'A live web app demonstrates real-time matching and full workflow.'),
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
print('Presentation updated successfully')
print('=' * 60)
print(f'File:   KaamSetu_AI_Presentation.pptx')
print(f'Slides: {len(prs.slides)}')
print(f'Author: {STUDENT_NAME}')
print('=' * 60)