#!/usr/bin/env python3
"""Fill the LNK Simple Suggestion form (FRM-DCI-001/S/001/rev.00) from a JSON file.

Usage:
    python fill_ss.py data.json [--outdir DIR] [--template PATH] [--check]

The template is edited at XML level so that the logo, in-cell checkboxes,
merged cells and print setup survive untouched (openpyxl would drop them).

Text fields accept two light markups:
    **bold**   -> bold run (e.g. "**Man:** ...", "**Akar masalah:** ...")
    newlines   -> kept as line breaks inside the cell

--check only reports fit warnings and the output file name; nothing is written.
Exit code 0 = ok, 1 = input error. Fit warnings never block the write.
"""
import argparse
import datetime as dt
import html
import json
import math
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, '..', 'assets', 'FRM-DCI-001-SS-rev00-template.xlsx')
SHEET1 = 'xl/worksheets/sheet1.xml'
SHEET2 = 'xl/worksheets/sheet2.xml'

# Big text boxes on sheet SS: cell -> (field name, font size, approx chars per line, max lines).
# Capacities were calibrated against printed real SS forms (9 pt Calibri, A4, scale 82%).
BOXES = {
    'B14': ('kondisi_sebelum', 9, 78, 16),
    'J14': ('kondisi_setelah', 9, 78, 16),
    'B17': ('analisa_penyebab', 9, 78, 25),   # merged B17:H22
    'J17': ('solusi', 9, 78, 16),
    'J22': ('manfaat', 9, 78, 13),            # merged J22:P25, incl. its header line
    'B24': ('biaya', 9, 78, 7),               # merged B24:H25
}
QCDSM = [  # json key, checkbox cell, label written in the description
    ('quality', 'J20', 'QUALITY'),
    ('cost', 'K20', 'COST'),
    ('delivery', 'L20', 'DELIVERY'),
    ('safety', 'M20', 'SAFETY'),
    ('morale', 'P20', 'MORALE'),
]
QCDSM_HEADER = 'Deskripsi masing-masing manfaat/ keuntungan (QCDSM) :'
ANAKONDA_ORDER = ['Man', 'Method', 'Machine', 'Material', 'Environment']
ANAKONDA_FIRST_ROW, ANAKONDA_SLOTS = 5, 5
ANAKONDA_WIDTHS = {'B': 46, 'C': 46, 'D': 24, 'E': 19}  # approx chars per line at 10 pt
BAD_FILENAME = r'[\\/:*?"<>|]'


def fail(msg):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(1)


def esc(t):
    return html.escape(t, quote=False)


def runs(text, size):
    """Turn '**bold**' markup into rich-text runs in the cell's font."""
    rpr = ('<sz val="%s"/><color theme="1"/><rFont val="Calibri"/>'
           '<family val="2"/><scheme val="minor"/>') % size
    out = []
    for p in re.split(r'(\*\*.+?\*\*)', text, flags=re.S):
        if not p:
            continue
        bold = p.startswith('**') and p.endswith('**') and len(p) > 4
        body = p[2:-2] if bold else p.replace('**', '')  # stray markers are dropped
        out.append('<r><rPr>%s%s</rPr><t xml:space="preserve">%s</t></r>'
                   % ('<b/>' if bold else '', rpr, esc(body)))
    return ''.join(out)


def set_text(xml, ref, text, size=None):
    """Write text into an existing empty cell of the template, keeping its style."""
    m = re.search(r'<c r="%s"( s="\d+")?\s*/>' % ref, xml)
    if not m:
        fail('template cell %s not found or not empty' % ref)
    if not text:
        return xml
    if '**' in text and size:
        inner = runs(text, size)
    else:
        inner = '<t xml:space="preserve">%s</t>' % esc(text.replace('**', ''))
    cell = '<c r="%s"%s t="inlineStr"><is>%s</is></c>' % (ref, m.group(1) or '', inner)
    return xml[:m.start()] + cell + xml[m.end():]


def set_bool(xml, ref, value):
    new, n = re.subn(r'(<c r="%s" s="\d+" t="b"><v>)\d(</v></c>)' % ref,
                     r'\g<1>%d\2' % (1 if value else 0), xml)
    if n != 1:
        fail('checkbox cell %s not found' % ref)
    return new


def est_lines(text, cpl):
    plain = (text or '').replace('**', '')
    return sum(max(1, math.ceil(len(line) / cpl)) for line in plain.split('\n'))


def clean(s):
    return re.sub(r'\s+', ' ', re.sub(BAD_FILENAME, '', s or '')).strip(' .')


def output_name(d):
    year = d.get('tahun')
    if not year:
        m = re.search(r'(20\d\d)', d.get('tanggal', ''))
        year = m.group(1) if m else dt.date.today().year
    pic = clean(d['pembuat'][0]['nama'])
    short = clean(d.get('judul_singkat') or d['judul'])
    return 'SS %s - %s - %s.xlsx' % (year, pic, short)


def validate(d):
    for k in ['judul', 'pembuat', 'departemen', 'tanggal', 'kondisi_sebelum', 'kondisi_setelah',
              'analisa_penyebab', 'solusi', 'biaya', 'manfaat']:
        if not d.get(k):
            fail('missing field: ' + k)
    if not 1 <= len(d['pembuat']) <= 2 or not all(p.get('nama') for p in d['pembuat']):
        fail('pembuat must list 1-2 people, each with "nama" (and "nik")')
    unknown = set(d['manfaat']) - {k for k, _, _ in QCDSM}
    if unknown:
        fail('unknown QCDSM keys: %s (use quality/cost/delivery/safety/morale)'
             % ', '.join(sorted(unknown)))
    if not any((v or '').strip() for v in d['manfaat'].values()):
        fail('manfaat needs at least one QCDSM category')
    rows = d.get('anakonda') or []
    if len(rows) > ANAKONDA_SLOTS:
        fail('anakonda has more than 5 rows')
    seen = set()
    for r in rows:
        if r.get('kategori') not in ANAKONDA_ORDER:
            fail('anakonda kategori must be one of ' + ', '.join(ANAKONDA_ORDER))
        if r['kategori'] in seen:
            fail('anakonda kategori repeated: ' + r['kategori'])
        seen.add(r['kategori'])


