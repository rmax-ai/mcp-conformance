<script>
  import { base } from "$app/paths";
  import { onMount } from "svelte";
  import { dev } from "$app/environment";

  export let title = "MCP Conformance";
  export let description =
    "Scenario-driven test runner for evaluating MCP client and server implementations.";

  onMount(() => {
    const loadMermaid = () => {
      if (document.querySelector('script[data-mermaid]')) return;
      const s = document.createElement("script");
      s.src = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js";
      s.dataset.mermaid = "1";
      s.onload = () => {
        window.mermaid.initialize({
          startOnLoad: false,
          theme: "base",
          themeVariables: {
            background: "transparent",
            primaryColor: "#0f172a",
            primaryBorderColor: "#38bdf8",
            primaryTextColor: "#e2e8f0",
            lineColor: "#475569",
            secondaryColor: "#1e293b",
            tertiaryColor: "#0c1929",
          },
        });
        const blocks = document.querySelectorAll("code.language-mermaid");
        if (blocks.length === 0) return;
        let idx = 0;
        blocks.forEach(async (el) => {
          const source = el.textContent.trim();
          if (!source) return;
          const id = "mermaid-" + (idx++);
          try {
            const { svg } = await window.mermaid.render(id, source);
            const wrapper = document.createElement("div");
            wrapper.className = "mermaid-render";
            wrapper.innerHTML = svg;
            el.parentElement.replaceWith(wrapper);
          } catch (e) {
            console.error("Mermaid render error:", e?.message || e);
          }
        });
      };
      s.onerror = () => console.error("Mermaid CDN failed to load");
      document.head.appendChild(s);
    };
    loadMermaid();
  });

  const navItems = [
    { href: `${base}/`, label: "Overview" },
    { href: `${base}/scenarios/`, label: "Scenarios" },
    { href: `${base}/authoring/`, label: "Authoring" },
    { href: `${base}/adapters/`, label: "Adapters" },
    { href: `${base}/reports/`, label: "Reports" },
  ];
</script>

<svelte:head>
  <title>{title} | MCP Conformance</title>
  <meta name="description" content={description} />
</svelte:head>

