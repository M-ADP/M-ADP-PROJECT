import pytest
from pydantic import ValidationError

from src.app.project.schemas import ProjectCreate, ProjectResourceUpdate


def test_project_create_accepts_memory_and_disk_boundaries() -> None:
    minimum = ProjectCreate(
        name="alpha",
        max_cpu=1.0,
        max_memory=0.5,
        max_disk=2.0,
    )
    maximum = ProjectCreate(
        name="beta",
        max_cpu=1.0,
        max_memory=1.0,
        max_disk=50.0,
    )

    assert minimum.max_memory == 0.5
    assert minimum.max_disk == 2.0
    assert maximum.max_memory == 1.0
    assert maximum.max_disk == 50.0


@pytest.mark.parametrize("max_memory", [0.49, 1.01])
def test_project_create_rejects_out_of_range_memory(max_memory: float) -> None:
    with pytest.raises(ValidationError):
        ProjectCreate(
            name="alpha",
            max_cpu=1.0,
            max_memory=max_memory,
            max_disk=2.0,
        )


@pytest.mark.parametrize("max_disk", [1.99, 50.01])
def test_project_create_rejects_out_of_range_disk(max_disk: float) -> None:
    with pytest.raises(ValidationError):
        ProjectCreate(
            name="alpha",
            max_cpu=1.0,
            max_memory=0.5,
            max_disk=max_disk,
        )


def test_project_resource_update_accepts_memory_and_disk_boundaries() -> None:
    minimum = ProjectResourceUpdate(max_memory=0.5, max_disk=2.0)
    maximum = ProjectResourceUpdate(max_memory=1.0, max_disk=50.0)

    assert minimum.max_memory == 0.5
    assert minimum.max_disk == 2.0
    assert maximum.max_memory == 1.0
    assert maximum.max_disk == 50.0


@pytest.mark.parametrize("max_memory", [0.49, 1.01])
def test_project_resource_update_rejects_out_of_range_memory(max_memory: float) -> None:
    with pytest.raises(ValidationError):
        ProjectResourceUpdate(max_memory=max_memory)


@pytest.mark.parametrize("max_disk", [1.99, 50.01])
def test_project_resource_update_rejects_out_of_range_disk(max_disk: float) -> None:
    with pytest.raises(ValidationError):
        ProjectResourceUpdate(max_disk=max_disk)
