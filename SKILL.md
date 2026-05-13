---
name: zju-thesis-writer
description: Generate a rigorous Chinese Zhejiang University thesis from all research materials in the current directory using the bundled zjuthesis LaTeX template. Use when Codex is asked to read PDFs, Word files, images, LaTeX, datasets, code repositories, Git project history, or mixed local files and produce a thesis draft, thesis LaTeX source, bibliography, appendices, and compiled PDF when possible, while preserving the zjuthesis template format.
---

# ZJU Thesis Writer

## Bundled Files

This skill is self-contained:

- `template/` contains the Zhejiang University `zjuthesis` LaTeX template, including `zjuthesis.tex`, `zjuthesis.cls`, body/page/config files, figures, logos, and fonts.
- `scripts/` contains inventory, extraction, workspace preparation, and compilation helpers.

When the current working directory already contains `zjuthesis.tex` and `zjuthesis.cls`, use that local template. Otherwise, prepare the generated thesis workspace from the bundled `template/` directory.

## Provenance and License Boundaries

Preserve upstream attribution when copying, modifying, or publishing generated workspaces:

- The bundled `template/` is based on the Zhejiang University `zjuthesis` LaTeX template.
- Upstream repository: <https://github.com/TheNetAdmin/zjuthesis>
- Project site: <https://thenetadmin.github.io/zjuthesis>
- Upstream copyright: Zixuan Wang and Contributors.
- Upstream template license: MIT License, preserved in `template/LICENSE`.
- Zhejiang University marks, rules, and school documents remain owned by Zhejiang University or the relevant rights holders.
- Files in `template/fonts/` are third-party font assets included under separate authorization confirmed by the repository maintainer. Do not treat them as MIT-licensed template code.

## Output Contract

Create a Zhejiang University thesis draft from local evidence and the bundled or local `zjuthesis` template. Default output goes to `generated-thesis/` in the working directory.

Deliver:

- `generated-thesis/zjuthesis.tex` and the copied template workspace.
- Updated body/page/ref files in the generated workspace only.
- `generated-thesis/thesis_sources.md` with the source inventory, extraction notes, and unresolved gaps.
- `generated-thesis/out/*.pdf` when compilation succeeds.
- `generated-thesis/compile.log` and `generated-thesis/compile_errors.md` when compilation fails.

Do not overwrite the original template files unless the user explicitly asks.

## Evidence Rules

- Write evidence-first. Do not fabricate experimental results, datasets, references, theorem statements, author claims, or code behavior.
- Use `TODO:` or `待补充` for missing personal information, unavailable data, unverified results, and unclear conclusions.
- Cite only materials found in the working directory unless the user explicitly authorizes web research.
- Mark uncertain interpretations as such, or omit them.
- Treat images as visual evidence only when their content is clear from filename, metadata, adjacent text, or user-provided context.

## Workflow

Resolve bundled script paths relative to this skill directory. If the shell is in the thesis material directory, use absolute paths to this skill's `scripts/` directory.

1. Confirm the intended working directory contains the user's thesis evidence or project materials. It does not need to contain the `zjuthesis` template because this skill bundles it.
2. Prepare the template workspace:
   ```bash
   python3 /path/to/zju-thesis-writer/scripts/prepare_zjuthesis_workspace.py . --output generated-thesis --force
   ```
   Use `--template-root /path/to/custom/zjuthesis` only when the user explicitly wants a different template.
3. Inventory sources:
   ```bash
   python3 /path/to/zju-thesis-writer/scripts/inventory_sources.py . --output generated-thesis/source_inventory.json
   ```
4. Extract source evidence:
   ```bash
   python3 /path/to/zju-thesis-writer/scripts/extract_sources.py . --inventory generated-thesis/source_inventory.json --output generated-thesis/thesis_sources.md --json-output generated-thesis/thesis_sources.json
   ```
5. Read `generated-thesis/thesis_sources.md` and draft an outline before writing thesis content.
6. Edit only the generated workspace. Preserve `zjuthesis.cls`, page structure, fonts, cover flow, abstract flow, table of contents, bibliography, and appendix mechanism.
7. Write the thesis using the template's existing configuration:
   - Undergraduate final: write `body/undergraduate/final/content.tex`, `body/undergraduate/final/abstract.tex`, and related final files.
   - Graduate Chinese: write `body/graduate/content.tex`, `page/graduate/abstract.tex`, `body/graduate/post/ref.tex`, and appendix/CV files as needed.
   - Graduate English: write the matching `graduate-eng` body/page files.
8. Compile from `generated-thesis/`:
   ```bash
   bash /path/to/zju-thesis-writer/scripts/compile_zjuthesis.sh generated-thesis
   ```

## Thesis Structure

Use this default structure unless the source materials strongly imply another structure:

- 绪论: research background, problem, contributions, thesis organization.
- 相关工作: local papers, notes, and code/documentation evidence.
- 材料与方法 or 系统设计: data, model, algorithm, architecture, or implementation.
- 实验或案例分析: only source-grounded datasets, settings, metrics, and observations.
- 结果与讨论: verified findings, limitations, threats to validity.
- 总结与展望: source-grounded conclusions and future work.

For code projects, summarize purpose, architecture, main modules, interfaces, algorithms, examples, tests, reproducibility steps, and limitations. Include code listings only when code itself is central evidence.

## Template Requirements

- Respect the existing `zjuthesis.tex` options: `Degree`, `Type`, `Period`, `GradLevel`, `MajorFormat`, `Language`, and blind review settings.
- Keep user identity fields as TODO placeholders if unavailable.
- Use `figure/` paths and LaTeX labels consistently.
- Use `body/ref.bib` for BibLaTeX entries. Partial bibliography metadata is acceptable; invented metadata is not.
- If the thesis cannot compile, still deliver the LaTeX source and explain the first actionable compiler problem.

## Script Notes

The bundled scripts are aids, not replacements for judgment:

- `inventory_sources.py` scans source files and Git summary while excluding generated/build/cache directories.
- `extract_sources.py` extracts bounded text and metadata from supported files. Missing optional libraries are reported in the output.
- `prepare_zjuthesis_workspace.py` copies a local template when present; otherwise it copies the bundled `template/`.
- `compile_zjuthesis.sh` tries POSIX `latexmk` first, then Windows MiKTeX `latexmk.exe` and `xelatex.exe` through `cmd.exe`/PowerShell with WSL path conversion.
