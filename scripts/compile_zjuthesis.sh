#!/usr/bin/env bash
set -u

WORKDIR="${1:-.}"
LOG_NAME="compile.log"
ERROR_NAME="compile_errors.md"

write_error_report() {
  local status="$1"
  local message="$2"
  local log_path="$WORKDIR/$LOG_NAME"
  local error_path="$WORKDIR/$ERROR_NAME"
  {
    printf '# Compile Errors\n\n'
    printf -- '- status: `%s`\n' "$status"
    printf -- '- message: %s\n\n' "$message"
    if [ -f "$log_path" ]; then
      printf '## First Actionable Lines\n\n'
      grep -a -n -E '(LaTeX Error|Package .* Error|Package biblatex Warning|Missing character|Font .* not found|not loadable|ERROR -|WARN -|Undefined control sequence|Emergency stop|Fatal error)' "$log_path" | head -40 || true
      printf '\n## Log Tail\n\n```text\n'
      tail -120 "$log_path" || true
      printf '\n```\n'
    fi
  } > "$error_path"
}

if [ ! -d "$WORKDIR" ]; then
  printf 'Workspace directory not found: %s\n' "$WORKDIR" >&2
  exit 2
fi

if [ ! -f "$WORKDIR/zjuthesis.tex" ]; then
  printf 'zjuthesis.tex not found in %s\n' "$WORKDIR" >&2
  exit 2
fi

mkdir -p "$WORKDIR/out"
rm -f "$WORKDIR/$LOG_NAME" "$WORKDIR/$ERROR_NAME"

if command -v latexmk >/dev/null 2>&1; then
  (
    cd "$WORKDIR" || exit 2
    latexmk -xelatex -interaction=nonstopmode -file-line-error -outdir=out zjuthesis.tex
  ) >"$WORKDIR/$LOG_NAME" 2>&1
  status=$?
  if [ "$status" -ne 0 ]; then
    write_error_report "$status" "POSIX latexmk failed. LaTeX sources are preserved."
    exit "$status"
  fi
  printf 'Compiled with POSIX latexmk. Log: %s\n' "$WORKDIR/$LOG_NAME"
  exit 0
fi

if ! command -v cmd.exe >/dev/null 2>&1; then
  write_error_report 127 "POSIX latexmk is unavailable, and cmd.exe is unavailable for Windows MiKTeX fallback."
  printf 'No POSIX latexmk or Windows cmd.exe fallback found.\n' >&2
  exit 127
fi

LATEXMK_WIN="$(cmd.exe /d /c where latexmk.exe 2>/dev/null | tr -d '\r' | head -n 1 || true)"
XELATEX_WIN="$(cmd.exe /d /c where xelatex.exe 2>/dev/null | tr -d '\r' | head -n 1 || true)"

if [ -z "$LATEXMK_WIN" ]; then
  write_error_report 127 "Windows MiKTeX latexmk.exe was not found on Windows PATH."
  printf 'latexmk.exe was not found on Windows PATH.\n' >&2
  exit 127
fi

if [ -z "$XELATEX_WIN" ]; then
  write_error_report 127 "Windows MiKTeX latexmk.exe was found, but xelatex.exe was not found on Windows PATH."
  printf 'xelatex.exe was not found on Windows PATH.\n' >&2
  exit 127
fi

if command -v wslpath >/dev/null 2>&1; then
  WIN_WORKDIR="$(wslpath -w "$(cd "$WORKDIR" && pwd)")"
else
  WIN_WORKDIR="$WORKDIR"
fi

PS_COMMAND="Set-Location -LiteralPath '$WIN_WORKDIR'; latexmk.exe -xelatex -interaction=nonstopmode -file-line-error -outdir=out zjuthesis.tex"
cmd.exe /d /c powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$PS_COMMAND" >"$WORKDIR/$LOG_NAME" 2>&1
status=$?
if [ "$status" -ne 0 ]; then
  write_error_report "$status" "Windows MiKTeX latexmk.exe failed. LaTeX sources are preserved."
  exit "$status"
fi

printf 'Compiled with Windows MiKTeX latexmk.exe. Log: %s\n' "$WORKDIR/$LOG_NAME"
