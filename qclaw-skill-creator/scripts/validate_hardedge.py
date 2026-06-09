#!/usr/bin/env python3
"""
validate_hardedge.py — 四硬核工程原则合规校验

校验 Anthropic "Agent Skills" 的 4 条原则是否在 SKILL.md 中落实：
  ① 描述=路由器：description 三要素（触发场景 + 关键动词 + 反例边界）
  ② 渐进式披露：L2 ≤ 200 行 + 互斥场景拆文件 + 引用完整性
  ③ 从缺口出发：metadata/run_log/task_history 等落地证据
  ④ 代码兜底：scripts/ 下每个脚本标注了 run 或 read

Usage:
    python validate_hardedge.py <skill_directory>
    python validate_hardedge.py <skill_directory> --strict  (warn 升级为 error)

Exit code: 0 = pass, 1 = fail

依赖: pyyaml (pip install pyyaml)
"""

import re
import sys
from pathlib import Path

# ========== 配置 ==========
L2_LINE_LIMIT = 200          # 原则② 红线
MIN_DESC_ACTION_VERBS = 1    # 原则① 最少动作动词数
MIN_DESC_TRIGGER_PATTERNS = 1
MIN_DESC_NEGATIVE_PATTERNS = 1

# 动作动词
ACTION_VERBS = [
    'sort', 'filter', 'aggregate', 'convert', 'merge', 'split',
    'extract', 'parse', 'generate', 'create', 'validate', 'transform',
    'search', 'query', 'fetch', 'download', 'upload', 'sync',
    'fill', 'sign', 'edit', 'format', 'render', 'plot', 'chart',
    'classify', 'detect', 'match', 'translate', 'summarize',
]

# 触发场景关键词
TRIGGER_PATTERNS = [
    r'when\s', r'if\s', r'for\s',
    r'user\s+(ask|want|need|request|upload|provide|submit|send)',
    r'input', r'file', r'data',
    r'csv', r'json', r'pdf', r'docx', r'xlsx', r'image',
    r'scenario', r'case', r'task',
]

# 反例边界关键词
NEGATIVE_PATTERNS = [
    r'\bnot\b', r'\bnot for\b', r'\bnot when\b',
    r'\binstead\b', r'\bavoid\b', r'\bforbidden\b',
    r"\bdon'?t\b", r'\bdo not\b', r"won'?t",
]

# 缺口证据关键词
GAP_EVIDENCE_PATTERNS = [
    r'example task',
    r'task[\s_-]?(history|log|record)',
    r'real[\s_-]?(world|task|scenario|case)',
    r'gap analy',
    r'failure',
    r'struggled?',
    r'generated?\s+(with|from)\s+.*?task',
    r'built?\s+(from|after|based\s+on)',
    r'\d+\s*(task|run|execution|attempt)',
    r'run_log',
]


class HardedgeIssue:
    """A single compliance issue found."""
    def __init__(self, rule: str, severity: str, message: str):
        self.rule = rule        # e.g. "①-描述"
        self.severity = severity  # "ERROR" or "WARN"
        self.message = message

    def __str__(self):
        return f"[{self.severity}] {self.rule}: {self.message}"


def check_description_heuristic(description: str) -> list[HardedgeIssue]:
    """
    原则①：描述 = 路由器
    启发式检查三要素：触发场景 + 关键动词 + 反例边界
    """
    issues = []
    desc_lower = description.lower()

    # 要素1：动作性动词
    found_verbs = [v for v in ACTION_VERBS if v in desc_lower]
    if len(found_verbs) < MIN_DESC_ACTION_VERBS:
        issues.append(HardedgeIssue(
            "①-描述", "WARN",
            f"未检测到动作性动词（建议用 sort/convert/validate 等）。"
            f"已检出: {found_verbs[:3] if found_verbs else '无'}"
        ))

    # 要素2：触发场景
    trigger_hits = sum(1 for p in TRIGGER_PATTERNS if re.search(p, desc_lower))
    if trigger_hits < MIN_DESC_TRIGGER_PATTERNS:
        issues.append(HardedgeIssue(
            "①-描述", "WARN",
            "未含触发场景关键词（建议加 when/user asks/input/task 等）"
        ))

    # 要素3：反例边界
    neg_hits = sum(1 for p in NEGATIVE_PATTERNS if re.search(p, desc_lower))
    if neg_hits < MIN_DESC_NEGATIVE_PATTERNS:
        issues.append(HardedgeIssue(
            "①-描述", "WARN",
            "未检出反例边界（建议加 NOT for / instead / avoid 语句）"
        ))

    return issues


