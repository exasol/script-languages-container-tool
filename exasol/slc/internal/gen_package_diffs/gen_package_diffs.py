from pathlib import Path
from typing import Any

import yaml


def _normalize_build_steps(raw_data: Any) -> dict[str, Any]:
    if raw_data is None:
        return {}
    if isinstance(raw_data, dict):
        return {str(name): value for name, value in raw_data.items()}
    if isinstance(raw_data, list):
        result: dict[str, Any] = {}
        for index, item in enumerate(raw_data, start=1):
            if isinstance(item, dict):
                if "build_step" in item:
                    step_name = str(item["build_step"])
                    step_value = {k: v for k, v in item.items() if k != "build_step"}
                elif "name" in item:
                    step_name = str(item["name"])
                    step_value = {k: v for k, v in item.items() if k != "name"}
                elif len(item) == 1:
                    step_name, step_value = next(iter(item.items()))
                    step_name = str(step_name)
                else:
                    step_name = f"build_step_{index}"
                    step_value = item
            else:
                step_name = f"build_step_{index}"
                step_value = item
            result[step_name] = step_value
        return result
    raise ValueError(f"Unsupported packages.yml format: {type(raw_data)}")


def _load_packages_file(packages_file: Path) -> dict[str, Any]:
    if not packages_file.is_file():
        return {}
    with packages_file.open("rt", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return _normalize_build_steps(data)


def _generate_packages_report(flavor_name: str, scope_name: str, build_steps: dict[str, Any]) -> str:
    title = f"# {scope_name} packages for flavor {flavor_name}\n\n"
    if not build_steps:
        return title + "No build steps found.\n"

    sections = []
    for build_step_name in sorted(build_steps):
        build_step_payload = yaml.safe_dump(
            build_steps[build_step_name], sort_keys=False
        ).strip()
        sections.append(
            f"## {build_step_name}\n\n"
            f"```yaml\n{build_step_payload}\n```\n"
        )
    return title + "\n".join(sections)


def _generate_reports_for_flavor(flavor_path: Path, output_flavor_path: Path):
    flavor_name = flavor_path.name
    output_flavor_path.mkdir(parents=True, exist_ok=True)

    public_build_steps = _load_packages_file(flavor_path / "packages.yml")
    internal_build_steps = _load_packages_file(flavor_path / "flavor_base" / "packages.yml")

    (output_flavor_path / "public_packages.md").write_text(
        _generate_packages_report(flavor_name, "Public", public_build_steps),
        encoding="utf-8",
    )
    (output_flavor_path / "internal_packages.md").write_text(
        _generate_packages_report(flavor_name, "Internal", internal_build_steps),
        encoding="utf-8",
    )


def gen_package_diffs(
    output_directory: str,
    current_working_copy_name: str,
    compare_to_commit: str | None,
):
    del current_working_copy_name
    del compare_to_commit

    working_copy_root = Path(".")
    output_root = Path(output_directory)
    output_root.mkdir(parents=True, exist_ok=True)

    overview_content = "# Package files\n\n"
    for flavor_path in sorted((working_copy_root / "flavors").iterdir()):
        if not flavor_path.is_dir():
            continue
        _generate_reports_for_flavor(flavor_path, output_root / flavor_path.name)
        overview_content += (
            f"- {flavor_path.name}\n"
            f"  - [public packages]({flavor_path.name}/public_packages.md)\n"
            f"  - [internal packages]({flavor_path.name}/internal_packages.md)\n"
        )

    (output_root / "README.md").write_text(overview_content, encoding="utf-8")
