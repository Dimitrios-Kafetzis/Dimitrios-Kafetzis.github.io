#!/usr/bin/env python3
"""Generate the inline SVG figures used by blog posts into _src/figures/*.svg.

Colours come from the page's CSS tokens (var(--fig-1) etc.) with light-theme fallbacks,
so the same SVG reads in light mode, dark mode and in an RSS reader without CSS.
Run:  python3 _src/figures/make_figures.py
"""
import pathlib

OUT = pathlib.Path(__file__).parent

# Tokens with light fallbacks
FG = "var(--fg, #121a2b)"
MUTED = "var(--muted, #5b6579)"
LINE = "var(--line, #d8dee8)"
SURF = "var(--surface, #ffffff)"
SURF2 = "var(--surface-2, #eaeef4)"
C1 = "var(--fig-1, #0f8fa6)"
C2 = "var(--fig-2, #c47a0a)"
C3 = "var(--fig-3, #6250d6)"
S1 = "var(--fig-1-soft, rgba(15,143,166,0.14))"
S2 = "var(--fig-2-soft, rgba(196,122,10,0.16))"
S3 = "var(--fig-3-soft, rgba(98,80,214,0.14))"
FONT = "font-family=\"'IBM Plex Mono', Menlo, Consolas, monospace\""


class Fig:
    def __init__(self, name, w, h, label):
        self.name, self.w, self.h, self.label = name, w, h, label
        self.parts = []
        self.defs = []

    def arrow_def(self, color=FG, key="a"):
        mid = f"{self.name}-arr-{key}"
        self.defs.append(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        return f"url(#{mid})"

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=12, anchor="start", color=FG, weight=None, dy=None):
        w = f' font-weight="{weight}"' if weight else ""
        d = f' dy="{dy}"' if dy else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}"{w}{d}>{s}</text>')

    def rect(self, x, y, w, h, fill=SURF, stroke=FG, sw=1.2, rx=6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def box(self, x, y, w, h, title, sub=None, fill=SURF, stroke=FG, size=12, rx=6, sw=1.2):
        self.rect(x, y, w, h, fill, stroke, sw, rx)
        cy = y + h / 2
        if sub:
            self.text(x + w / 2, cy - 3, title, size, "middle", weight=600)
            self.text(x + w / 2, cy + 13, sub, size - 2, "middle", MUTED)
        else:
            self.text(x + w / 2, cy + 4, title, size, "middle", weight=600)

    def line(self, x1, y1, x2, y2, color=FG, sw=1.4, arrow=None, dash=None, start=None):
        a = f' marker-end="{arrow}"' if arrow else ""
        st = f' marker-start="{start}"' if start else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{a}{st}{d}/>')

    def path(self, d, color=FG, sw=1.4, arrow=None, fill="none", dash=None):
        a = f' marker-end="{arrow}"' if arrow else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{a}{ds}/>')

    def hbar(self, x, y, w, h, color):
        """Horizontal bar growing from x: square at the baseline, 4px rounded data end."""
        r = min(4, w / 2)
        self.add(f'<path d="M{x},{y} h{w - r} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r} a{r},{r} 0 0 1 -{r},{r} h-{w - r} z" fill="{color}"/>')

    def render(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
               f'aria-label="{self.label}" {FONT}>{defs}{"".join(self.parts)}</svg>')
        (OUT / f"{self.name}.svg").write_text(svg, encoding="utf-8")
        print(self.name)


# ----------------------------------------------------------------------------- SynapticOS

def syn_arena():
    f = Fig("syn-arena", 760, 204, "The SynapticOS tensor arena: persistent weights grow from the base, ephemeral activations after them, scratch at the top; the ephemeral pointer is reset every frame")
    a = f.arrow_def()
    x0, y0, w, h = 40, 60, 680, 54
    f.rect(x0, y0, w, h, SURF, FG, 1.2, 4)
    # regions
    pw, ew, fw = 250, 190, 120
    f.add(f'<rect x="{x0}" y="{y0}" width="{pw}" height="{h}" fill="{S1}"/>')
    f.add(f'<rect x="{x0 + pw}" y="{y0}" width="{ew}" height="{h}" fill="{S2}"/>')
    f.add(f'<rect x="{x0 + w - fw}" y="{y0}" width="{fw}" height="{h}" fill="{S3}"/>')
    f.line(x0 + pw, y0, x0 + pw, y0 + h, FG, 1.2)
    f.line(x0 + pw + ew, y0, x0 + pw + ew, y0 + h, FG, 1.2, dash="3 3")
    f.line(x0 + w - fw, y0, x0 + w - fw, y0 + h, FG, 1.2)
    f.text(x0 + pw / 2, y0 + 24, "persistent", 12, "middle", weight=600)
    f.text(x0 + pw / 2, y0 + 40, "weights, lifetime of the model", 10, "middle", MUTED)
    f.text(x0 + pw + ew / 2, y0 + 24, "ephemeral", 12, "middle", weight=600)
    f.text(x0 + pw + ew / 2, y0 + 40, "activations, one frame", 10, "middle", MUTED)
    f.text(x0 + pw + ew + (w - fw - pw - ew) / 2, y0 + 31, "free", 11, "middle", MUTED)
    f.text(x0 + w - fw / 2, y0 + 24, "scratch pool", 12, "middle", weight=600)
    f.text(x0 + w - fw / 2, y0 + 40, "one layer", 10, "middle", MUTED)
    # pointers
    f.text(x0, y0 - 28, "base", 11, "start", MUTED)
    f.line(x0 + 1, y0 - 18, x0 + 1, y0 - 4, MUTED, 1, arrow=a)
    f.text(x0 + pw, y0 - 28, "persistent boundary", 11, "middle", MUTED)
    f.line(x0 + pw, y0 - 18, x0 + pw, y0 - 4, MUTED, 1, arrow=a)
    f.text(x0 + pw + ew, y0 - 28, "ephemeral pointer", 11, "middle", MUTED)
    f.line(x0 + pw + ew, y0 - 18, x0 + pw + ew, y0 - 4, MUTED, 1, arrow=a)
    f.text(x0 + w, y0 - 28, "base + total", 11, "end", MUTED)
    f.line(x0 + w - 1, y0 - 18, x0 + w - 1, y0 - 4, MUTED, 1, arrow=a)
    # reset arrow
    ar = f.arrow_def(C2, "r")
    f.path(f"M{x0 + pw + ew},{y0 + h + 10} v18 H{x0 + pw + 2} v-18", C2, 1.6, arrow=ar)
    f.text(x0 + w, y0 + h + 50, "syn_mem_reset_ephemeral() every frame: O(1), peak returns to zero", 10.5, "end", MUTED)
    f.text(x0, y0 + h + 70, "16-byte aligned, ~154 cycles per allocation, zero fragmentation by construction", 10, "start", MUTED)
    f.render()


def syn_sched():
    f = Fig("syn-sched", 760, 230, "A preemptible NORMAL job yields at a layer boundary to a REALTIME job with a deadline, then resumes bit-exactly")
    a = f.arrow_def()
    x0, xe = 150, 730
    rows = [("REALTIME job", 70), ("NORMAL job", 130)]
    for label, y in rows:
        f.text(x0 - 14, y + 17, label, 12, "end", weight=600)
        f.line(x0, y + 28, xe, y + 28, LINE, 1)
    # time axis
    f.line(x0, 190, xe, 190, FG, 1.2, arrow=a)
    f.text(xe, 208, "time", 11, "end", MUTED)
    # NORMAL layers: L1 L2 (0-240) then gap, L3 L4 (330-570)
    def layer(x, w, y, label, col=S1, stroke=C1):
        f.add(f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="3" fill="{col}" stroke="{stroke}" stroke-width="1.2"/>')
        f.text(x + w / 2, y + 17, label, 11, "middle")
    y = 130
    layer(x0, 110, y, "layer 1"); layer(x0 + 112, 110, y, "layer 2")
    layer(x0 + 400, 86, y, "layer 3"); layer(x0 + 488, 86, y, "layer 4")
    # realtime job arrives and runs 230..395
    yr = 70
    layer(x0 + 230, 182, yr, "realtime job, deadline met", S2, C2)
    # arrival marker
    f.line(x0 + 230, yr - 22, x0 + 230, yr - 4, C2, 1.4, arrow=f.arrow_def(C2, "r"))
    f.text(x0 + 230, yr - 28, "submitted", 10, "middle", MUTED)
    # preemption annotations
    f.line(x0 + 222, y + 13, x0 + 222, y - 10, FG, 1, dash="2 2")
    f.text(x0 + 222, y - 16, "layer boundary: park context, 10 µs", 10, "middle", MUTED)
    f.line(x0 + 400, y + 13, x0 + 400, y - 10, FG, 1, dash="2 2")
    f.text(x0 + 400, y - 16, "resume, bit-exact", 10, "middle", MUTED)
    f.text(x0 + 310, y + 17, "suspended", 10, "middle", MUTED)
    f.text(x0, 208, "dispatch: priority, then earliest deadline, then FIFO", 10, "start", MUTED)
    f.render()


def syn_dualcore():
    f = Fig("syn-dualcore", 760, 284, "CPU0 owns the AI runtime and the NPU; CPU1 reaches inference only through two single-producer single-consumer rings in shared SRAM; the MPU guard protects CPU1's RAM in one direction")
    a = f.arrow_def()
    # CPU0 box
    f.rect(30, 30, 300, 210, SURF, FG, 1.4, 8)
    f.text(45, 54, "CPU0  Cortex-M33 with FPU, DSP, MPU", 12, "start", weight=600)
    f.text(45, 72, "owns the AI runtime", 10, "start", MUTED)
    for i, t in enumerate(["job scheduler", "model store + OTA", "NPU / DSP HAL", "tensor arena"]):
        yy = 88 + i * 36
        f.add(f'<rect x="45" y="{yy}" width="270" height="28" rx="4" fill="{S1}" stroke="{C1}" stroke-width="1"/>')
        f.text(180, yy + 18, t, 11, "middle")
    # CPU1 box
    f.rect(560, 30, 170, 210, SURF, FG, 1.4, 8)
    f.text(575, 54, "CPU1  Cortex-M33", 12, "start", weight=600)
    f.text(575, 72, "no FPU, DSP, MPU or TZ", 10, "start", MUTED)
    f.add(f'<rect x="575" y="88" width="140" height="28" rx="4" fill="{S3}" stroke="{C3}" stroke-width="1"/>')
    f.text(645, 106, "application", 11, "middle")
    f.add(f'<rect x="575" y="124" width="140" height="28" rx="4" fill="{S3}" stroke="{C3}" stroke-width="1"/>')
    f.text(645, 142, "inference client", 11, "middle")
    f.text(645, 180, "64 KB RAM", 10, "middle", MUTED)
    # shared SRAM
    f.rect(360, 60, 170, 150, SURF2, LINE, 1, 6)
    f.text(445, 80, "shared SRAM", 11, "middle", weight=600)
    # rings
    ar = f.arrow_def(FG, "f")
    f.line(330, 112, 560, 112, FG, 1.6, arrow=ar)
    f.text(445, 104, "request ring (SPSC)", 10, "middle", MUTED)
    f.line(560, 150, 330, 150, FG, 1.6, arrow=ar)
    f.text(445, 166, "response ring (SPSC)", 10, "middle", MUTED)
    f.add(f'<rect x="370" y="180" width="150" height="20" rx="3" fill="{S2}" stroke="{C2}" stroke-width="1"/>')
    f.text(445, 194, "tensor slot, zero copy", 10, "middle")
    # MPU guard
    ag = f.arrow_def(C2, "g")
    f.path("M180,240 v14 H645 v-14", C2, 1.4, arrow=ag, dash="4 3")
    f.text(412, 276, "CPU0 MPU region 7 maps CPU1's RAM read-only; nothing guards the other way", 10, "middle", MUTED)
    f.text(445, 40, "15 µs typical, 81 µs max round trip", 10, "middle", MUTED)
    f.render()


def syn_measured():
    f = Fig("syn-measured", 760, 200, "Measured on the FRDM-MCXN947: DMA ingest lands an 8 KB frame in 131 microseconds against 460 for a CPU copy; PowerQuad computes a 256-point FFT in 132 microseconds against 403 in software")
    groups = [("8 KB frame ingest", [("CPU copy", 460), ("eDMA", 131)]),
              ("256-point FFT", [("software, hard FPU", 403), ("PowerQuad", 132)])]
    x0, xmax = 230, 700
    scale = (xmax - x0) / 500
    y = 40
    for gname, bars in groups:
        f.text(x0 - 14, y + 4, gname, 12, "end", weight=600)
        for i, (lbl, v) in enumerate(bars):
            yy = y + 12 + i * 28
            col = C1 if i == 0 else C2
            f.hbar(x0, yy, v * scale, 20, col)
            f.text(x0 - 14, yy + 14, lbl, 11, "end", MUTED)
            f.text(x0 + v * scale + 8, yy + 14, f"{v} µs", 11, "start")
        y += 86
    f.line(x0, 36, x0, 176, LINE, 1)
    f.render()


# ----------------------------------------------------------------------------- Zephyr

def zephyr_timeline():
    prs = [  # number, label, opened(day), merged(day) or None
        (121224, "dts: nxp mcxn flash ranges", 4, None),
        (121225, "boards: nxp mcxn USB1 host clocks", 4, None),
        (121226, "cbprintf: bound packaged strings", 4, None),
        (121250, "usb cdc_acm: logging guard", 4, None),
        (121251, "cmake: gperf check at configure", 4, 8),
        (121369, "cmake: APP_BUILD_VERSION via sysbuild", 5, 9),
        (121370, "boards: frdm_mcxa577 CONFIG_MUX", 5, 13),
        (121602, "soc: opentitan PLIC irq count", 8, None),
        (121728, "tests: uart async_api RX wait", 9, 14),
        (121835, "flash_hp_ra: blank check default", 11, 14),
    ]
    rowh = 26
    top = 44
    h = top + len(prs) * rowh + 50
    f = Fig("zephyr-timeline", 760, h, "Ten pull requests to Zephyr opened between 4 and 11 October 2026; five merged between 8 and 14 October, five still open on 18 October")
    x0, xe = 300, 730
    d0, d1 = 4, 18
    sx = lambda d: x0 + (d - d0) / (d1 - d0) * (xe - x0)
    # day gridlines
    for d in range(d0, d1 + 1, 2):
        f.line(sx(d), top - 8, sx(d), top + len(prs) * rowh, LINE, 1)
        f.text(sx(d), top - 14, f"{d} Oct", 10, "middle", MUTED)
    # freeze marker
    f.line(sx(12), top - 8, sx(12), top + len(prs) * rowh, C2, 1.2, dash="4 3")
    f.text(sx(12) + 4, top + len(prs) * rowh + 16, "4.5 hard freeze", 10, "start", MUTED)
    for i, (n, lbl, o, m) in enumerate(prs):
        y = top + i * rowh
        f.text(14, y + 15, f"#{n}", 11, "start", weight=600)
        f.text(78, y + 15, lbl, 10.5, "start", MUTED)
        if m:
            f.hbar(sx(o), y + 4, max(sx(m) - sx(o), 6), 16, C1)
            f.text(sx(m) + 7, y + 16, "merged", 10, "start")
        else:
            f.add(f'<rect x="{sx(o)}" y="{y + 4}" width="{sx(18) - sx(o)}" height="16" fill="{S3}" stroke="{C3}" stroke-width="1" stroke-dasharray="3 2"/>')
            f.text(sx(18) - 6, y + 16, "open", 10, "end")
    # legend
    ly = top + len(prs) * rowh + 34
    f.add(f'<rect x="300" y="{ly - 10}" width="14" height="12" rx="2" fill="{C1}"/>')
    f.text(320, ly, "opened to merged", 10, "start", MUTED)
    f.add(f'<rect x="440" y="{ly - 10}" width="14" height="12" fill="{S3}" stroke="{C3}" stroke-width="1" stroke-dasharray="3 2"/>')
    f.text(460, ly, "still open on 18 Oct", 10, "start", MUTED)
    f.render()


def zephyr_ranges():
    f = Fig("zephyr-ranges", 760, 300, "Before the fix the secure-alias ranges sat on the flash node and only translated its children, so every partition resolved 0x10000000 too high; after it the controller lives under /soc with one ranges entry per child")
    a = f.arrow_def()
    def column(x, title, nodes, note, bad):
        f.text(x + 150, 24, title, 12, "middle", weight=600)
        y = 40
        for i, (name, prop, hi) in enumerate(nodes):
            stroke = (C2 if bad else C1) if hi else FG
            fill = (S2 if bad else S1) if hi else SURF
            f.rect(x, y, 300, 40, fill, stroke, 1.2, 5)
            f.text(x + 12, y + 17, name, 11, "start", weight=600)
            f.text(x + 12, y + 32, prop, 10, "start", MUTED)
            if i < len(nodes) - 1:
                f.line(x + 150, y + 40, x + 150, y + 52, FG, 1.2, arrow=a)
            y += 54
        f.text(x + 150, y + 8, note, 10.5, "middle", (C2 if bad else C1))
    column(40, "before (4.5 regression)",
           [("flash controller", "no ranges", False),
            ("flash@0", "ranges = <0x0 0x10000000 ...>  (secure alias)", True),
            ("partitions", "reg = <0x0 ...>  children of flash", False),
            ("slot0_partition", "resolves to 0x1000_0000 + offset", True)],
           "MCUboot: \"not same sector layout\"", True)
    column(420, "after (#121224)",
           [("/soc/flash-controller", "ranges = one entry per child", True),
            ("flash@0", "no ranges needed", False),
            ("partitions", "reg = <0x0 ...>  children of flash", False),
            ("slot0_partition", "resolves to 0x0000_0000 + offset", True)],
           "generated DT identical on 15 MCXN targets", False)
    f.text(380, 290, "a node's ranges translates only its own children", 10.5, "middle", MUTED)
    f.render()


def zephyr_loop():
    f = Fig("zephyr-loop", 760, 206, "The contribution loop: scout an unclaimed issue, write a root-cause note, claim it on the issue, fix and build a test matrix, open the PR with a Testing and Not-tested section, answer reviews by rebasing, then merge")
    a = f.arrow_def()
    steps = [("scout", "unclaimed, repro"), ("root-cause note", "verified / inferred"), ("claim on issue", "cause + repro"),
             ("fix + tests", "sim, QEMU, board"), ("pull request", "Testing, Not tested"), ("review", "rebase, force-push"), ("merged", "")]
    n = len(steps)
    w, gap = 98, 6
    x = 19
    y = 60
    for i, (t, s) in enumerate(steps):
        last = i == n - 1
        f.rect(x, y, w, 52, S1 if last else SURF, C1 if last else FG, 1.2, 6)
        f.text(x + w / 2, y + (31 if not s else 22), t, 10, "middle", weight=600)
        if s:
            f.text(x + w / 2, y + 40, s, 8, "middle", MUTED)
        if not last:
            f.line(x + w, y + 26, x + w + gap - 1, y + 26, FG, 1.3, arrow=a)
        x += w + gap
    # review loop back to fix
    xf = 20 + 3 * (w + gap) + w / 2
    xr = 20 + 5 * (w + gap) + w / 2
    ar = f.arrow_def(C2, "r")
    f.path(f"M{xr},{y + 52} v24 H{xf} v-18", C2, 1.4, arrow=ar)
    f.text((xf + xr) / 2, y + 92, "changes requested: smaller fix, shorter commit message", 10, "middle", MUTED)
    f.text(380, 176, "one nudge after seven days of silence, then stop", 10, "middle", MUTED)
    f.text(380, 194, "4 Oct to 18 Oct 2026: 10 PRs opened, 5 merged, 24 lines added by the merged ones", 10, "middle", MUTED)
    f.render()


# ----------------------------------------------------------------------------- LLM

def llm_partition():
    f = Fig("llm-partition", 760, 282, "Layer-wise partitioning keeps one device busy at a time; head-level partitioning runs every layer's attention on all four devices at once, leaving only the FFN on a single device")
    a = f.arrow_def()
    def panel(x, title, kind):
        f.text(x + 170, 22, title, 12, "middle", weight=600)
        devs = ["device 1", "device 2", "device 3", "device 4"]
        y0 = 40
        for i, d in enumerate(devs):
            y = y0 + i * 36
            f.text(x + 56, y + 20, d, 10.5, "end", MUTED)
            f.line(x + 64, y + 30, x + 340, y + 30, LINE, 1)
        tx = x + 64
        if kind == "layer":
            lw = 66
            for L in range(4):
                y = y0 + L * 36
                f.add(f'<rect x="{tx + L * (lw + 2)}" y="{y + 4}" width="{lw}" height="24" rx="3" fill="{S1}" stroke="{C1}" stroke-width="1"/>')
                f.text(tx + L * (lw + 2) + lw / 2, y + 20, f"layer {L + 1}", 10, "middle")
                for D in range(4):
                    if D != L:
                        f.text(tx + L * (lw + 2) + lw / 2, y0 + D * 36 + 20, "idle", 9, "middle", MUTED)
        else:
            # per layer: attention 22 wide on all devices, FFN 38 on device (L % 4)
            aw, fw = 24, 40
            cx = tx
            for L in range(4):
                for D in range(4):
                    y = y0 + D * 36
                    f.add(f'<rect x="{cx}" y="{y + 4}" width="{aw}" height="24" rx="3" fill="{S1}" stroke="{C1}" stroke-width="1"/>')
                fd = L % 4
                y = y0 + fd * 36
                f.add(f'<rect x="{cx + aw + 2}" y="{y + 4}" width="{fw}" height="24" rx="3" fill="{S2}" stroke="{C2}" stroke-width="1"/>')
                f.text(cx + aw + 2 + fw / 2, y + 20, "FFN", 10, "middle")
                cx += aw + fw + 6
        f.line(x + 64, y0 + 4 * 36 + 6, x + 340, y0 + 4 * 36 + 6, FG, 1.2, arrow=a)
        f.text(x + 340, y0 + 4 * 36 + 22, "time", 10, "end", MUTED)
    panel(20, "layer-wise", "layer")
    panel(400, "head-level", "head")
    ly = 250
    f.add(f'<rect x="20" y="{ly - 10}" width="14" height="12" rx="2" fill="{S1}" stroke="{C1}"/>')
    f.text(40, ly, "attention heads (layer-wise: whole layer)", 10, "start", MUTED)
    f.add(f'<rect x="300" y="{ly - 10}" width="14" height="12" rx="2" fill="{S2}" stroke="{C2}"/>')
    f.text(320, ly, "feed-forward network, one device per layer", 10, "start", MUTED)
    f.text(20, ly + 18, "per-layer attention for TinyLlama: 38 ms on one device, 14 ms across four", 10, "start", MUTED)
    f.render()


def llm_speculation():
    f = Fig("llm-speculation", 760, 240, "Inter-layer speculation: once layer l has its intermediate output Z, the next layer's attention starts on Z while the FFN finishes; the result is kept if the FFN contribution is small, otherwise attention is re-run on the exact input")
    a = f.arrow_def()
    x0 = 150
    rows = [("layer l", 60), ("layer l+1", 130)]
    for lbl, y in rows:
        f.text(x0 - 14, y + 18, lbl, 12, "end", weight=600)
        f.line(x0, y + 30, 730, y + 30, LINE, 1)
    def blk(x, y, w, lbl, fill, stroke, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        f.add(f'<rect x="{x}" y="{y + 2}" width="{w}" height="26" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{d}/>')
        f.text(x + w / 2, y + 19, lbl, 10.5, "middle")
    y = 60
    blk(x0, y, 120, "attention", S1, C1)
    blk(x0 + 122, y, 70, "projection", S1, C1)
    blk(x0 + 194, y, 190, "FFN(Z) on device A", S2, C2)
    # Z marker
    zx = x0 + 192
    f.line(zx, y - 14, zx, y + 2, FG, 1.2)
    f.text(zx, y - 20, "Z = X_prev + proj(A) available", 10, "middle", MUTED)
    # forward Z down to next layer
    ar = f.arrow_def(C1, "z")
    f.path(f"M{zx},{y + 30} v18 h12", C1, 1.4, arrow=ar)
    y2 = 130
    blk(zx + 14, y2, 186, "attention on Z (speculative)", S1, C1, "4 3")
    blk(zx + 202, y2, 70, "projection", S1, C1, "4 3")
    # check
    cx = x0 + 384
    f.line(cx, y + 2, cx, 58, FG, 1, dash="2 2")
    f.text(cx + 8, 22, "FFN done: ||FFN(Z)||/||Z|| < 0.05 ?", 10, "start")
    f.text(cx + 8, 36, "yes: keep (84% of transitions)", 10, "start", MUTED)
    f.text(cx + 8, 50, "no: re-run attention on exact X", 10, "start", MUTED)
    # saved time bracket
    f.path(f"M{zx + 14},{y2 + 40} v8 H{x0 + 384} v-8", MUTED, 1)
    f.text((zx + 14 + x0 + 384) / 2, y2 + 64, "overlap hides 70 to 85% of the FFN time", 10, "middle", MUTED)
    f.line(x0, 215, 730, 215, FG, 1.2, arrow=a)
    f.text(730, 232, "time within one token", 10, "end", MUTED)
    f.render()


def llm_latency():
    f = Fig("llm-latency", 760, 176, "Time to generate 256 tokens with TinyLlama-1.1B on four Raspberry Pi 4 workers: 62.4 seconds layer-wise, 48.2 with random head placement, 44.8 round-robin, 40.0 with the greedy placement")
    data = [("layer-wise (baseline)", 62.4, C3), ("heads + speculation, random placement", 48.2, C1), ("heads + speculation, round-robin", 44.8, C1), ("heads + speculation, greedy placement", 40.0, C1)]
    x0, xmax = 300, 700
    sc = (xmax - x0) / 70
    y = 24
    for lbl, v, col in data:
        f.hbar(x0, y, v * sc, 20, col)
        f.text(x0 - 12, y + 14, lbl, 11, "end", MUTED)
        f.text(x0 + v * sc + 8, y + 14, f"{v:.1f} s", 11, "start")
        y += 30
    f.line(x0, 20, x0, y, LINE, 1)
    f.text(x0, y + 22, "seconds for 256 tokens, lower is better; greedy is 1.56x the baseline", 10, "start", MUTED)
    f.render()


def llm_timeshare():
    f = Fig("llm-timeshare", 760, 170, "Share of per-layer time: layer-wise spends 55 percent in attention and 35 in the FFN; after head-level partitioning attention falls to 24 percent and the FFN rises to 48")
    rows = [("layer-wise", [(55, "attention 55%"), (35, "FFN 35%"), (10, "")]), ("head-level", [(24, "attention 24%"), (48, "FFN 48%"), (28, "")])]
    cols = [C1, C2, LINE]
    x0, w = 150, 560
    y = 30
    for lbl, segs in rows:
        f.text(x0 - 14, y + 15, lbl, 12, "end", weight=600)
        x = x0
        for i, (p, t) in enumerate(segs):
            sw = w * p / 100
            f.add(f'<rect x="{x}" y="{y}" width="{sw - 2}" height="22" fill="{cols[i]}"/>')
            if t:
                f.text(x + (sw - 2) / 2, y + 15, t, 10.5, "middle", "#ffffff" if i < 2 else FG, weight=600)
            x += sw
        y += 38
    ly = 130
    for i, (c, t) in enumerate([(C1, "attention"), (C2, "feed-forward network"), (LINE, "communication and other")]):
        lx = x0 + i * 190
        f.add(f'<rect x="{lx}" y="{ly - 10}" width="14" height="12" rx="2" fill="{c}"/>')
        f.text(lx + 20, ly, t, 10, "start", MUTED)
    f.text(x0, 156, "parallelising attention moved the bottleneck to the FFN, which speculation then overlaps", 10, "start", MUTED)
    f.render()


def llm_system():
    f = Fig("llm-system", 760, 230, "One controller holds embeddings, the LM head, placement and the token loop; four workers hold attention heads, projections and FFN blocks and exchange activations over PyTorch RPC on WiFi")
    a = f.arrow_def()
    f.rect(270, 20, 220, 60, S2, C2, 1.3, 8)
    f.text(380, 42, "controller (Raspberry Pi 4)", 12, "middle", weight=600)
    f.text(380, 60, "embeddings, LM head, placement,", 10, "middle", MUTED)
    f.text(380, 72, "speculation decisions, token loop", 10, "middle", MUTED)
    xs = [40, 220, 400, 580]
    for i, x in enumerate(xs):
        f.rect(x, 140, 140, 60, S1, C1, 1.3, 8)
        f.text(x + 70, 160, f"worker {i + 1}", 12, "middle", weight=600)
        f.text(x + 70, 177, "heads, projection, FFN", 10, "middle", MUTED)
        f.text(x + 70, 190, "4 GB, Cortex-A72", 9.5, "middle", MUTED)
        f.line(380, 80, x + 70, 140, FG, 1, arrow=a)
    f.add(f'<rect x="200" y="106" width="360" height="18" rx="4" fill="{SURF}"/>')
    f.text(380, 119, "PyTorch RPC over 802.11ac, 8 to 12 ms RTT, retries for jitter", 10, "middle", MUTED)
    ar = f.arrow_def(C1, "g")
    f.path("M180,215 H580", C1, 1.2, arrow=ar, dash="4 3")
    f.text(380, 226, "head outputs gathered at the projection device, result broadcast to the next layer's devices", 9.5, "middle", MUTED)
    f.render()


# ----------------------------------------------------------------------------- EdgeNN

def edgenn_arena():
    f = Fig("edgenn-arena", 760, 230, "EdgeNN's scratch arena usage over five layers: each operator saves the offset, allocates, computes and restores, so usage returns to the activation baseline after every layer and the peak is the single most expensive layer, not the sum")
    a = f.arrow_def()
    x0, y0, xe, yb = 90, 30, 720, 180
    # axes
    f.line(x0, yb, xe, yb, FG, 1.2, arrow=a)
    f.line(x0, yb, x0, y0, FG, 1.2, arrow=a)
    f.text(xe, yb + 18, "layers", 10, "end", MUTED)
    f.text(x0 - 8, y0 + 4, "scratch", 10, "end", MUTED)
    f.text(x0 - 8, y0 + 16, "offset", 10, "end", MUTED)
    # sawtooth: baseline 140, peaks per layer
    peaks = [110, 70, 125, 95, 60]
    base = 150
    lw = (xe - x0 - 40) / len(peaks)
    d = f"M{x0},{base}"
    for i, p in enumerate(peaks):
        xa = x0 + i * lw + 6
        xb = x0 + (i + 1) * lw - 6
        d += f" H{xa} V{p} H{xb} V{base}"
        f.text(x0 + i * lw + lw / 2, yb + 16, f"layer {i + 1}", 10, "middle", MUTED)
    f.add(f'<path d="{d} H{x0} z" fill="{S1}" stroke="none"/>')
    f.path(d, C1, 2)
    # peak line
    pk = min(peaks)
    f.line(x0, pk, xe - 20, pk, C2, 1, dash="4 3")
    f.text(x0 + 8, pk - 7, "edgenn_arena_peak(): the SRAM to reserve", 10, "start", C2)
    f.text(x0 + lw * 2.5, base + 20, "each layer: save, alloc, compute, restore", 10, "middle", MUTED)
    f.line(x0, base, xe - 20, base, MUTED, 1, dash="2 3")
    f.text(xe - 20, base - 6, "activation tensors", 9.5, "end", MUTED)
    f.text(x0, 212, "weight arena: filled once at load, never freed, zero-copy from flash", 10, "start", MUTED)
    f.render()


def edgenn_int8():
    f = Fig("edgenn-int8", 760, 210, "The INT8 path: int8 inputs and per-channel int8 weights multiply into an int32 accumulator with an int32 bias, then a fixed-point multiplier and shift computed at load time requantise to int8, saturate, and a 256-entry lookup table applies the activation; no float anywhere on this path")
    a = f.arrow_def()
    y = 70
    steps = [("int8 x", "per-tensor scale"), ("int8 w", "per-channel scale"), ("int32 acc", "MAC + int32 bias"),
             ("requantise", "(acc * M) >> shift"), ("saturate", "[-128, 127]"), ("LUT", "256-entry table"), ("int8 y", "")]
    w, gap = 96, 8
    x = 19
    for i, (t, s) in enumerate(steps):
        hot = 2 <= i <= 5
        f.rect(x, y, w, 52, S1 if hot else SURF, C1 if hot else FG, 1.2, 6)
        f.text(x + w / 2, y + (31 if not s else 22), t, 11, "middle", weight=600)
        if s:
            f.text(x + w / 2, y + 40, s, 8, "middle", MUTED)
        if i < len(steps) - 1:
            f.line(x + w, y + 26, x + w + gap - 1, y + 26, FG, 1.3, arrow=a)
        x += w + gap
    # bracket "no float"
    bx0 = 20 + 2 * (w + gap)
    bx1 = 20 + 5 * (w + gap) + w
    f.path(f"M{bx0},{y + 64} v8 H{bx1} v-8", C1, 1.2)
    f.text((bx0 + bx1) / 2, y + 88, "runtime: integer only, SMMUL + shift on Cortex-M7", 10, "middle", C1)
    # load-time inputs
    ar = f.arrow_def(C2, "l")
    lx = 20 + 3 * (w + gap) + w / 2
    f.text(lx, 24, "load time (floats allowed once)", 10, "middle", C2)
    f.text(lx, 38, "M, shift = frexpf(S_in * S_w / S_out)", 10, "middle", MUTED)
    f.line(lx, 44, lx, y - 4, C2, 1.2, arrow=ar)
    lx2 = 20 + 5 * (w + gap) + w / 2
    f.text(lx2, 38, "table = f(scale, zero point)", 10, "middle", MUTED)
    f.line(lx2, 44, lx2, y - 4, C2, 1.2, arrow=ar)
    f.text(380, 190, "symmetric weights (zero point 0) remove one subtraction per multiply-accumulate", 10, "middle", MUTED)
    f.render()


def edgenn_format():
    f = Fig("edgenn-format", 760, 180, "The .edgenn binary: a 44-byte header, then layer records, tensor records and a 16-byte aligned weight blob; a weight tensor's data pointer points straight into the blob, so weights in flash are never copied")
    a = f.arrow_def()
    x0, y0, h = 30, 50, 46
    segs = [("header", "44 B, magic ENNE", 120, S2, C2), ("layer records", "op, in, out, aux", 150, SURF, FG),
            ("tensor records", "shape, dtype, data_offset", 180, SURF, FG), ("weight blob", "16-byte aligned, in flash", 250, S1, C1)]
    x = x0
    pos = {}
    for t, s, w, fill, stroke in segs:
        f.rect(x, y0, w, h, fill, stroke, 1.2, 0)
        f.text(x + w / 2, y0 + 19, t, 11, "middle", weight=600)
        f.text(x + w / 2, y0 + 35, s, 8.5, "middle", MUTED)
        pos[t] = (x, w)
        x += w
    # pointer from tensor record into blob
    ar = f.arrow_def(C1, "p")
    tx = pos["tensor records"][0] + 60
    bx = pos["weight blob"][0] + 90
    f.path(f"M{tx},{y0 + h} v30 H{bx} v-28", C1, 1.4, arrow=ar)
    f.text((tx + bx) / 2, y0 + h + 44, "tensor->data = blob + data_offset  (zero copy)", 10, "middle", C1)
    f.text(x0, y0 + h + 62, "data_offset = 0xFFFFFFFF marks an activation tensor, which is allocated from the arena", 9.5, "start", MUTED)
    f.text(x0, y0 - 14, "offset 0", 10, "start", MUTED)
    f.text(x, y0 - 14, "end of file", 10, "end", MUTED)
    f.render()


if __name__ == "__main__":
    for fn in [syn_arena, syn_sched, syn_dualcore, syn_measured,
               zephyr_timeline, zephyr_ranges, zephyr_loop,
               llm_partition, llm_speculation, llm_latency, llm_timeshare, llm_system,
               edgenn_arena, edgenn_int8, edgenn_format]:
        fn()


# ----------------------------------------------------------------------------- Testbed

def testbed_topology():
    f = Fig("testbed-topology", 760, 320, "The testbed has two networks: an isolated 802.11ac data plane between the edge server's access point and the five boards, and a wired management plane through a switch for SSH, result collection, NTP and package installation")
    a = f.arrow_def()
    # edge server
    f.rect(30, 70, 210, 150, SURF, FG, 1.4, 8)
    f.text(135, 94, "edge server", 12, "middle", weight=600)
    f.text(135, 110, "i7-9700K, 32 GB, Ubuntu 22.04", 9.5, "middle", MUTED)
    for i, t in enumerate(["NNPM + orchestration", "access point 802.11ac", "NTP server, package mirror"]):
        yy = 122 + i * 30
        f.add(f'<rect x="45" y="{yy}" width="180" height="24" rx="4" fill="{S1}" stroke="{C1}" stroke-width="1"/>')
        f.text(135, yy + 16, t, 10, "middle")
    # switch
    f.rect(330, 250, 110, 34, SURF2, LINE, 1, 6)
    f.text(385, 271, "Ethernet switch", 10, "middle", weight=600)
    # devices
    ys = [30, 84, 138, 192, 246]
    for i, y in enumerate(ys):
        f.rect(560, y, 170, 42, SURF, FG, 1.2, 6)
        f.text(645, y + 17, f"device {i + 1}  Raspberry Pi 4", 10.5, "middle", weight=600)
        f.text(645, y + 32, "4 or 8 GB, INA260 on 5 V rail", 9, "middle", MUTED)
        # wireless: thick accent from AP to device
        f.line(240, 160, 560, y + 14, C1, 2.2)
        # wired: thin from switch to device
        f.line(440, 267, 560, y + 30, MUTED, 1, dash="3 3")
    f.line(240, 200, 330, 267, MUTED, 1, dash="3 3")
    # labels with halos
    f.add(f'<rect x="262" y="26" width="276" height="34" rx="4" fill="{SURF}"/>')
    f.text(400, 40, "data plane: isolated 5 GHz 802.11ac", 10, "middle", C1)
    f.text(400, 54, "inference, ping, tc-netem; no default route", 10, "middle", MUTED)
    f.add(f'<rect x="262" y="290" width="276" height="26" rx="4" fill="{SURF}"/>')
    f.text(400, 302, "management plane: SSH dispatch, results, NTP, mirror", 10, "middle", MUTED)
    f.render()


def testbed_pipeline():
    f = Fig("testbed-pipeline", 760, 290, "One experiment runs in seven stages; every change the apply stage makes is journaled with its undo action before the next step, and teardown replays the journal in reverse on success, failure, Stop or after a crash")
    a = f.arrow_def()
    stages = [("preflight", "metadata, NTP check"), ("apply", "shape, load, limits"), ("profile", "start signal T0"), ("collect", "scp + hostname"), ("aggregate", "3 thesis files"), ("optimise", "RR / SJF search"), ("teardown", "undo in reverse")]
    w, gap, x, y = 96, 8, 19, 36
    xs = []
    for i, (t, s) in enumerate(stages):
        hot = i in (1, 6)
        f.rect(x, y, w, 50, S2 if hot else SURF, C2 if hot else FG, 1.2, 6)
        f.text(x + w / 2, y + 21, t, 10.5, "middle", weight=600)
        f.text(x + w / 2, y + 38, s, 8, "middle", MUTED)
        xs.append(x)
        if i < len(stages) - 1:
            f.line(x + w, y + 25, x + w + gap - 1, y + 25, FG, 1.3, arrow=a)
        x += w + gap
    # journal ledger under apply
    entries = ["edge_freq_restore", "cpufreq_restore", "cgroup_remove", "tc_clear", "stop_process (load)", "stop_process (monitor)"]
    jx = xs[1] - 10
    jy = 120
    f.text(jx + 58, jy - 8, "journal.json", 9.5, "middle", weight=600)
    for i, e in enumerate(entries):
        yy = jy + i * 20
        f.add(f'<rect x="{jx}" y="{yy}" width="116" height="17" rx="3" fill="{SURF}" stroke="{LINE}" stroke-width="1"/>')
        f.text(jx + 58, yy + 12, e, 8, "middle", MUTED)
    ar = f.arrow_def(C2, "j")
    f.line(xs[1] + w / 2, y + 50, xs[1] + w / 2, jy - 20, C2, 1.3, arrow=ar)
    f.text(jx + 130, jy + 4, "append the undo", 8.5, "start", MUTED)
    f.text(jx + 130, jy + 16, "before the next step", 8.5, "start", MUTED)
    # teardown pops in reverse
    tx = xs[6] - 24
    f.text(tx + 58, jy - 8, "undo, last first", 9.5, "middle", weight=600)
    for i, e in enumerate(reversed(entries)):
        yy = jy + i * 20
        f.add(f'<rect x="{tx}" y="{yy}" width="116" height="17" rx="3" fill="{S1}" stroke="{C1}" stroke-width="1"/>')
        f.text(tx + 58, yy + 12, e, 8, "middle")
    f.line(xs[6] + w / 2, y + 50, xs[6] + w / 2, jy - 20, C1, 1.3, arrow=f.arrow_def(C1, "t"))
    # triggers into teardown
    f.path(f"M{xs[4] + 20},{jy + 60} H{tx - 14}", MUTED, 1, arrow=a, dash="3 3")
    f.text(xs[4] - 10, jy + 50, "also on failure, Stop,", 8.5, "start", MUTED)
    f.text(xs[4] - 10, jy + 74, "crash + clean_devices.sh", 8.5, "start", MUTED)
    f.text(380, 272, "nothing stays resident: every device process is tagged testbed-&lt;run id&gt;, grouped, and killed by group", 9.5, "middle", MUTED)
    f.render()


def testbed_clock():
    f = Fig("testbed-clock", 760, 230, "Each board has its own monotonic counter; at the shared start instant T0 every board captures wall time and counter together, so any later sample maps to the common clock by arithmetic")
    a = f.arrow_def()
    x0, xe = 150, 700
    t0 = 330
    rows = [("device 1", 54, 0), ("device 2", 104, 37), ("device 3", 154, 18)]
    for lbl, y, off in rows:
        f.text(x0 - 14, y + 4, lbl, 12, "end", weight=600)
        f.line(x0, y, xe, y, LINE, 1.2, arrow=a)
        # ticks with different zeros
        for k in range(12):
            tx = x0 + off + k * 48
            if tx < xe - 10:
                f.line(tx, y - 4, tx, y + 4, MUTED, 1)
        f.text(x0 + off, y + 17, "perf_counter_ns = 0", 8.5, "start", MUTED)
        # capture at T0
        f.add(f'<circle cx="{t0}" cy="{y}" r="5" fill="{C2}" stroke="{SURF}" stroke-width="2"/>')
        # sample later
        sx = t0 + 180
        f.add(f'<circle cx="{sx}" cy="{y}" r="4" fill="{C1}" stroke="{SURF}" stroke-width="2"/>')
    f.line(t0, 30, t0, 172, C2, 1.2, dash="4 3")
    f.text(t0, 22, "T0: start signal, 3 s ahead", 10, "middle", C2)
    f.text(t0 + 180, 184, "sample", 9.5, "middle", C1)
    f.text(x0, 206, "wall = origin.wall_time_s + (sample.perf_counter_ns - origin.perf_counter_ns) / 1e9", 10, "start")
    f.text(x0, 222, "preflight refuses to start if any device's NTP offset exceeds 1 ms (chrony on the edge server)", 9.5, "start", MUTED)
    f.render()


def testbed_validation():
    f = Fig("testbed-validation", 760, 190, "Chapter 4 validation on four boards with AlexNet, 50 runs per policy: the delay model predicted 1042 ms under round-robin and the testbed measured 1087 plus or minus 34; under shortest-job-first 986 predicted against 1021 plus or minus 29")
    x0, xmax = 190, 690
    sc = (xmax - x0) / 1500
    groups = [("round-robin", 1042, 1087, 34, "+4.3%"), ("shortest-job-first", 986, 1021, 29, "+3.6%")]
    y = 30
    for name, pred, meas, err, gap in groups:
        f.text(x0 - 14, y + 4, name, 12, "end", weight=600)
        f.hbar(x0, y + 10, pred * sc, 18, C3)
        f.text(x0 - 14, y + 23, "predicted", 10, "end", MUTED)
        f.text(x0 + pred * sc + 8, y + 23, f"{pred:,} ms", 10.5, "start")
        yy = y + 32
        f.hbar(x0, yy, meas * sc, 18, C1)
        f.text(x0 - 14, yy + 13, "measured", 10, "end", MUTED)
        ex0, ex1 = x0 + (meas - err) * sc, x0 + (meas + err) * sc
        f.line(ex0, yy + 9, ex1, yy + 9, FG, 1.4)
        f.line(ex0, yy + 4, ex0, yy + 14, FG, 1.4)
        f.line(ex1, yy + 4, ex1, yy + 14, FG, 1.4)
        f.text(ex1 + 8, yy + 13, f"{meas:,} ± {err} ms  ({gap})", 10.5, "start")
        y += 70
    f.line(x0, 26, x0, 166, LINE, 1)
    ly = 178
    f.add(f'<rect x="{x0}" y="{ly - 10}" width="14" height="12" rx="2" fill="{C3}"/>')
    f.text(x0 + 20, ly, "analytical delay model", 10, "start", MUTED)
    f.add(f'<rect x="{x0 + 190}" y="{ly - 10}" width="14" height="12" rx="2" fill="{C1}"/>')
    f.text(x0 + 210, ly, "testbed, mean ± std over 50 runs", 10, "start", MUTED)
    f.render()


for fn in [testbed_topology, testbed_pipeline, testbed_clock, testbed_validation]:
    fn()