def build_qcdsm(manfaat):
    lines = [QCDSM_HEADER]
    for key, _, label in QCDSM:
        txt = (manfaat.get(key) or '').strip()
        if txt:
            lines.append('**%s** %s' % (label, txt))
    return '\n'.join(lines)


def fill_sheet1(xml, d, warnings):
    p = d['pembuat']

    def person(x):
        return '%s / %s' % (x['nama'], x['nik']) if x.get('nik') else x['nama']

    xml = set_text(xml, 'E6', d['judul'])
    xml = set_text(xml, 'E8', person(p[0]))
    if len(p) > 1:
        xml = set_text(xml, 'E9', person(p[1]))
    xml = set_text(xml, 'E10', d['departemen'])
    xml = set_text(xml, 'E11', d['tanggal'])
    if len(d['judul']) > 95:
        warnings.append('judul: %d chars, may not fit on one line (aim for <= 95)' % len(d['judul']))

    for ref, (field, size, cpl, cap) in BOXES.items():
        text = build_qcdsm(d['manfaat']) if field == 'manfaat' else d[field].strip()
        xml = set_text(xml, ref, text, size)
        n = est_lines(text, cpl)
        if n > cap:
            warnings.append('%s: ~%d lines, box fits ~%d (shorten by ~%d%%)'
                            % (field, n, cap, math.ceil(100 * (n - cap) / n)))
    for key, cell, _ in QCDSM:
        xml = set_bool(xml, cell, bool((d['manfaat'].get(key) or '').strip()))

    a = d.get('approval') or {}
    xml = set_text(xml, 'N29', p[0]['nama'])          # Dibuat oleh: PIC Improvement (1)
    xml = set_text(xml, 'J29', a.get('supervisor'))   # Diperiksa oleh: Supervisor/Manager (2)
    xml = set_text(xml, 'F29', a.get('dept_head'))    # Disetujui: Manager/ Dept Head (3)
    xml = set_text(xml, 'C29', a.get('dept_ci'))      # Disetujui: Dept. Cont. Improvement (4)
    xml = set_text(xml, 'B29', a.get('no_reg'))
    return xml


def fill_sheet2(xml, d):
    rows = sorted(d.get('anakonda') or [], key=lambda r: ANAKONDA_ORDER.index(r['kategori']))
    xml = set_text(xml, 'B2', d['judul'])
    default_pic = d['pembuat'][0]['nama']
    for i, r in enumerate(rows):
        n = ANAKONDA_FIRST_ROW + i
        vals = {'A': r['kategori'], 'B': r.get('should', ''), 'C': r.get('actual', ''),
                'D': r.get('pic') or default_pic, 'E': r.get('tempat', ''), 'F': r.get('hasil', '')}
        for col, v in vals.items():
            xml = set_text(xml, '%s%d' % (col, n), v)
        lines = max(est_lines(vals[c], w) for c, w in ANAKONDA_WIDTHS.items())
        xml = re.sub(r'(<row r="%d" ht=")[\d.]+(")' % n,
                     r'\g<1>%.1f\2' % max(30, 13.5 * lines + 4), xml)
    # drop unused slots so the printed table ends at the last category
    for n in range(ANAKONDA_FIRST_ROW + len(rows), ANAKONDA_FIRST_ROW + ANAKONDA_SLOTS):
        xml = re.sub(r'<row r="%d"[^>]*>.*?</row>' % n, '', xml, flags=re.S)
    last = ANAKONDA_FIRST_ROW + max(len(rows), 1) - 1
    return xml.replace('<dimension ref="A1:F9"/>', '<dimension ref="A1:F%d"/>' % last)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('data')
    ap.add_argument('--outdir', default='.')
    ap.add_argument('--template', default=DEFAULT_TEMPLATE)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    with open(a.data, encoding='utf-8') as f:
        d = json.load(f)
    validate(d)

    warnings = []
    zin = zipfile.ZipFile(a.template)
    s1 = fill_sheet1(zin.read(SHEET1).decode('utf-8'), d, warnings)
    s2 = fill_sheet2(zin.read(SHEET2).decode('utf-8'), d)
    name = output_name(d)
    for w in warnings:
        print('FIT WARNING: ' + w)
    if a.check:
        print('OUTPUT NAME: ' + name)
        return

    core = zin.read('docProps/core.xml').decode('utf-8')
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    core = re.sub(r'<dc:creator>.*?</dc:creator>',
                  '<dc:creator>%s</dc:creator>' % esc(d['pembuat'][0]['nama']), core)
    core = re.sub(r'(<dcterms:created [^>]*>).*?(</dcterms:created>)', r'\g<1>%s\2' % now, core)
    core = re.sub(r'(<dcterms:modified [^>]*>).*?(</dcterms:modified>)', r'\g<1>%s\2' % now, core)

    os.makedirs(a.outdir, exist_ok=True)
    out = os.path.join(a.outdir, name)
    replaced = {SHEET1: s1, SHEET2: s2, 'docProps/core.xml': core}
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = replaced.get(item.filename)
            zout.writestr(item, data.encode('utf-8') if data is not None else zin.read(item.filename))
    print('WROTE: ' + out)


if __name__ == '__main__':
    main()
