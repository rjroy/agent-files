"""Render a self-contained, post-review visualization of saved results."""

from html import escape
import json


STYLES = """
:root {
  color-scheme: light;
  --paper: #f5f3eb;
  --sheet: #fffef9;
  --ink: #202e29;
  --muted: #52625a;
  --rule: #d4d9cd;
  --axis: #9daaa0;
  --human: #286450;
  --win: #3d5f91;
  --loss: #9d4c37;
  --display: "Iowan Old Style", "Palatino Linotype", "P052", Palatino, Georgia, serif;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font: .9375rem/1.45 "Source Sans 3", "Adwaita Sans", "Segoe UI", sans-serif;
}
main { max-width: 74rem; margin-inline: auto; padding: 1.5rem clamp(1rem, 3vw, 2.5rem) 3rem; }
header { border-block-start: 3px solid var(--ink); padding-block: 1rem .25rem; }
h1, h2, h3, p { margin: 0; }
h1, h2 { font-family: var(--display); font-weight: 600; line-height: 1.08; }
h1 { font-size: clamp(2.125rem, 5vw, 3rem); letter-spacing: -.035em; }
h2 { font-size: 1.625rem; letter-spacing: -.02em; }
.report-header { display: flex; flex-wrap: wrap; align-items: baseline; gap: .5rem 1rem; }
.privacy {
  font-size: .75rem; font-weight: 700; color: var(--human);
  border: 1px solid var(--axis); border-radius: 1rem; padding: .125rem .5rem;
}
.header-note, .section-note { color: var(--muted); max-width: 75ch; }
.header-note { margin-top: .375rem; font-size: .875rem; }
nav { display: flex; flex-wrap: wrap; gap: .25rem 1rem; margin-top: .625rem; font-size: .8125rem; }
a { color: var(--human); text-underline-offset: .2em; }
a:hover { color: var(--ink); }
:focus-visible { outline: 2px solid var(--human); outline-offset: 3px; }
::selection { background: #cee6da; color: var(--ink); }
section { margin-block-start: 1.75rem; scroll-margin-block-start: 1rem; }
.section-note { margin-block: .375rem .75rem; font-size: .875rem; }
.chart-list {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 18rem), 1fr));
  gap: .75rem;
}
.chart {
  min-width: 0; background: var(--sheet); border: 1px solid var(--rule);
  border-radius: .75rem; padding: .75rem 1rem;
  --name-width: 41%; --value-width: 1.625rem; --plot-gap: .5rem;
}
.chart h3 { font-size: .9375rem; line-height: 1.25; overflow-wrap: anywhere; }
.case-label { display: block; margin-bottom: .1875rem; color: var(--muted); font-size: .75rem; }
.plot-row, .axis-labels {
  display: grid; grid-template-columns: var(--name-width) minmax(0, 1fr) var(--value-width);
  column-gap: var(--plot-gap); align-items: center; font-variant-numeric: tabular-nums;
}
.axis-labels { margin-top: .5rem; color: var(--muted); font-size: .6875rem; }
.axis-ticks { grid-column: 2; display: flex; justify-content: space-between; position: relative; }
.axis-mid { position: absolute; left: 50%; transform: translateX(-50%); }
.plot-rows { position: relative; padding: 0; margin: .1875rem 0 0; list-style: none; }
.plot-rows::before {
  content: ""; position: absolute; inset-block: 0; pointer-events: none;
  left: calc(var(--name-width) + var(--plot-gap));
  right: calc(var(--value-width) + var(--plot-gap));
  border-inline: 1px solid var(--rule);
  background: linear-gradient(var(--axis), var(--axis)) left / 1px 100% no-repeat;
}
.preference .plot-rows::before { background-position: center; }
.plot-row { min-height: 1.5rem; padding-block: .125rem; font-size: .8125rem; }
.preference .plot-row { min-height: 2.25rem; }
.model { display: block; font-weight: 600; overflow-wrap: anywhere; }
.mark { position: relative; display: block; width: 100%; overflow: visible; }
.mark-grade { fill: var(--human); }
.mark-ahead { fill: var(--win); }
.mark-behind { fill: var(--loss); }
.mark-even { stroke: var(--ink); stroke-width: 3; }
.value { text-align: right; color: var(--muted); font-size: .75rem; }
.counts { display: block; color: var(--muted); font-size: .6875rem; line-height: 1.3; }
.counts span { white-space: nowrap; }
.counts span + span { margin-inline-start: .125rem; }
.sr-only {
  position: absolute; inline-size: 1px; block-size: 1px; padding: 0;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap;
}
.scroll {
  overflow-x: auto; scrollbar-color: var(--axis) var(--sheet);
  background: var(--sheet); border: 1px solid var(--rule); border-radius: .75rem;
}
table { border-collapse: collapse; width: 100%; font-size: .8125rem; }
th, td {
  text-align: left; vertical-align: top; padding: .5rem .75rem;
  min-width: 7.5rem; border-bottom: 1px solid var(--rule); overflow-wrap: anywhere;
}
thead { background: #eeefe7; }
tbody tr:last-child > * { border-bottom: 0; }
.outcome { display: inline-block; border-radius: .25rem; padding-inline: .25rem; }
.good { background: #e2eee6; color: #235a3d; }
.bad { background: #f5e7df; color: #793b2b; }
.neutral { background: #eff0e9; color: #47564e; }
@media (forced-colors: active) {
  .mark rect { fill: CanvasText; }
  .mark-even { stroke: CanvasText; }
}
"""


