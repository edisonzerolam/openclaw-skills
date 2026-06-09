#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-dir] [--skip-hardedge]

Example:
    python scripts/package_skill.py skills/public/my-skill
    python scripts/package_skill.py skills/public/my-skill ./dist
    python scripts/package_skill.py skills/public/my-skill --skip-hardedge
"""

import sys
import zipfile
from pathlib import Path

# Make sure we can find sibling modules
_this_dir = Path(__file__).resolve().parent
if str(_this_dir) not in sys.path:
    sys.path.insert(0, str(_this_dir))

from quick_validate import validate_skill
from validate_hardedge import validate_hardedge, print_results


def package_skill(skill_path, output_dir=None, skip_hardedge=False):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file
        skip_hardedge: Skip hardedge (4 principles) validation

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run quick validation before packaging
    print("🔍 Running structure validation...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Structure validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}")

    # Run hardedge validation (unless skipped)
    if not skip_hardedge:
        print("🔍 Running hardedge (4 principles) validation...")
        he_passed, he_issues = validate_hardedge(skill_path)
        print_results(he_issues)
        if not he_passed:
            errors = [i for i in he_issues if i.severity == "ERROR"]
            print(f"\n❌ Hardedge validation failed ({len(errors)} errors).")
            print("   Fix errors before packaging, or use --skip-hardedge to bypass.")
            return None
        print()
    else:
        print("⏭️  Skipped hardedge validation (--skip-hardedge)")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format, UTF-8 normalized paths)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(skill_path.rglob('*')):
                if file_path.is_file():
                    # Skip __pycache__ and .pyc files
                    if '__pycache__' in file_path.parts or file_path.suffix == '.pyc':
                        continue
                    arcname = file_path.relative_to(skill_path.parent)
                    # Use forward slashes for zip portability
                    zipf.write(file_path, arcname.as_posix())
                    print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Parse args
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    skill_path = args[0]
    output_dir = args[1] if len(args) > 1 else None
    skip_hardedge = '--skip-hardedge' in flags

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir, skip_hardedge=skip_hardedge)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
