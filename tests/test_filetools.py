"""Test module for `filetools`."""

from pathlib import Path

from holiday_cn.filetools import workspace_path, dataspace_path


class TestWorkspacePath:
    """Tests for workspace_path function."""

    def test_workspace_path_returns_path(self):
        result = workspace_path()
        assert isinstance(result, Path)

    def test_workspace_path_is_absolute(self):
        result = workspace_path()
        assert result.is_absolute()

    def test_workspace_path_with_args(self):
        result = workspace_path("foo", "bar")
        assert result.name == "bar"
        assert result.parent.name == "foo"

    def test_workspace_path_contains_project(self):
        """Workspace should be the project root."""
        result = workspace_path()
        # 项目根目录应该包含 pyproject.toml
        assert (result / "pyproject.toml").exists()


class TestDataspacePath:
    """Tests for dataspace_path function."""

    def test_dataspace_path_returns_path(self):
        result = dataspace_path()
        assert isinstance(result, Path)

    def test_dataspace_path_is_absolute(self):
        result = dataspace_path()
        assert result.is_absolute()

    def test_dataspace_path_ends_with_data(self):
        result = dataspace_path()
        assert result.name == "data"

    def test_dataspace_path_with_args(self):
        result = dataspace_path("2024.json")
        assert result.name == "2024.json"
        assert result.parent.name == "data"

    def test_dataspace_path_is_subdir_of_workspace(self):
        workspace = workspace_path()
        dataspace = dataspace_path()
        assert dataspace.parent == workspace
