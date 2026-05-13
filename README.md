# zju-thesis-writer

一个 Codex skill，用于读取当前目录中的论文材料、项目文件、代码和文档，并基于浙江大学 `zjuthesis` LaTeX 模板生成学位论文草稿工作区。

## 内容

- `SKILL.md`: Codex skill 的触发描述与工作流程。
- `scripts/`: 资料清单、证据抽取、模板工作区准备和编译辅助脚本。
- `template/`: 随 skill 打包的 `zjuthesis` 模板文件。
- `agents/openai.yaml`: Codex UI 元数据。

## 上游模板来源

本仓库内 `template/` 目录基于浙江大学学位论文 LaTeX 模板 `zjuthesis`：

- 原仓库: <https://github.com/TheNetAdmin/zjuthesis>
- 项目主页: <https://thenetadmin.github.io/zjuthesis>
- 原作者/版权声明: Zixuan Wang and Contributors
- 上游模板许可: MIT License，见 `template/LICENSE`

请勿移除上游作者、原仓库链接和许可文件。

## 字体与学校标志

`template/fonts/` 中的字体文件由本仓库维护者确认具有上传与再分发授权后打包提供。这些字体文件不属于 `zjuthesis` 模板的 MIT 许可范围；字体的使用、复制、再分发仍受其各自授权条款约束。

`template/figure/` 中涉及浙江大学标志、规则文件或学校视觉元素的内容，其权利归属浙江大学或相应权利人。请仅在合规场景下使用。

## 使用方式

把本仓库作为 Codex skill 安装或放入 Codex 可发现的 skills 目录后，在论文材料目录中请求 Codex 使用 `$zju-thesis-writer`：

```text
Use $zju-thesis-writer to read this directory and generate a Zhejiang University thesis draft.
```

默认输出写入当前工作目录的 `generated-thesis/`，不会覆盖原始模板或原始材料。

## 合规提醒

此 skill 只根据本地材料写作，不应编造实验结果、数据、引用、作者结论或代码行为。生成论文前请确认你有权使用输入材料、模板、学校标志、图片和字体。
