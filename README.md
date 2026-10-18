# dimitrios-kafetzis.github.io

Personal site, served by GitHub Pages from `main`. Plain HTML, one stylesheet, one script, no dependencies.

## Layout

| Path | What it is |
| --- | --- |
| `_src/pages/*.body.html` | Page content for Home, About, Projects, Publications (everything between the header and footer) |
| `_src/posts.json` | Blog post list: slug, title, date, summary, tags, optional `"draft": true` |
| `_src/posts/<slug>.html` | Blog post body (HTML, starting at the first `<p>` or `<h2>`) |
| `_build.py` | Assembles pages, posts, `blog.html`, `feed.xml` and `sitemap.xml` |
| `assets/` | `style.css`, `site.js`, portrait images |
| `blog/` | Generated post pages |
| `*.pdf`, `*.bib` | Paper PDFs and BibTeX, linked from the publications page and the GitHub profile README |

## Editing

1. Edit a file under `_src/`.
2. Run `python3 _build.py` (Python 3.8 or newer, no packages needed).
3. Commit the generated files together with the source and push.

Generated files (`index.html`, `about.html`, `projects.html`, `publications.html`, `blog.html`, `blog/*.html`, `feed.xml`, `sitemap.xml`, `robots.txt`) are overwritten on every build, so do not edit them by hand.

## Adding a blog post

1. Write the article body as HTML in `_src/posts/<slug>.html`. Use `<h2>` for sections, `<p>` for paragraphs, `<pre><code>` for code, `<figure>` with `<figcaption>` for images.
2. Add an entry to `_src/posts.json`:

   ```json
   {
     "slug": "my-post",
     "title": "Title of the article",
     "date": "2026-11-01",
     "summary": "One or two sentences shown in the list, on the home page and in the RSS feed.",
     "tags": ["Zephyr", "Embedded"]
   }
   ```

3. Run `python3 _build.py`. The post page, the blog index, the three latest posts on the home page, the RSS feed and the sitemap update together.

Reading time is computed from the word count. Share buttons (X, LinkedIn, Bluesky, Hacker News, Reddit, email, copy link) are added to every post automatically.

## Theme

Colours and fonts are CSS custom properties at the top of `assets/style.css`. Light and dark themes follow the visitor's system setting; the header toggle overrides it and remembers the choice in the browser.