def common_model_prefix(models):
    """Shorten labels only if every model has the same provider prefix."""
    if models:
        provider, slash, _ = models[0].partition("/")
        prefix = provider + slash
        if provider and slash and all(m.startswith(prefix) and m != prefix for m in models):
            return prefix
    return ""


def plot_row(model, prefix, mark, value, counts=""):
    name = escape(model[len(prefix):])
    full_name = escape(model, quote=True)
    if prefix:
        name = (f'<span class="sr-only">{full_name}</span>'
                f'<span aria-hidden="true">{name}</span>')
    svg = f'<svg class="mark" height="12" aria-hidden="true">{mark}</svg>'
    return (
        f'<li class="plot-row" data-model="{full_name}">'
        f'<div><span class="model" title="{full_name}">{name}</span>{counts}</div>'
        f'{svg}<span class="value">{value}</span></li>'
    )


def bar(kind, start, width):
    return f'<rect class="mark-{kind}" x="{start:.6g}%" width="{width:.6g}%" height="12"/>'


def missing_value(label):
    return f'<span aria-hidden="true">–</span><span class="sr-only">{label}</span>'


def signed(value):
    return f"−{-value}" if value < 0 else f"+{value}" if value > 0 else "0"


def plot(case_id, title, kind, ticks, rows, rubric_index=None):
    key = "" if rubric_index is None else f' data-rubric="{rubric_index}"'
    scope = f'<span class="case-label">{escape(case_id)}</span>' if rubric_index is not None else ""
    middle = f'<span class="axis-mid">{ticks[1]}</span>' if len(ticks) == 3 else ""
    return (
        f'<article class="chart {kind}" data-case="{escape(case_id, quote=True)}"{key}>'
        f'<h3>{scope}{escape(title)}</h3>'
        f'<div class="axis-labels" aria-hidden="true"><div class="axis-ticks">'
        f'<span>{ticks[0]}</span>{middle}<span>{ticks[-1]}</span></div></div>'
        f'<ul class="plot-rows" role="list">{"".join(rows)}</ul></article>'
    )


def grade_plot(case, rubric_index, rubric, models, prefix, grades):
    rows = []
    for model in models:
        grade = grades.get(json.dumps([case["id"], model, rubric_index]))
        if grade is None:
            mark, value = "", missing_value("Missing grade")
        else:
            if type(grade) is not int or not 1 <= grade <= 5:
                raise ValueError(f"invalid grade for {case['id']}, {model}, rubric {rubric_index}")
            mark, value = bar("grade", 0, 20 * grade), str(grade)
        rows.append(plot_row(model, prefix, mark, value))
    return plot(case["id"], rubric["label"], "human", ("0", "5"), rows, rubric_index)


def comparison_counts(entry, legacy):
    fields = [("W", "wins"), ("L", "losses"), ("T", "ties")]
    if not legacy:
        fields.append(("D", "disagreements"))
    visible = " ".join(
        f'<span>{entry[field]} {initial}</span>' for initial, field in fields
    )
    spoken = "; ".join(f'{field.capitalize()}: {entry[field]}' for _, field in fields)
    return (
        f'<span class="counts" aria-hidden="true">{visible}</span>'
        f'<span class="sr-only">{spoken}</span>'
    )


