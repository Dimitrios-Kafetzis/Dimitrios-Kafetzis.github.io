#!/usr/bin/env python3
"""Assemble the site from _src/ into plain static HTML. No dependencies beyond Python 3.8+.

    python3 _build.py

Pages:  _src/pages/<name>.body.html  ->  <name>.html
Posts:  _src/posts.json + _src/posts/<slug>.html  ->  blog/<slug>.html, blog.html, feed.xml
"""
import datetime as dt
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "_src"
BASE = "https://dimitrios-kafetzis.github.io/"
AUTHOR = "Dimitrios Kafetzis"

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' rx='14' fill='%23121a2b'/%3E"
        "%3Ctext x='32' y='41' text-anchor='middle' font-family='IBM Plex Mono,Menlo,monospace' font-size='26' font-weight='600' fill='%23f4f6f9'%3EDK%3C/text%3E%3C/svg%3E")

PAGES = {
    "index.html": dict(title="Dimitrios Kafetzis", desc="Systems architect and researcher working where embedded systems, networks and AI meet. PhD candidate at AUEB, creator of SynapticOS, Zephyr contributor."),
    "about.html": dict(title="About · Dimitrios Kafetzis", desc="Career timeline, education, funded research projects, awards and skills of Dimitrios Kafetzis."),
    "projects.html": dict(title="Projects · Dimitrios Kafetzis", desc="Open-source systems by Dimitrios Kafetzis: SynapticOS, EdgeNN, HeadSplit, Fieldproof, NMEA Simulator X and more."),
    "publications.html": dict(title="Publications · Dimitrios Kafetzis", desc="Peer-reviewed papers and preprints by Dimitrios Kafetzis on edge AI, distributed inference, SDN/SDR and tactical networks."),
    "blog.html": dict(title="Blog · Dimitrios Kafetzis", desc="Lessons learned from building operating systems, inference runtimes and research testbeds for the edge."),
}

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{base}assets/portrait.jpg">
<meta property="og:site_name" content="Dimitrios Kafetzis">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#f4f6f9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b1120" media="(prefers-color-scheme: dark)">
<link rel="alternate" type="application/rss+xml" title="Dimitrios Kafetzis · Blog" href="{base}feed.xml">
<link rel="icon" href="{icon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{p}assets/style.css">
<script>try{{var t=localStorage.getItem("theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
{extra_head}</head>
<body>
<header class="site-header">
  <nav class="nav wrap" aria-label="Main">
    <a class="brand" href="{p}index.html"><span class="mark" aria-hidden="true">DK</span><span>Dimitrios Kafetzis</span></a>
    <ul class="nav-links" id="nav-links">
      <li><a href="{p}index.html">Home</a></li>
      <li><a href="{p}about.html">About</a></li>
      <li><a href="{p}projects.html">Projects</a></li>
      <li><a href="{p}publications.html">Publications</a></li>
      <li><a href="{p}blog.html"{blogcur}>Blog</a></li>
    </ul>
    <div class="nav-actions">
      <a class="icon-btn hide-sm" href="https://github.com/Dimitrios-Kafetzis" aria-label="GitHub" title="GitHub"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg></a>
      <a class="icon-btn hide-sm" href="https://scholar.google.com/citations?user=3RLgkhwAAAAJ&amp;hl=en" aria-label="Google Scholar" title="Google Scholar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"/></svg></a>
      <a class="icon-btn hide-sm" href="https://linkedin.com/in/dimitrios-kafetzis" aria-label="LinkedIn" title="LinkedIn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>
      <a class="icon-btn hide-sm" href="{p}feed.xml" aria-label="RSS feed" title="RSS feed"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.199 24C19.199 13.467 10.533 4.8 0 4.8V0c13.165 0 24 10.835 24 24h-4.801zM3.291 17.415a3.3 3.3 0 0 1 3.293 3.295A3.303 3.303 0 0 1 3.283 24C1.47 24 0 22.526 0 20.71s1.475-3.294 3.291-3.295zM15.909 24h-4.665c0-6.169-5.075-11.245-11.244-11.245V8.09c8.727 0 15.909 7.184 15.909 15.91z"/></svg></a>
      <button class="icon-btn" id="theme-toggle" type="button" aria-label="Switch theme"><svg class="sun" viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round" hidden><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg><svg class="moon" viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg></button>
      <button class="icon-btn menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </nav>
</header>
<main>
"""

FOOT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <a class="brand" href="{p}index.html"><span class="mark" aria-hidden="true">DK</span><span>Dimitrios Kafetzis</span></a>
      <p class="tagline" style="margin-top:12px">Systems architect and researcher. Embedded systems, edge AI and networks, from the PCB to the model.</p>
      <div class="contact-line"><code>dimitrioskafetzis@gmail.com</code><button class="copy-btn" type="button" data-copy="dimitrioskafetzis@gmail.com">Copy</button></div>
    </div>
    <div>
      <h3>Site</h3>
      <ul>
        <li><a href="{p}index.html">Home</a></li>
        <li><a href="{p}about.html">About</a></li>
        <li><a href="{p}projects.html">Projects</a></li>
        <li><a href="{p}publications.html">Publications</a></li>
        <li><a href="{p}blog.html">Blog</a></li>
        <li><a href="{p}feed.xml">RSS feed</a></li>
      </ul>
    </div>
    <div>
      <h3>Elsewhere</h3>
      <ul>
        <li><a href="https://github.com/Dimitrios-Kafetzis">GitHub</a></li>
        <li><a href="https://scholar.google.com/citations?user=3RLgkhwAAAAJ&amp;hl=en">Google Scholar</a></li>
        <li><a href="https://www.researchgate.net/profile/Dimitrios_Kafetzis3">ResearchGate</a></li>
        <li><a href="https://arxiv.org/search/?query=Kafetzis%2C+Dimitrios&amp;searchtype=author">arXiv</a></li>
        <li><a href="https://linkedin.com/in/dimitrios-kafetzis">LinkedIn</a></li>
        <li><a href="https://synapticos.io/">SynapticOS</a></li>
      </ul>
    </div>
    <div class="legal"><span>&copy; <span id="year">2026</span> Dimitrios Kafetzis</span><span>Athens &middot; Hamburg</span></div>
  </div>
</footer>
<script src="{p}assets/site.js"></script>
</body>
</html>
"""

SHARE_ICONS = {
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    "bluesky": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"/></svg>',
    "hn": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M0 24V0h24v24H0zM6.951 5.896l4.112 7.708v5.064h1.583v-4.972l4.148-7.799h-1.749l-2.457 4.875c-.372.745-.688 1.434-.688 1.434s-.297-.708-.651-1.434L8.831 5.896h-1.88z"/></svg>',
    "reddit": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
}


def q(s):
    from urllib.parse import quote
    return quote(s, safe="")


def share_row(url, title):
    t = f"{title} by {AUTHOR}"
    items = [
        ("x", "Share on X", f"https://twitter.com/intent/tweet?text={q(t)}&url={q(url)}"),
        ("linkedin", "Share on LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={q(url)}"),
        ("bluesky", "Share on Bluesky", f"https://bsky.app/intent/compose?text={q(t + ' ' + url)}"),
        ("hn", "Submit to Hacker News", f"https://news.ycombinator.com/submitlink?u={q(url)}&t={q(title)}"),
        ("reddit", "Share on Reddit", f"https://www.reddit.com/submit?url={q(url)}&title={q(title)}"),
        ("mail", "Share by email", f"mailto:?subject={q(title)}&body={q(url)}"),
    ]
    out = ['<div class="share" aria-label="Share this article"><span class="share-label">Share</span>']
    for key, label, href in items:
        out.append(f'<a class="share-btn" href="{html.escape(href)}" target="_blank" rel="noopener" aria-label="{label}" title="{label}">{SHARE_ICONS[key]}</a>')
    out.append(f'<button class="share-btn" type="button" data-copy="{html.escape(url)}" data-copy-label aria-label="Copy link" title="Copy link">{SHARE_ICONS["link"]}</button>')
    out.append("</div>")
    return "".join(out)


def reading_time(body_html):
    prose = re.sub(r"<svg.*?</svg>", " ", body_html, flags=re.S)
    words = len(re.sub(r"<[^>]+>", " ", prose).split())
    return max(1, round(words / 220))


def fmt_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%-d %B %Y")


def rfc822(iso):
    d = dt.datetime.combine(dt.date.fromisoformat(iso), dt.time(9, 0), tzinfo=dt.timezone.utc)
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


def render(name, body, meta, depth=0, extra_head="", ogtype="website", blogcur=""):
    p = "../" * depth
    canon = BASE + ("" if name == "index.html" else name)
    head = HEAD.format(title=html.escape(meta["title"]), desc=html.escape(meta["desc"]), canon=canon, base=BASE,
                       icon=ICON, p=p, extra_head=extra_head, ogtype=ogtype, blogcur=blogcur)
    return head + body + FOOT.format(p=p)


def main():
    posts = json.loads((SRC / "posts.json").read_text(encoding="utf-8"))
    posts = [p for p in posts if not p.get("draft")]
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Posts
    def inline_figures(body):
        def repl(m):
            svg = (SRC / "figures" / f"{m.group(1)}.svg").read_text(encoding="utf-8")
            return svg
        return re.sub(r"<!--\s*fig:([a-z0-9-]+)\s*-->", repl, body)

    for post in posts:
        body = (SRC / "posts" / f"{post['slug']}.html").read_text(encoding="utf-8")
        body = inline_figures(body)
        post["minutes"] = reading_time(body)
        post["body"] = body
        url = f"{BASE}blog/{post['slug']}.html"
        tags = "".join(f"<li>{html.escape(t)}</li>" for t in post.get("tags", []))
        article = f"""<article class="article wrap">
  <header class="article-head">
    <p class="eyebrow"><a href="../blog.html">Blog</a></p>
    <h1>{html.escape(post['title'])}</h1>
    <p class="lede">{html.escape(post['summary'])}</p>
    <p class="meta mono"><time datetime="{post['date']}">{fmt_date(post['date'])}</time> &middot; {post['minutes']} min read</p>
    <ul class="tags">{tags}</ul>
  </header>
  <div class="article-body">
{body}
  </div>
  <footer class="article-foot">
    {share_row(url, post['title'])}
    <p class="muted">Written by {AUTHOR}. Corrections and questions are welcome at <a href="mailto:dimitrioskafetzis@gmail.com">dimitrioskafetzis@gmail.com</a>. Subscribe to new articles with the <a href="../feed.xml">RSS feed</a>.</p>
  </footer>
</article>
"""
        meta = dict(title=f"{post['title']} · Dimitrios Kafetzis", desc=post["summary"])
        extra = (f'<meta property="article:published_time" content="{post["date"]}">\n'
                 f'<meta property="article:author" content="{AUTHOR}">\n')
        out = render(f"blog/{post['slug']}.html", article, meta, depth=1, extra_head=extra, ogtype="article", blogcur=' aria-current="page"')
        (ROOT / "blog" / f"{post['slug']}.html").write_text(out, encoding="utf-8")
        print(f"blog/{post['slug']}.html  {post['minutes']} min")

    # Blog index
    items = []
    for post in posts:
        tags = "".join(f"<li>{html.escape(t)}</li>" for t in post.get("tags", []))
        items.append(f"""      <article class="post-item">
        <div class="when mono"><time datetime="{post['date']}">{fmt_date(post['date'])}</time><span>{post['minutes']} min read</span></div>
        <div>
          <h2><a href="blog/{post['slug']}.html">{html.escape(post['title'])}</a></h2>
          <p>{html.escape(post['summary'])}</p>
          <ul class="tags">{tags}</ul>
        </div>
      </article>""")
    blog_body = f"""<section class="page-title wrap">
  <p class="eyebrow">Blog</p>
  <h1>Notes from the workbench</h1>
  <p>Lessons learned while building operating systems, inference runtimes, simulators and research testbeds for constrained hardware. New articles arrive by <a href="feed.xml">RSS</a>.</p>
</section>
<section class="section">
  <div class="wrap">
    <div class="post-list">
{chr(10).join(items)}
    </div>
  </div>
</section>
"""
    (ROOT / "blog.html").write_text(render("blog.html", blog_body, PAGES["blog.html"]), encoding="utf-8")

    # Pages (home gets the latest three posts injected)
    latest = ""
    for post in posts[:3]:
        latest += f"""      <article class="post-item">
        <div class="when mono"><time datetime="{post['date']}">{fmt_date(post['date'])}</time><span>{post['minutes']} min read</span></div>
        <div>
          <h3><a href="blog/{post['slug']}.html">{html.escape(post['title'])}</a></h3>
          <p>{html.escape(post['summary'])}</p>
        </div>
      </article>
"""
    for name, meta in PAGES.items():
        if name == "blog.html":
            continue
        body = (SRC / "pages" / name.replace(".html", ".body.html")).read_text(encoding="utf-8")
        body = body.replace("<!-- LATEST_POSTS -->", latest)
        (ROOT / name).write_text(render(name, body, meta), encoding="utf-8")
        print(name)

    # RSS
    rss = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">',
           "<channel>",
           f"<title>Dimitrios Kafetzis · Blog</title>",
           f"<link>{BASE}blog.html</link>",
           f'<atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>',
           "<description>Lessons learned while building operating systems, inference runtimes and research testbeds for constrained hardware.</description>",
           "<language>en</language>",
           f"<lastBuildDate>{rfc822(posts[0]['date']) if posts else rfc822(dt.date.today().isoformat())}</lastBuildDate>"]
    for post in posts:
        url = f"{BASE}blog/{post['slug']}.html"
        content = post["body"].replace("]]>", "]]]]><![CDATA[>")
        rss += ["<item>",
                f"<title>{html.escape(post['title'])}</title>",
                f"<link>{url}</link>",
                f'<guid isPermaLink="true">{url}</guid>',
                f"<pubDate>{rfc822(post['date'])}</pubDate>",
                f"<description>{html.escape(post['summary'])}</description>",
                f"<content:encoded><![CDATA[{content}]]></content:encoded>"]
        rss += [f"<category>{html.escape(t)}</category>" for t in post.get("tags", [])]
        rss += ["</item>"]
    rss += ["</channel>", "</rss>", ""]
    (ROOT / "feed.xml").write_text("\n".join(rss), encoding="utf-8")
    print("feed.xml", len(posts), "items")

    # Sitemap + robots
    urls = [BASE] + [BASE + n for n in PAGES if n != "index.html"] + [f"{BASE}blog/{p['slug']}.html" for p in posts]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    main()