def check_L2_linecount(skill_md: Path, content: str) -> list[HardedgeIssue]:
    """原则②：L2 主说明 ≤ 200 行"""
    issues = []
    body = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)
    body_lines = body.strip().split('\n')
    line_count = len(body_lines)
    if line_count > L2_LINE_LIMIT:
        issues.append(HardedgeIssue(
            "②-L2行数", "ERROR",
            f"SKILL.md 正文 {line_count} 行（红线 {L2_LINE_LIMIT} 行）。"
            f"超出 {line_count - L2_LINE_LIMIT} 行，建议拆至 references/"
        ))
    else:
        issues.append(HardedgeIssue(
            "②-L2行数", "INFO",
            f"SKILL.md 正文 {line_count} 行（≤{L2_LINE_LIMIT} ✓）"
        ))
    return issues


def check_cross_references(skill_path: Path) -> list[HardedgeIssue]:
    """原则②：SKILL.md 中引用的 .md 文件必须存在"""
    issues = []
    skill_md = skill_path / 'SKILL.md'
    content = skill_md.read_text(encoding='utf-8')
    body = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)

    # 提取 markdown 链接到 .md 文件
    links = re.findall(r'\]\(([^)]+\.md)\)', body)
    links += re.findall(r'src="([^"]+\.md)"', body)
    links += re.findall(r"href='([^']+\.md)'", body)

    missing = []
    for link in links:
        if link.startswith('http://') or link.startswith('https://'):
            continue
        target = (skill_path / link).resolve()
        if not target.exists():
            missing.append(link)

    if missing:
        issues.append(HardedgeIssue(
            "②-引用", "ERROR",
            f"引用了 {len(missing)} 个不存在的文件: {'; '.join(missing[:5])}"
            + ("..." if len(missing) > 5 else "")
        ))
    else:
        issues.append(HardedgeIssue("②-引用", "INFO", "所有引用文件存在 ✓"))
    return issues


def check_gap_evidence(skill_path: Path) -> list[HardedgeIssue]:
    """原则③：是否有从缺口出发的证据"""
    issues = []

    # 检查 SKILL.md 正文
    skill_md = skill_path / 'SKILL.md'
    md_content = skill_md.read_text(encoding='utf-8')
    md_lower = md_content.lower()

    has_gap = any(re.search(p, md_lower) for p in GAP_EVIDENCE_PATTERNS)

    # 检查 references/ 下的文件
    if not has_gap:
        refs_dir = skill_path / 'references'
        if refs_dir.exists():
            for f in refs_dir.rglob('*.md'):
                if f.is_file() and f.name != 'anthropic-hardedge-template.md':
                    try:
                        f_lower = f.read_text(encoding='utf-8').lower()
                        if any(re.search(p, f_lower) for p in GAP_EVIDENCE_PATTERNS):
                            has_gap = True
                            break
                    except Exception:
                        pass

    if not has_gap:
        issues.append(HardedgeIssue(
            "③-缺口", "WARN",
            "未检出 task history / example tasks / failure 等缺口证据。"
            "建议在 SKILL.md 或 references/ 中记录 3-5 个真实触发任务。"
        ))
    else:
        issues.append(HardedgeIssue("③-缺口", "INFO", "已检出缺口落地证据 ✓"))

    return issues


