# 生成课程 PPT 指南

本项目提供一个小工具，将 `docs/syllabus.yaml` 中的章节/课程结构自动渲染为 PPTX 幻灯片骨架，便于授课与分享。

## 安装依赖

建议使用虚拟环境：

```bash
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell
# 或
python3 -m venv .venv && source .venv/bin/activate # macOS/Linux

pip install -r tools/requirements-slides.txt
```

## 快速生成

- 生成每一讲一份 PPT：

```bash
python tools/build_ppt.py
```

- 仅生成第 1 章：

```bash
python tools/build_ppt.py --chapter 1
```

- 生成“按章节分组”的摘要版 PPT（每章 1 份）：

```bash
python tools/build_ppt.py --grouping chapter
```

- 仅生成指定几讲：

```bash
python tools/build_ppt.py --filter 1 3 15.1
```

生成结果默认输出到 `slides/` 目录。

## 自定义内容

- 修改 `docs/syllabus.yaml` 中的每讲 `topics` 与 `code` 列表即可调整对应幻灯片的“学习目标/核心概念/Notebook”。
- 如需更换风格，可在 `tools/build_ppt.py` 中替换布局或添加主题文件。

## 建议的授课结构（每讲）

1. 标题与章节说明
2. 学习目标（3 条内）
3. 核心概念（3 条内）
4. 实操与 Notebook 对应关系
5. 实验建议（可在课上调整）
6. 小结与下一讲

> 本工具生成的是高质量骨架，建议讲师在生成的 PPT 基础上按需补充案例截图、性能图表与注意事项。

