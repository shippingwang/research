#!/usr/bin/env python3
"""Build a static research notes site from posts/*.md."""

from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

SITE_TITLE = "research"
HOME_URL = "/"
BASE = "/research"  # deployed under shippingwang.com/research/


@dataclass
class Post:
    slug: str
    title: str
    date: str
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    body_html: str = ""


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key == "tags":
            inner = val
            if inner.startswith("[") and inner.endswith("]"):
                inner = inner[1:-1]
            meta["tags"] = [t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip()]
        else:
            meta[key] = val
    return meta, body


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def md_to_html(src: str) -> str:
    lines = src.splitlines()
    out: list[str] = []
    i = 0
    in_ul = False
    in_pre = False
    pre_buf: list[str] = []

    def close_ul():
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_pre:
                close_ul()
                code = html.escape("\n".join(pre_buf))
                out.append(f"<pre><code>{code}</code></pre>")
                pre_buf = []
                in_pre = False
            else:
                close_ul()
                in_pre = True
            i += 1
            continue
        if in_pre:
            pre_buf.append(line)
            i += 1
            continue
        if not line.strip():
            close_ul()
            i += 1
            continue
        if line.startswith("### "):
            close_ul()
            out.append(f"<h3>{md_inline(line[4:].strip())}</h3>")
        elif line.startswith("## "):
            close_ul()
            out.append(f"<h2>{md_inline(line[3:].strip())}</h2>")
        elif line.startswith("# "):
            close_ul()
            out.append(f"<h2>{md_inline(line[2:].strip())}</h2>")
        elif line.startswith("> "):
            close_ul()
            out.append(f"<blockquote><p>{md_inline(line[2:].strip())}</p></blockquote>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{md_inline(line[2:].strip())}</li>")
        else:
            close_ul()
            out.append(f"<p>{md_inline(line.strip())}</p>")
        i += 1
    close_ul()
    if in_pre:
        code = html.escape("\n".join(pre_buf))
        out.append(f"<pre><code>{code}</code></pre>")
    return "\n".join(out)


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title") or path.stem
        posts.append(
            Post(
                slug=path.stem,
                title=title,
                date=meta.get("date") or date.today().isoformat(),
                tags=meta.get("tags") or [],
                summary=meta.get("summary") or "",
                body_html=md_to_html(body),
            )
        )
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def shell(title: str, body: str, active: str = "research") -> str:
    def nav_cls(name: str) -> str:
        return ' class="is-active"' if active == name else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <link rel="icon" href="/assets/favicon.png" type="image/png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{BASE}/css/research.css" />
</head>
<body>
  <header class="nav">
    <div class="wrap nav__inner">
      <a class="nav__brand" href="{HOME_URL}" aria-label="shippingwang">
        <img class="nav__mark" src="/assets/favicon.png" alt="" width="28" height="28" />
        <span class="nav__brand-text">shippingwang</span>
      </a>
      <nav class="nav__links" aria-label="primary">
        <a{nav_cls("research")} href="{BASE}/">research</a>
        <a{nav_cls("book")} href="/book/">book</a>
        <a{nav_cls("life")} href="/life/">life</a>
        <a{nav_cls("idea")} href="/idea/">idea</a>
      </nav>
    </div>
  </header>
  {body}
  <footer class="site-footer">
    <div class="wrap site-footer__inner">
      <span>shippingwang / research</span>
      <a href="{HOME_URL}">home</a>
    </div>
  </footer>
</body>
</html>
"""


def render_index(posts: list[Post], tag: str | None = None) -> str:
    all_tags = sorted({t for p in posts for t in p.tags}, key=str.casefold)
    visible = [p for p in posts if tag is None or tag in p.tags]
    tag_links = [
        '<a class="tag{cls}" href="{href}">{label}</a>'.format(
            cls=" is-active" if tag is None else "",
            href=f"{BASE}/",
            label="all",
        )
    ]
    for t in all_tags:
        tag_links.append(
            '<a class="tag{cls}" href="{href}">{label}</a>'.format(
                cls=" is-active" if tag == t else "",
                href=f"{BASE}/tag/{html.escape(t)}/",
                label=html.escape(t),
            )
        )

    cards = []
    for p in visible:
        ordered_tags = sorted(p.tags, key=str.casefold)
        tags_html = "".join(
            f'<a class="tag" href="{BASE}/tag/{html.escape(t)}/">{html.escape(t)}</a>'
            for t in ordered_tags
        )
        summary = html.escape(p.summary) if p.summary else ""
        cards.append(
            f"""<li class="post-card">
  <div class="post-card__meta"><time datetime="{html.escape(p.date)}">{html.escape(p.date)}</time></div>
  <h2 class="post-card__title"><a href="{BASE}/{html.escape(p.slug)}/">{html.escape(p.title)}</a></h2>
  {"<p class='post-card__summary'>" + summary + "</p>" if summary else ""}
  <div class="post-card__tags">{tags_html}</div>
</li>"""
        )
    if not cards:
        cards.append('<li class="empty">No notes under this tag.</li>')

    heading = "research" if tag is None else f"tag · {tag}"
    body = f"""
  <main class="wrap">
    <header class="masthead">
      <h1 class="masthead__title">{html.escape(heading)}</h1>
    </header>
    <div class="tag-bar tag-bar--filter">{"".join(tag_links)}</div>
    <ul class="post-list">
      {"".join(cards)}
    </ul>
  </main>
"""
    page_title = SITE_TITLE if tag is None else f"{tag} · research"
    return shell(page_title, body)


def render_post(post: Post) -> str:
    ordered_tags = sorted(post.tags, key=str.casefold)
    tags_html = " ".join(
        f'<a class="tag" href="{BASE}/tag/{html.escape(t)}/">{html.escape(t)}</a>'
        for t in ordered_tags
    )
    body = f"""
  <main class="wrap article">
    <div class="article__meta">
      <time datetime="{html.escape(post.date)}">{html.escape(post.date)}</time>
      {tags_html}
    </div>
    <h1 class="article__title">{html.escape(post.title)}</h1>
    <div class="article__body">
{post.body_html}
    </div>
    <a class="article__back" href="{BASE}/">← index</a>
  </main>
"""
    return shell(f"{post.title} · research", body)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(STATIC / "css", DIST / "css")

    posts = load_posts()
    write(DIST / "index.html", render_index(posts))

    for post in posts:
        write(DIST / post.slug / "index.html", render_post(post))

    tags = sorted({t for p in posts for t in p.tags})
    for tag in tags:
        write(DIST / "tag" / tag / "index.html", render_index(posts, tag=tag))

    print(f"built {len(posts)} posts → {DIST}")


if __name__ == "__main__":
    main()