def preference_plot(case_id, models, prefix, stats, limit, legacy):
    rows = []
    for model in models:
        entry = stats.get(model)
        if entry is None:
            rows.append(plot_row(model, prefix, "", missing_value("Not compared")))
            continue
        score = entry["score"]
        if score == 0:
            mark = '<line class="mark-even" x1="50%" x2="50%" y1="1" y2="11"/>'
        else:
            width = 50 * abs(score) / limit
            mark = bar("ahead", 50, width) if score > 0 else bar("behind", 50 - width, width)
        rows.append(plot_row(model, prefix, mark, signed(score), comparison_counts(entry, legacy)))
    return plot(case_id, case_id, "preference", (signed(-limit), "0", signed(limit)), rows)


def preference_section(record, cases, models, prefix):
    standings = record["standings"]
    legacy = record.get("version", 1) == 1
    saved = [(case["id"], standings.get(case["id"], {})) for case in cases]
    # All plots share the largest possible net score among the plotted rows.
    limit = max((stats[model]["games"] for _, stats in saved for model in models
                 if model in stats), default=0)
    charts = []
    if limit:
        charts = [preference_plot(case_id, models, prefix, stats, limit, legacy)
                  for case_id, stats in saved if any(model in stats for model in models)]
    content = (f'<div class="chart-list">{"".join(charts)}</div>' if charts
               else '<p class="section-note">No pairwise comparisons were saved.</p>')
    grader = escape(record["grader"]["model"])
    legend = ("T counts ties and order disagreements in this older report." if legacy else
              "T counts ties; D counts disagreements when the responses switch sides.")
    return (
        '<section id="preferences"><h2>Pairwise preferences</h2>'
        f'<p class="section-note">Local grader: <strong>{grader}</strong>. Bars show wins '
        f'minus losses, not grades. W and L count wins and losses. {legend}</p>{content}</section>'
    )


def outcome_class(value):
    return {"pass": "good", "ok": "good", "fail": "bad", "error": "bad"}.get(
        value, "neutral"
    )


def outcome_table(state):
    headings = "".join(f'<th scope="col">{escape(case["id"])}</th>'
                       for case in state["cases"])
    rows = []
    for model in state["models"]:
        cells = []
        for case in state["cases"]:
            run = state["runs"].get(case["id"], {}).get(model, {})
            status = run.get("status", "not run")
            check = run.get("check", "not run")
            cells.append(
                '<td>'
                f'<div>Run: <span class="outcome {outcome_class(status)}">'
                f'{escape(status)}</span></div>'
                f'<div>Check: <span class="outcome {outcome_class(check)}">'
                f'{escape(check)}</span></div></td>'
            )
        rows.append(f'<tr><th scope="row">{escape(model)}</th>{"".join(cells)}</tr>')
    return (f'<div class="scroll" role="region" aria-labelledby="outcome-heading" tabindex="0">'
            f'<table><thead><tr><th scope="col">Model</th>{headings}'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def render_graphs(state):
    models, cases = state["models"], state["cases"]
    prefix = common_model_prefix(models)
    charts = [grade_plot(case, index, rubric, models, prefix, state["grades"])
              for case in cases for index, rubric in enumerate(case["rubrics"])]
    human = (f'<div class="chart-list">{"".join(charts)}</div>' if charts
             else '<p class="section-note">These cases have checks but no human rubrics.</p>')
    record = state.get("auto_grades")
    preferences = preference_section(record, cases, models, prefix) if record else ""
    preference_link = '<a href="#preferences">Pairwise preferences</a>' if preferences else ""
    demo = ('<p class="header-note"><strong>Demo rehearsal:</strong> synthetic results, '
            'not model performance.</p>' if state.get("demo") else "")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Benchmark graphs</title>
<style>{STYLES}</style></head><body><main>
<header>
  <div class="report-header"><h1>Benchmark graphs</h1><span class="privacy">Private report</span></div>
  <p class="header-note">Contains model identities and grades. Share only with authorized readers.</p>
  {demo}
  <nav aria-label="Report sections">{preference_link}<a href="#outcomes">Run and check outcomes</a></nav>
</header>
<section id="human"><h2>Human rubric grades</h2>
  <p class="section-note">Grades run from 1 to 5; bars start at zero. A dash means no grade was saved.</p>
  {human}
</section>
{preferences}
<section id="outcomes"><h2 id="outcome-heading">Run and check outcomes</h2>
  <p class="section-note">Checks are independent of runs. Not run and not configured are not failures.</p>
  {outcome_table(state)}
</section>
</main></body></html>
"""
