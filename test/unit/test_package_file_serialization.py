from pathlib import Path

from exasol.exaslpm.model.package_file_config import Phase, Tools, RPackages, RPackage, AptRepo, AptPackage, \
    AptPackages, BuildStep, CondaBinary, CondaPackage, CondaPackages, Micromamba, PipPackage, PipPackages, Pip, \
    PackageFile
from pydantic import HttpUrl

from exasol.slc.internal.tasks.build.docker_flavor_image_task import package_model_to_yaml_str

def make_package_file() -> PackageFile:
    return PackageFile(
    build_steps=[
        BuildStep(
            name="base_deps",
            phases=[
                Phase(
                    name="phase_base_apt",
                    apt=AptPackages(
                        packages=[
                            AptPackage(name="locales", version="2.39-0ubuntu8.7"),
                            AptPackage(name="ca-certificates", version="20240203"),
                            AptPackage(name="bzip2", version="1.0.8-5.1build0.1"),
                            AptPackage(name="gpg", version="2.4.4-2ubuntu17.4"),
                            AptPackage(name="git", version="1:2.43.0-1ubuntu7.3"),
                        ],
                        repos={
                            "trivy": AptRepo(
                                key_url=HttpUrl(
                                    "https://aquasecurity.github.io/trivy-repo/deb/public.key"
                                ),
                                entry="deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main",
                                out_file="trivy.list",
                            )
                        },
                    ),
                ),
            ],
        ),
        BuildStep(
            name="python_pip",
            phases=[
                Phase(
                    name="python",
                    apt=AptPackages(
                        packages=[
                            AptPackage(
                                name="python3.12-dev", version="3.12.3-1ubuntu0.11"
                            ),
                        ]
                    ),
                ),
                Phase(
                    name="phase_python_binary",
                    tools=Tools(python_binary_path=Path("/usr/bin/python3.12")),
                ),
                Phase(
                    name="pip",
                    tools=Tools(
                        pip=Pip(version="25.3", needs_break_system_packages=True),
                    ),
                ),
                Phase(
                    name="pip_packages",
                    pip=PipPackages(
                        packages=[
                            PipPackage(name="jinja2", version=" >=3.1.6, <4.0.0"),
                            PipPackage(
                                name="exasol-db-api",
                                url="git+https://github.com/EXASOL/websocket-api.git@91bd9a7970941c578f246c07f2645699fc491d6c#egg=exasol-db-api&subdirectory=python",
                            ),
                        ]
                    ),
                ),
            ],
        ),
        BuildStep(
            name="conda",
            phases=[
                Phase(
                    name="micromamba",
                    tools=Tools(micromamba=Micromamba(version="2.5.0-1")),
                ),
                Phase(
                    name="conda_package_mamba",
                    conda=CondaPackages(
                        packages=[CondaPackage(name="mamba", version="=2.3.*")],
                        binary=CondaBinary.Micromamba,
                        channels={"conda-forge", "nvidia", "some_other_channel"},
                    ),
                ),
                Phase(
                    name="mamba",
                    tools=Tools(mamba_binary_path=Path("/opt/conda/bin/mamba")),
                ),
                Phase(
                    name="conda_package_conda",
                    conda=CondaPackages(
                        packages=[CondaPackage(name="conda", version="=26.1.*")],
                        binary=CondaBinary.Mamba,
                    ),
                ),
                Phase(
                    name="conda",
                    tools=Tools(conda_binary_path=Path("/opt/conda/bin/conda")),
                ),
                Phase(
                    name="conda_packages",
                    conda=CondaPackages(
                        packages=[
                            CondaPackage(
                                name="numpy",
                                version=">=2.3.0,<3",
                                channel="main",
                                build="py314*",
                            ),
                            CondaPackage(name="pydantic", version="=2.*"),
                        ],
                        binary=CondaBinary.Conda,
                    ),
                ),
            ],
        ),
        BuildStep(
            name="R",
            phases=[
                Phase(
                    name="R apt repo",
                    apt=AptPackages(
                        packages=[
                            AptPackage(name="r-base-core", version="4.5.2-1.2404.0"),
                            AptPackage(name="build-essential", version="12.10ubuntu1"),
                        ],
                        repos={
                            "cran-r": AptRepo(
                                key_url=HttpUrl(
                                    "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xE298A3A825C0D65DFD57CBB651716619E084DAB9"
                                ),
                                entry="deb [signed-by=/usr/share/keyrings/cran-r.gpg] https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/",
                                out_file="noble-cran40.list",
                            )
                        },
                    ),
                ),
                Phase(
                    name="R binary",
                    tools=Tools(r_binary_path=Path("/usr/bin/Rscript")),
                ),
                Phase(
                    name="R packages",
                    r=RPackages(packages=[RPackage(name="dplyr", version="1.2.0")]),
                ),
                Phase(name="Variables", variables={"PROTOBUF": "something"}),
            ],
        ),
    ]
)


def test_package_file_serialization():
    package_file_yaml_str = package_model_to_yaml_str(make_package_file())
    for i  in range(100):
        new_package_file_yaml_str = package_model_to_yaml_str(make_package_file())
        assert new_package_file_yaml_str == package_file_yaml_str