def check_script_annotations(skill_path: Path) -> list[HardedgeIssue]:
    """原则④：脚本必须标注是 run 还是 read"""
    issues = []
    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return [HardedgeIssue("④-脚本", "INFO", "无 scripts/ 目录，跳过检查")]

    scripts = list(scripts_dir.rglob('*.py')) + list(scripts_dir.rglob('*.sh'))
    if not scripts:
        return [HardedgeIssue("④-脚本", "INFO", "scripts/ 目录为空，跳过检查")]

    skill_md = skill_path / 'SKILL.md'
    md_content = skill_md.read_text(encoding='utf-8')

    unannotated = []
    for script in scripts:
        rel = str(script.relative_to(skill_path)).replace('\\', '/')
        name_escaped = re.escape(rel)

        run_pat = re.compile(rf'`(?:run|execute|调用)\s+{name_escaped}`', re.IGNORECASE)
        read_pat = re.compile(rf'`(?:read|参考|查看|引用)\s+{name_escaped}`', re.IGNORECASE)

        if not run_pat.search(md_content) and not read_pat.search(md_content):
            unannotated.append(rel)

    if unannotated:
        issues.append(HardedgeIssue(
            "④-脚本", "WARN",
            f"{len(unannotated)} 个脚本未在 SKILL.md 中标注 `run scripts/...` 或 `read scripts/...`: "
            + '; '.join(unannotated[:5])
        ))
    else:
        issues.append(HardedgeIssue("④-脚本", "INFO", "所有脚本已标注 ✓"))

    return issues


def validate_hardedge(skill_path_str: str, strict: bool = False) -> tuple[bool, list[HardedgeIssue]]:
    """运行所有四原则检查，返回 (pass, issues列表)"""
    skill_path = Path(skill_path_str).resolve()
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, [HardedgeIssue("GLOBAL", "ERROR", "SKILL.md 不存在")]
    if not skill_md.is_file():
        return False, [HardedgeIssue("GLOBAL", "ERROR", "SKILL.md 不是常规文件")]

    # 读取 content
    content = skill_md.read_text(encoding='utf-8')

    # 提取 description
    description_text = ''
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            import yaml
            fm = yaml.safe_load(match.group(1))
            if isinstance(fm, dict) and 'description' in fm:
                description_text = str(fm.get('description', ''))
        except ImportError:
            issues = [HardedgeIssue("GLOBAL", "ERROR", "缺少 pyyaml 依赖: pip install pyyaml")]
            return False, issues
        except yaml.YAMLError as e:
            issues = [HardedgeIssue("GLOBAL", "ERROR", f"frontmatter YAML 解析失败: {e}")]
            return False, issues

    all_issues: list[HardedgeIssue] = []

    # 原则①
    all_issues.extend(check_description_heuristic(description_text))

    # 原则②
    all_issues.extend(check_L2_linecount(skill_md, content))
    all_issues.extend(check_cross_references(skill_path))

    # 原则③
    all_issues.extend(check_gap_evidence(skill_path))

    # 原则④
    all_issues.extend(check_script_annotations(skill_path))

    # 判断结果
    errors = [i for i in all_issues if i.severity == "ERROR"]
    warnings = [i for i in all_issues if i.severity == "WARN"]
    info = [i for i in all_issues if i.severity == "INFO"]

    if strict:
        blocking = errors + warnings
    else:
        blocking = errors

    if blocking:
        return False, all_issues
    return True, all_issues


def print_results(issues: list[HardedgeIssue]):
    """格式化打印检查结果"""
    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARN"]
    info = [i for i in issues if i.severity == "INFO"]

    if info:
        print("\nℹ️  信息:")
        for i in info:
            print(f"     {i.message}")

    if warnings:
        print(f"\n⚠️  WARN ({len(warnings)}):")
        for w in warnings:
            print(f"     {w.message}")

    if errors:
        print(f"\n❌  ERROR ({len(errors)}):")
        for e in errors:
            print(f"     {e.message}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(1)

    strict = '--strict' in sys.argv
    skill_dir = [a for a in sys.argv[1:] if not a.startswith('--')][0]

    passed, issues = validate_hardedge(skill_dir, strict=strict)
    print_results(issues)

    if passed:
        print(f"\n✅ {len([i for i in issues if i.severity != 'INFO'])} 项检查，全部通过")
        sys.exit(0)
    else:
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARN"]
        blocking_count = len(errors) + (len(warnings) if strict else 0)
        print(f"\n❌ {blocking_count} 个阻断项未通过。请修复后重试。")
        sys.exit(1)


if __name__ == "__main__":
    main()
