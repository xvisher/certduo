/**
 * SimpleMarkdown – lightweight in-app markdown renderer.
 * Supports: ## / ### headings, **bold**, `code`, bullet lists,
 * numbered lists, horizontal rules, and tables.
 * No external dependencies required.
 */

import React from "react";

function parseLine(text: string): React.ReactNode[] {
  // Split on **bold**, `code`, and plain text
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*.*?\*\*|`[^`]+`)/g;
  let last = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      parts.push(text.slice(last, match.index));
    }
    const raw = match[0];
    if (raw.startsWith("**")) {
      parts.push(<strong key={match.index}>{raw.slice(2, -2)}</strong>);
    } else if (raw.startsWith("`")) {
      parts.push(
        <code
          key={match.index}
          className="bg-gray-100 text-[#0078D4] px-1 py-0.5 rounded text-sm font-mono"
        >
          {raw.slice(1, -1)}
        </code>
      );
    }
    last = match.index + raw.length;
  }
  if (last < text.length) {
    parts.push(text.slice(last));
  }
  return parts;
}

interface TableRow {
  cells: string[];
  isHeader: boolean;
}

function parseTable(lines: string[]): React.ReactNode {
  const rows: TableRow[] = [];
  lines.forEach((line, i) => {
    if (/^\|[-\s|]+\|$/.test(line.trim())) return; // separator row
    const cells = line
      .trim()
      .replace(/^\||\|$/g, "")
      .split("|")
      .map((c) => c.trim());
    rows.push({ cells, isHeader: i === 0 });
  });
  if (rows.length === 0) return null;
  return (
    <div className="overflow-x-auto my-4">
      <table className="min-w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-50">
            {rows[0].cells.map((cell, i) => (
              <th
                key={i}
                className="border border-gray-200 px-3 py-2 text-left font-semibold text-gray-700"
              >
                {parseLine(cell)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(1).map((row, ri) => (
            <tr key={ri} className={ri % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              {row.cells.map((cell, ci) => (
                <td
                  key={ci}
                  className="border border-gray-200 px-3 py-2 text-gray-600"
                >
                  {parseLine(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SimpleMarkdown({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Heading 2
    if (line.startsWith("## ")) {
      elements.push(
        <h2
          key={i}
          className="text-xl font-bold text-gray-900 mt-6 mb-2 pb-1 border-b border-gray-100"
        >
          {parseLine(line.slice(3))}
        </h2>
      );
      i++;
      continue;
    }

    // Heading 3
    if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="text-base font-semibold text-gray-800 mt-4 mb-1">
          {parseLine(line.slice(4))}
        </h3>
      );
      i++;
      continue;
    }

    // Horizontal rule
    if (/^---+$/.test(line.trim())) {
      elements.push(<hr key={i} className="my-4 border-gray-200" />);
      i++;
      continue;
    }

    // Table (lines starting with |)
    if (line.trimStart().startsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trimStart().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      elements.push(<React.Fragment key={`table-${i}`}>{parseTable(tableLines)}</React.Fragment>);
      continue;
    }

    // Code block
    if (line.startsWith("```")) {
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      elements.push(
        <pre
          key={`code-${i}`}
          className="bg-gray-900 text-green-300 rounded-xl p-4 my-3 overflow-x-auto text-sm font-mono leading-relaxed"
        >
          {codeLines.join("\n")}
        </pre>
      );
      continue;
    }

    // Bullet list
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const items: React.ReactNode[] = [];
      while (
        i < lines.length &&
        (lines[i].startsWith("- ") || lines[i].startsWith("* "))
      ) {
        items.push(
          <li key={i} className="flex gap-2 text-gray-600">
            <span className="text-[#0078D4] mt-0.5 shrink-0">•</span>
            <span>{parseLine(lines[i].slice(2))}</span>
          </li>
        );
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} className="space-y-1.5 my-3 ml-1">
          {items}
        </ul>
      );
      continue;
    }

    // Numbered list
    if (/^\d+\.\s/.test(line)) {
      const items: React.ReactNode[] = [];
      let num = 1;
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        const text = lines[i].replace(/^\d+\.\s/, "");
        items.push(
          <li key={i} className="flex gap-2 text-gray-600">
            <span className="text-[#0078D4] font-semibold shrink-0 w-5 text-right">
              {num}.
            </span>
            <span>{parseLine(text)}</span>
          </li>
        );
        i++;
        num++;
      }
      elements.push(
        <ol key={`ol-${i}`} className="space-y-1.5 my-3 ml-1">
          {items}
        </ol>
      );
      continue;
    }

    // Empty line
    if (line.trim() === "") {
      i++;
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={i} className="text-gray-600 leading-relaxed my-2">
        {parseLine(line)}
      </p>
    );
    i++;
  }

  return <div className="prose-content">{elements}</div>;
}