<div class="page-shell">
  <div class="backdrop backdrop-a"></div>
  <div class="backdrop backdrop-b"></div>

  <header class="site-header">
    <a class="brand" href={`${base}/`}>
      <span class="brand-mark">CC</span>
      <span class="brand-copy">
        <strong>MCP Conformance</strong>
        <small>Scenario-driven protocol test runner</small>
      </span>
    </a>

    <nav aria-label="Primary">
      {#each navItems as item}
        <a href={item.href}>{item.label}</a>
      {/each}
      <a href="https://github.com/rmax-ai/mcp-conformance" rel="noreferrer">GitHub</a>
    </nav>
  </header>

  <main class="content">
    <slot />
  </main>

  <footer class="site-footer">
    <p>Built with SvelteKit + mdsvex. Deployable as a static site on GitHub Pages.</p>
  </footer>
</div>

<style>
  :global(html) {
    background:
      radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 30%),
      radial-gradient(circle at 85% 20%, rgba(99, 102, 241, 0.12), transparent 28%),
      linear-gradient(180deg, #0b1120 0%, #0f172a 42%, #020617 100%);
    color: #e2e8f0;
    font-family:
      "Iowan Old Style",
      "Palatino Linotype",
      "Book Antiqua",
      Georgia,
      serif;
  }

  :global(body) {
    margin: 0;
    min-height: 100vh;
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(a) {
    color: #93c5fd;
  }

  :global(code) {
    font-family:
      "SFMono-Regular",
      Consolas,
      "Liberation Mono",
      Menlo,
      monospace;
  }

  :global(pre) {
    overflow-x: auto;
    padding: 1.1rem 1.25rem;
    border-radius: 18px;
    background: #0f172a;
    color: #e2e8f0;
    border: 1px solid rgba(148, 163, 184, 0.15);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }

  :global(pre code) {
    display: block;
    line-height: 1.6;
    font-size: 0.93rem;
  }

  :global(h1),
  :global(h2),
  :global(h3) {
    font-family:
      "Avenir Next Condensed",
      "Arial Narrow",
      sans-serif;
    letter-spacing: 0.02em;
    line-height: 0.95;
    margin: 0 0 0.75rem;
  }

  :global(h1) {
    font-size: clamp(3.4rem, 9vw, 6.8rem);
  }

  :global(h2) {
    font-size: clamp(2rem, 3.8vw, 3rem);
    margin-top: 2.75rem;
  }

  :global(h3) {
    font-size: clamp(1.35rem, 2.5vw, 1.9rem);
    margin-top: 1.75rem;
  }

  :global(p),
  :global(li) {
    font-size: 1.03rem;
    line-height: 1.7;
  }

  :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    background: rgba(15, 23, 42, 0.72);
    border-radius: 16px;
    overflow: hidden;
    backdrop-filter: blur(10px);
  }

  :global(th),
  :global(td) {
    text-align: left;
    padding: 0.9rem 1rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    vertical-align: top;
  }

  :global(th) {
    color: #93c5fd;
    font-weight: 700;
  }

  :global(blockquote) {
    margin: 1.5rem 0;
    padding: 0.25rem 0 0.25rem 1rem;
    border-left: 4px solid #38bdf8;
    color: #94a3b8;
  }

  :global(.eyebrow) {
    display: inline-flex;
    gap: 0.55rem;
    align-items: center;
    padding: 0.4rem 0.72rem;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.12);
    font-family:
      "Avenir Next",
      "Segoe UI",
      sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  :global(.panel-grid) {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0 2rem;
  }

  :global(.panel-card) {
    padding: 1.2rem;
    border-radius: 20px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.1);
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.3);
  }

  :global(.hero-note) {
    max-width: 55rem;
    font-size: 1.16rem;
    color: #94a3b8;
  }

  :global(.command-callout) {
    margin: 1.5rem 0;
    padding: 1rem 1.15rem;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.1);
    background: rgba(15, 23, 42, 0.5);
  }

  .page-shell {
    position: relative;
    min-height: 100vh;
    overflow: hidden;
  }

  .backdrop {
    position: fixed;
    inset: auto;
    border-radius: 999px;
    filter: blur(30px);
    opacity: 0.9;
    pointer-events: none;
  }

  .backdrop-a {
    width: 16rem;
    height: 16rem;
    top: 6rem;
    right: -3rem;
    background: rgba(56, 189, 248, 0.15);
  }

  .backdrop-b {
    width: 18rem;
    height: 18rem;
    bottom: 6rem;
    left: -5rem;
    background: rgba(99, 102, 241, 0.12);
  }

  .site-header,
  .content,
  .site-footer {
    position: relative;
    z-index: 1;
    width: min(1100px, calc(100vw - 2rem));
    margin: 0 auto;
  }

  .site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    padding: 1.25rem 0 0;
  }

  .brand {
    display: inline-flex;
    gap: 0.9rem;
    align-items: center;
    text-decoration: none;
  }

  .brand-mark {
    display: grid;
    place-items: center;
    width: 3rem;
    height: 3rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    color: #e2e8f0;
    font-family:
      "Avenir Next Condensed",
      "Arial Narrow",
      sans-serif;
    font-weight: 800;
    letter-spacing: 0.1em;
  }

  .brand-copy {
    display: grid;
  }

  .brand-copy strong {
    font-family:
      "Avenir Next Condensed",
      "Arial Narrow",
      sans-serif;
    font-size: 1.12rem;
    letter-spacing: 0.04em;
  }

  .brand-copy small {
    color: #94a3b8;
  }

  nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
  }

  nav a {
    text-decoration: none;
    padding: 0.55rem 0.85rem;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.76);
    border: 1px solid rgba(148, 163, 184, 0.08);
    color: #93c5fd;
  }

  .content {
    padding: 3.2rem 0 4rem;
  }

  .site-footer {
    padding: 0 0 2.5rem;
    color: #64748b;
  }

  @media (max-width: 720px) {
    .site-header {
      align-items: flex-start;
      flex-direction: column;
    }

    .content {
      padding-top: 2.2rem;
    }
  }
</style>
