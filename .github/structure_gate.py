#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公开仓结构门（只依赖本仓 SKILL.md / README.md，不引入开发包资产）。

检查 6 项：
  1) frontmatter 合法，且 name 必须为 young-renter-assistant
  2) 代码围栏（```）成对闭合
  3) 无 CRLF 行尾（公开版约定 LF-only）
  4) README 的「附录 B」存在
  5) SKILL 的版本锚点（"当前版本：**X**"）存在
  6) 表格分隔行列数与表头一致（防 Markdown 表格结构损坏）

用法：python .github/structure_gate.py [--root <仓库根>]
退出码：0 通过，1 未通过。
"""
import argparse
import re
import sys
from pathlib import Path

failures = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"[FAIL] {msg}")


def check_file(p: Path) -> str:
    if not p.is_file():
        fail(f"{p.name}: 文件不存在")
        return ""
    text = p.read_text(encoding="utf-8")
    # 3) 无 CRLF
    if "\r" in text:
        fail(f"{p.name}: 含 CRLF（约定 LF-only）")
    # 2) 代码围栏成对
    fences = [ln for ln in text.splitlines() if ln.startswith("```")]
    if len(fences) % 2 != 0:
        fail(f"{p.name}: 代码围栏不成对（{len(fences)} 处）")
    # 6) 表格分隔行列数一致
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"^\s*\|[-: ]+\|\s*$", ln) and i > 0:
            if lines[i - 1].count("|") != ln.count("|"):
                fail(f"{p.name}: 表格分隔行列数与表头不一致（行 {i + 1}）")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    skill = check_file(root / "SKILL.md")
    readme = check_file(root / "README.md")

    # 1) frontmatter
    if skill:
        if not skill.startswith("---"):
            fail("SKILL.md: 缺少 frontmatter（须以 --- 开头）")
        else:
            end = skill.find("\n---", 3)
            fm = skill[3:end] if end != -1 else ""
            if "name: young-renter-assistant" not in fm:
                fail("SKILL.md: frontmatter 中 name 不是 young-renter-assistant")

    # 5) SKILL 版本锚点
    if skill and not re.search(r"当前版本：\*\*[0-9][0-9.]*\*\*", skill):
        fail("SKILL.md: 缺少『当前版本：**X**』版本锚点")

    # 4) README 附录 B
    if readme and "## 附录 B" not in readme:
        fail("README.md: 缺少『附录 B』")

    if failures:
        print(f"== 结构门未通过：{len(failures)} 项 ==")
        return 1
    print("== 结构门通过（6 项）==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
