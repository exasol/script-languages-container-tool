import importlib
import inspect
import sys
from pathlib import Path

from exasol.slc.internal.tasks.build.docker_flavor_image_task import (
    DockerFlavorAnalyzeImageTask,
)


def _load_build_steps_module(build_steps_path: Path):
    spec = importlib.util.spec_from_file_location("build_steps", build_steps_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_steps"] = module
    spec.loader.exec_module(module)
    return module


def _collect_build_step_classes(module) -> list[type]:
    return [
        obj
        for obj in vars(module).values()
        if inspect.isclass(obj)
        and issubclass(obj, DockerFlavorAnalyzeImageTask)
        and obj is not DockerFlavorAnalyzeImageTask
    ]


def _build_dependency_edges(
    build_step_classes: list[type],
) -> tuple[list[str], list[tuple[str, str]]]:
    nodes: list[str] = []
    edges: list[tuple[str, str]] = []
    for cls in build_step_classes:
        step_name = cls.get_build_step(cls)
        nodes.append(step_name)
    for cls in build_step_classes:
        step_name = cls.get_build_step(cls)
        requires = cls.requires_tasks(cls)
        if requires:
            for dep_name in requires:
                edges.append((dep_name, step_name))
    return nodes, edges


def generate_dot(flavor_path: str, output_path: str | None = None) -> str:
    """
    Generate a .dot dependency graph from a flavor's build_steps.py.

    :param flavor_path: Path to the flavor directory.
    :param output_path: Optional path where to write the .dot file.
        Defaults to <flavor_path>/build_steps.dot.
    :return: The .dot file content as a string.
    """
    flavor_dir = Path(flavor_path)
    build_steps_path = flavor_dir / "flavor_base" / "build_steps.py"
    if not build_steps_path.exists():
        raise FileNotFoundError(
            f"build_steps.py not found at {build_steps_path}"
        )

    module = _load_build_steps_module(build_steps_path)
    build_step_classes = _collect_build_step_classes(module)
    nodes, edges = _build_dependency_edges(build_step_classes)

    lines = ["strict digraph {"]
    for node in nodes:
        lines.append(f'"{node}" [label="{node}"];')
    for source, target in edges:
        lines.append(f'"{source}" -> "{target}";')
    lines.append("}")
    dot_content = "\n".join(lines) + "\n"

    if output_path is None:
        output_path = str(flavor_dir / "build_steps.dot")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(dot_content, encoding="utf-8")

    return dot_content
