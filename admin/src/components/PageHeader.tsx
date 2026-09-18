import type { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-200 pb-5">
      <div className="min-w-0">
        <h1 className="text-2xl font-bold text-ink-900 sm:text-3xl">{title}</h1>
        {description ? (
          <p className="mt-1 max-w-[60ch] text-sm text-ink-600">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
    </header>
  );
}
