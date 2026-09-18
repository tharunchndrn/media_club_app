import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";

const navItems = [
  {
    to: "/",
    label: "Overview",
    end: true,
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zm-10 9a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1v-5zm10-2a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1v-7z"
      />
    ),
  },
  {
    to: "/events",
    label: "Events",
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
      />
    ),
  },
  {
    to: "/committee",
    label: "Committee",
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
      />
    ),
  },
  {
    to: "/suggestions",
    label: "Suggestions",
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
      />
    ),
  },
];

export function Layout({ children }: { children: ReactNode }) {
  const [navOpen, setNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      {navOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-navy-950/45 lg:hidden"
          onClick={() => setNavOpen(false)}
        />
      )}

      <aside
        id="main-nav"
        className={`fixed top-0 left-0 z-40 flex h-screen w-64 flex-col border-r border-ink-200 bg-white shadow-sm
          transition-transform duration-200 ease-out lg:sticky lg:translate-x-0
          ${navOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="border-b border-ink-200 px-6 py-5">
          <img
            src="/logo.png"
            alt="NIBM KIC Media Club"
            className="h-10 w-auto object-contain object-left"
          />
        </div>

        <nav className="flex-1 overflow-y-auto px-4 py-4">
          <div className="mb-2 px-3 text-[11px] font-bold tracking-wider text-ink-400 uppercase">
            Management
          </div>
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.end}
                  onClick={() => setNavOpen(false)}
                  className={({ isActive }) =>
                    `relative flex items-center gap-3 rounded-lg py-2.5 pr-3 pl-3.5 text-sm font-semibold transition-all
                     focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-navy-600 ${
                       isActive
                         ? "bg-navy-700 text-white shadow-sm"
                         : "text-ink-600 hover:bg-ink-50 hover:text-navy-800"
                     }`
                  }
                >
                  <svg
                    aria-hidden="true"
                    className="h-5 w-5 shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.8}
                  >
                    {item.icon}
                  </svg>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* User profile & system summary */}
        <div className="border-t border-ink-200 bg-ink-50/60 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-navy-700 text-sm font-bold text-gold-400 shadow-sm border border-navy-800">
              TC
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-bold text-ink-900">Tharun Chandran</p>
              <p className="truncate text-[11px] text-ink-500">admin@nibm.lk</p>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top bar header */}
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-ink-200 bg-white/95 px-6 backdrop-blur-sm lg:px-10">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setNavOpen(true)}
              aria-label="Open navigation"
              aria-expanded={navOpen}
              aria-controls="main-nav"
              className="btn-secondary px-2.5 py-2 lg:hidden"
            >
              <svg
                aria-hidden="true"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="hidden sm:block">
              <span className="text-xs font-semibold text-ink-500">Workspace / </span>
              <span className="text-xs font-bold text-navy-800">Media Club Committee</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="http://localhost:8081"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 rounded-lg border border-navy-200 bg-navy-50 px-3 py-1.5 text-xs font-bold text-navy-700 transition hover:bg-navy-100"
              title="Open Student Flutter App in a new tab"
            >
              <svg className="h-3.5 w-3.5 text-navy-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Student App (8081)
            </a>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1240px] flex-1 px-4 py-6 lg:px-10 lg:py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
