import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest
import things
from anyio import BrokenResourceError


SRC_MAIN = Path(__file__).resolve().parents[1] / "src" / "main.py"


def load_main_module(module_name: str) -> object:
    spec = importlib.util.spec_from_file_location(module_name, SRC_MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def app_module(monkeypatch):
    monkeypatch.delenv("THINGS_DB_PATH", raising=False)
    database_instance = object()
    monkeypatch.setattr(things, "Database", Mock(return_value=database_instance))

    module = load_main_module("things_mcp_main_under_test")
    module._test_database_instance = database_instance
    return module


def test_app_registers_current_tools(app_module):
    tools = asyncio.run(app_module.app.list_tools())

    assert [tool.name for tool in tools] == ["things_list", "things_get"]
    assert asyncio.run(app_module.app.get_tool("things_list")) is not None
    assert asyncio.run(app_module.app.get_tool("things_get")) is not None


def test_import_uses_custom_things_database_path(monkeypatch):
    database_instance = object()
    database_ctor = Mock(return_value=database_instance)

    monkeypatch.setenv("THINGS_DB_PATH", "/tmp/things.sqlite")
    monkeypatch.setattr(things, "Database", database_ctor)

    module = load_main_module("things_mcp_main_with_custom_db")

    database_ctor.assert_called_once_with(filepath="/tmp/things.sqlite")
    assert module.THINGS_DATABASE is database_instance


def test_things_list_todos_passes_supported_filters(app_module, monkeypatch):
    todos = [{"uuid": "todo-1"}, {"uuid": "todo-2"}]
    todos_mock = Mock(return_value=todos)

    monkeypatch.setattr(app_module.things, "todos", todos_mock)

    result = app_module.things_list(
        app_module.ThingsEntityType.TODO,
        include_completed=True,
        include_canceled=True,
    )

    assert result == {"items": todos, "count": 2}
    todos_mock.assert_called_once_with(
        include_completed=True,
        include_canceled=True,
        database=app_module._test_database_instance,
    )


@pytest.mark.parametrize(
    ("entity_type", "api_name", "items"),
    [
        ("PROJECT", "projects", [{"uuid": "project-1"}]),
        ("AREA", "areas", [{"uuid": "area-1"}]),
        ("TAG", "tags", [{"uuid": "tag-1"}]),
    ],
)
def test_things_list_reads_non_todo_entities(app_module, monkeypatch, entity_type, api_name, items):
    api_mock = Mock(return_value=items)

    monkeypatch.setattr(app_module.things, api_name, api_mock)

    result = app_module.things_list(getattr(app_module.ThingsEntityType, entity_type))

    assert result == {"items": items, "count": 1}
    api_mock.assert_called_once_with(database=app_module._test_database_instance)


def test_things_get_returns_item(app_module, monkeypatch):
    item = {"uuid": "todo-1", "title": "Ship tests"}
    get_mock = Mock(return_value=item)

    monkeypatch.setattr(app_module.things, "get", get_mock)

    result = app_module.things_get("todo-1")

    assert result == {"item": item}
    get_mock.assert_called_once_with("todo-1", database=app_module._test_database_instance)


def test_things_get_raises_for_missing_item(app_module, monkeypatch):
    monkeypatch.setattr(app_module.things, "get", Mock(return_value=None))

    with pytest.raises(ValueError, match="Item with UUID missing-uuid not found"):
        app_module.things_get("missing-uuid")


def test_is_broken_resource_group_accepts_nested_broken_resource_errors(app_module):
    exc = ExceptionGroup(
        "shutdown",
        [
            BrokenResourceError(),
            ExceptionGroup("nested", [BrokenResourceError()]),
        ],
    )

    assert app_module._is_broken_resource_group(exc) is True


def test_is_broken_resource_group_rejects_other_exceptions(app_module):
    exc = ExceptionGroup("shutdown", [BrokenResourceError(), ValueError("boom")])

    assert app_module._is_broken_resource_group(exc) is False


def test_main_runs_stdio_transport(app_module, monkeypatch):
    run_mock = Mock()

    monkeypatch.setattr(app_module.app, "run", run_mock)

    app_module.main()

    run_mock.assert_called_once_with(transport="stdio")


def test_main_swallows_keyboard_interrupt(app_module, monkeypatch):
    monkeypatch.setattr(app_module.app, "run", Mock(side_effect=KeyboardInterrupt))

    app_module.main()


def test_main_swallows_broken_resource_exception_group(app_module, monkeypatch):
    monkeypatch.setattr(
        app_module.app,
        "run",
        Mock(side_effect=ExceptionGroup("shutdown", [BrokenResourceError()])),
    )

    app_module.main()


def test_main_reraises_other_exception_groups(app_module, monkeypatch):
    monkeypatch.setattr(
        app_module.app,
        "run",
        Mock(side_effect=ExceptionGroup("shutdown", [ValueError("boom")])),
    )

    with pytest.raises(ExceptionGroup):
        app_module.main()
