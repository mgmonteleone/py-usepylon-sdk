"""Integration tests for additional resources (teams, users, tasks, tags)."""

from typing import Any

import httpx
import pytest
import respx

from pylon import AsyncPylonClient, PylonClient


def make_team_data(
    team_id: str = "team_123", name: str = "Test Team", **overrides: Any
) -> dict[str, Any]:
    """Create valid team data for tests."""
    base_data = {
        "id": team_id,
        "name": name,
        "description": "Team description",
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


def make_user_data(
    user_id: str = "user_123", name: str = "Test User", **overrides: Any
) -> dict[str, Any]:
    """Create valid user data for tests."""
    base_data = {
        "id": user_id,
        "name": name,
        "email": "test@example.com",
        "status": "active",
        "role_id": "role_123",
        "emails": ["test@example.com"],
    }
    base_data.update(overrides)
    return base_data


def make_tag_data(
    tag_id: str = "tag_123", name: str = "Test Tag", **overrides: Any
) -> dict[str, Any]:
    """Create valid tag data for tests."""
    base_data = {
        "id": tag_id,
        "value": name,  # PylonTag uses 'value' not 'name'
        "object_type": "issue",
        "hex_color": "#FF0000",
    }
    base_data.update(overrides)
    return base_data


def make_task_data(
    task_id: str = "task_123", title: str = "Test Task", **overrides: Any
) -> dict[str, Any]:
    """Create valid task data for tests."""
    base_data = {
        "id": task_id,
        "title": title,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


def make_project_data(
    project_id: str = "project_123", name: str = "Test Project", **overrides: Any
) -> dict[str, Any]:
    """Create valid project data for tests."""
    base_data = {
        "id": project_id,
        "name": name,
        "description": "Project description",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


def make_audit_log_data(
    log_id: str = "log_123", action: str = "create", **overrides: Any
) -> dict[str, Any]:
    """Create valid audit log data for tests."""
    base_data = {
        "id": log_id,
        "action": action,
        "resource_type": "issue",
        "resource_id": "issue_123",
        "timestamp": "2024-01-01T00:00:00Z",
        "details": {},
    }
    base_data.update(overrides)
    return base_data


def make_attachment_data(
    att_id: str = "att_123", filename: str = "test.txt", **overrides: Any
) -> dict[str, Any]:
    """Create valid attachment data for tests."""
    base_data = {
        "id": att_id,
        "filename": filename,
        "url": "https://example.com/test.txt",
        "content_type": "text/plain",
        "size": 1024,
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


class TestTeamsResource:
    """Integration tests for teams resource."""

    @respx.mock
    def test_list_teams(self):
        """Should list all teams."""
        respx.get("https://api.usepylon.com/teams").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_team_data(team_id=f"team_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            teams = list(client.teams.list())
            assert len(teams) == 3

    @respx.mock
    def test_get_team(self):
        """Should get a specific team by ID."""
        respx.get("https://api.usepylon.com/teams/team_123").mock(
            return_value=httpx.Response(200, json={"data": make_team_data()})
        )

        with PylonClient(api_key="test-key") as client:
            team = client.teams.get("team_123")
            assert team.id == "team_123"
            assert team.name == "Test Team"

    @respx.mock
    def test_create_team(self):
        """Should create a new team."""
        respx.post("https://api.usepylon.com/teams").mock(
            return_value=httpx.Response(
                201, json={"data": make_team_data(team_id="new_team", name="New Team")}
            )
        )

        with PylonClient(api_key="test-key") as client:
            team = client.teams.create(name="New Team")
            assert team.id == "new_team"


class TestAsyncTeamsResource:
    """Integration tests for async teams resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_teams(self):
        """Should list teams asynchronously."""
        respx.get("https://api.usepylon.com/teams").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_team_data(team_id="async_team")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            teams = []
            async for team in client.teams.list():
                teams.append(team)
            assert len(teams) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_team(self):
        """Should get team asynchronously."""
        respx.get("https://api.usepylon.com/teams/async_team").mock(
            return_value=httpx.Response(
                200, json={"data": make_team_data(team_id="async_team")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            team = await client.teams.get("async_team")
            assert team.id == "async_team"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_team(self):
        """Should create team asynchronously."""
        respx.post("https://api.usepylon.com/teams").mock(
            return_value=httpx.Response(
                201, json={"data": make_team_data(team_id="new_async_team")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            team = await client.teams.create(name="Async Team")
            assert team.id == "new_async_team"


class TestUsersResource:
    """Integration tests for users resource."""

    @respx.mock
    def test_list_users(self):
        """Should list all users."""
        respx.get("https://api.usepylon.com/users").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_user_data(user_id=f"user_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            users = list(client.users.list())
            assert len(users) == 3

    @respx.mock
    def test_get_user(self):
        """Should get a specific user by ID."""
        respx.get("https://api.usepylon.com/users/user_123").mock(
            return_value=httpx.Response(200, json={"data": make_user_data()})
        )

        with PylonClient(api_key="test-key") as client:
            user = client.users.get("user_123")
            assert user.id == "user_123"
            assert user.name == "Test User"

    @respx.mock
    def test_search_users(self):
        """Should search users by query."""
        respx.post("https://api.usepylon.com/users/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_user_data(user_id="found_user")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            users = list(client.users.search("test"))
            assert len(users) == 1
            assert users[0].id == "found_user"


class TestAsyncUsersResource:
    """Integration tests for async users resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_users(self):
        """Should list users asynchronously."""
        respx.get("https://api.usepylon.com/users").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_user_data(user_id="async_user")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            users = []
            async for user in client.users.list():
                users.append(user)
            assert len(users) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_user(self):
        """Should get user asynchronously."""
        respx.get("https://api.usepylon.com/users/async_user").mock(
            return_value=httpx.Response(
                200, json={"data": make_user_data(user_id="async_user")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            user = await client.users.get("async_user")
            assert user.id == "async_user"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_users(self):
        """Should search users asynchronously."""
        respx.post("https://api.usepylon.com/users/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_user_data(user_id="async_found")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            users = []
            async for user in client.users.search("query"):
                users.append(user)
            assert len(users) == 1


class TestTagsResource:
    """Integration tests for tags resource."""

    @respx.mock
    def test_list_tags(self):
        """Should list all tags."""
        respx.get("https://api.usepylon.com/tags").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_tag_data(tag_id=f"tag_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            tags = list(client.tags.list())
            assert len(tags) == 3

    @respx.mock
    def test_get_tag(self):
        """Should get a specific tag by ID."""
        respx.get("https://api.usepylon.com/tags/tag_123").mock(
            return_value=httpx.Response(200, json={"data": make_tag_data()})
        )

        with PylonClient(api_key="test-key") as client:
            tag = client.tags.get("tag_123")
            assert tag.id == "tag_123"
            assert tag.value == "Test Tag"

    @respx.mock
    def test_create_tag(self):
        """Should create a new tag."""
        respx.post("https://api.usepylon.com/tags").mock(
            return_value=httpx.Response(
                201, json={"data": make_tag_data(tag_id="new_tag", name="New Tag")}
            )
        )

        with PylonClient(api_key="test-key") as client:
            tag = client.tags.create(name="New Tag")
            assert tag.id == "new_tag"


class TestAsyncTagsResource:
    """Integration tests for async tags resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_tags(self):
        """Should list tags asynchronously."""
        respx.get("https://api.usepylon.com/tags").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_tag_data(tag_id="async_tag")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            tags = []
            async for tag in client.tags.list():
                tags.append(tag)
            assert len(tags) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_tag(self):
        """Should get tag asynchronously."""
        respx.get("https://api.usepylon.com/tags/async_tag").mock(
            return_value=httpx.Response(
                200, json={"data": make_tag_data(tag_id="async_tag")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            tag = await client.tags.get("async_tag")
            assert tag.id == "async_tag"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_tag(self):
        """Should create tag asynchronously."""
        respx.post("https://api.usepylon.com/tags").mock(
            return_value=httpx.Response(
                201, json={"data": make_tag_data(tag_id="new_async_tag")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            tag = await client.tags.create(name="Async Tag")
            assert tag.id == "new_async_tag"


class TestTasksResource:
    """Integration tests for tasks resource."""

    @respx.mock
    def test_list_tasks(self):
        """Should list all tasks."""
        respx.get("https://api.usepylon.com/tasks").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_task_data(task_id=f"task_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            tasks = list(client.tasks.list())
            assert len(tasks) == 3

    @respx.mock
    def test_get_task(self):
        """Should get a specific task by ID."""
        respx.get("https://api.usepylon.com/tasks/task_123").mock(
            return_value=httpx.Response(200, json={"data": make_task_data()})
        )

        with PylonClient(api_key="test-key") as client:
            task = client.tasks.get("task_123")
            assert task.id == "task_123"
            assert task.title == "Test Task"

    @respx.mock
    def test_create_task(self):
        """Should create a new task."""
        respx.post("https://api.usepylon.com/tasks").mock(
            return_value=httpx.Response(
                201, json={"data": make_task_data(task_id="new_task", title="New Task")}
            )
        )

        with PylonClient(api_key="test-key") as client:
            task = client.tasks.create(title="New Task")
            assert task.id == "new_task"

    @respx.mock
    def test_update_task(self):
        """Should update a task."""
        respx.patch("https://api.usepylon.com/tasks/task_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_task_data(task_id="task_123", status="completed")},
            )
        )

        with PylonClient(api_key="test-key") as client:
            task = client.tasks.update("task_123", status="completed")
            assert task.status == "completed"


class TestAsyncTasksResource:
    """Integration tests for async tasks resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_tasks(self):
        """Should list tasks asynchronously."""
        respx.get("https://api.usepylon.com/tasks").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_task_data(task_id="async_task")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            tasks = []
            async for task in client.tasks.list():
                tasks.append(task)
            assert len(tasks) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_task(self):
        """Should get task asynchronously."""
        respx.get("https://api.usepylon.com/tasks/async_task").mock(
            return_value=httpx.Response(
                200, json={"data": make_task_data(task_id="async_task")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            task = await client.tasks.get("async_task")
            assert task.id == "async_task"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_task(self):
        """Should create task asynchronously."""
        respx.post("https://api.usepylon.com/tasks").mock(
            return_value=httpx.Response(
                201, json={"data": make_task_data(task_id="new_async_task")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            task = await client.tasks.create(title="Async Task")
            assert task.id == "new_async_task"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_update_task(self):
        """Should update task asynchronously."""
        respx.patch("https://api.usepylon.com/tasks/async_task").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_task_data(task_id="async_task", status="completed")},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            task = await client.tasks.update("async_task", status="completed")
            assert task.status == "completed"


class TestProjectsResource:
    """Integration tests for projects resource."""

    @respx.mock
    def test_list_projects(self):
        """Should list all projects."""
        respx.get("https://api.usepylon.com/projects").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_project_data(project_id=f"project_{i}") for i in range(3)
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            projects = list(client.projects.list())
            assert len(projects) == 3

    @respx.mock
    def test_get_project(self):
        """Should get a specific project by ID."""
        respx.get("https://api.usepylon.com/projects/project_123").mock(
            return_value=httpx.Response(200, json={"data": make_project_data()})
        )

        with PylonClient(api_key="test-key") as client:
            project = client.projects.get("project_123")
            assert project.id == "project_123"
            assert project.name == "Test Project"

    @respx.mock
    def test_create_project(self):
        """Should create a new project."""
        respx.post("https://api.usepylon.com/projects").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_project_data(
                        project_id="new_project", name="New Project"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            project = client.projects.create(name="New Project")
            assert project.id == "new_project"


class TestAsyncProjectsResource:
    """Integration tests for async projects resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_projects(self):
        """Should list projects asynchronously."""
        respx.get("https://api.usepylon.com/projects").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_project_data(project_id="async_project")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            projects = []
            async for project in client.projects.list():
                projects.append(project)
            assert len(projects) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_project(self):
        """Should get project asynchronously."""
        respx.get("https://api.usepylon.com/projects/async_project").mock(
            return_value=httpx.Response(
                200, json={"data": make_project_data(project_id="async_project")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            project = await client.projects.get("async_project")
            assert project.id == "async_project"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_project(self):
        """Should create project asynchronously."""
        respx.post("https://api.usepylon.com/projects").mock(
            return_value=httpx.Response(
                201, json={"data": make_project_data(project_id="new_async_project")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            project = await client.projects.create(name="Async Project")
            assert project.id == "new_async_project"


class TestAuditLogsResource:
    """Integration tests for audit logs resource."""

    @respx.mock
    def test_list_audit_logs(self):
        """Should list all audit logs."""
        respx.get("https://api.usepylon.com/audit_logs").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_audit_log_data(log_id=f"log_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            logs = list(client.audit_logs.list())
            assert len(logs) == 3

    @respx.mock
    def test_search_audit_logs(self):
        """Should search audit logs with filters."""
        respx.get("https://api.usepylon.com/audit_logs/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_audit_log_data(log_id="log_1", action="update")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            logs = list(client.audit_logs.search(action="update"))
            assert len(logs) == 1
            assert logs[0].action == "update"


class TestAsyncAuditLogsResource:
    """Integration tests for async audit logs resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_audit_logs(self):
        """Should list audit logs asynchronously."""
        respx.get("https://api.usepylon.com/audit_logs").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_audit_log_data(log_id="async_log")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            logs = []
            async for log in client.audit_logs.list():
                logs.append(log)
            assert len(logs) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_audit_logs(self):
        """Should search audit logs asynchronously."""
        respx.get("https://api.usepylon.com/audit_logs/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_audit_log_data(
                            log_id="search_log", resource_type="account"
                        )
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            logs = []
            async for log in client.audit_logs.search(resource_type="account"):
                logs.append(log)
            assert len(logs) == 1
            assert logs[0].resource_type == "account"


class TestAttachmentsResource:
    """Integration tests for attachments resource."""

    @respx.mock
    def test_list_attachments(self):
        """Should list all attachments."""
        respx.get("https://api.usepylon.com/attachments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_attachment_data(att_id=f"att_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            attachments = list(client.attachments.list())
            assert len(attachments) == 3

    @respx.mock
    def test_get_attachment(self):
        """Should get a specific attachment by ID."""
        respx.get("https://api.usepylon.com/attachments/att_123").mock(
            return_value=httpx.Response(200, json={"data": make_attachment_data()})
        )

        with PylonClient(api_key="test-key") as client:
            attachment = client.attachments.get("att_123")
            assert attachment.id == "att_123"
            assert attachment.filename == "test.txt"

    @respx.mock
    def test_create_attachment(self):
        """Should create a new attachment."""
        respx.post("https://api.usepylon.com/attachments").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_attachment_data(att_id="new_att", filename="new.txt")
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            attachment = client.attachments.create(
                filename="new.txt",
                content_type="text/plain",
                content=b"Hello World",
            )
            assert attachment.id == "new_att"

    @respx.mock
    def test_create_attachment_from_url(self):
        """Should create an attachment from URL."""
        respx.post("https://api.usepylon.com/attachments/from-url").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_attachment_data(
                        att_id="url_att", filename="remote.pdf"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            attachment = client.attachments.create_from_url(
                file_url="https://example.com/file.pdf",
                description="Downloaded file",
            )
            assert attachment.id == "url_att"


class TestAsyncAttachmentsResource:
    """Integration tests for async attachments resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_attachments(self):
        """Should list attachments asynchronously."""
        respx.get("https://api.usepylon.com/attachments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_attachment_data(att_id="async_att")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            attachments = []
            async for att in client.attachments.list():
                attachments.append(att)
            assert len(attachments) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_attachment(self):
        """Should get attachment asynchronously."""
        respx.get("https://api.usepylon.com/attachments/async_att").mock(
            return_value=httpx.Response(
                200, json={"data": make_attachment_data(att_id="async_att")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            attachment = await client.attachments.get("async_att")
            assert attachment.id == "async_att"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_attachment(self):
        """Should create attachment asynchronously."""
        respx.post("https://api.usepylon.com/attachments").mock(
            return_value=httpx.Response(
                201, json={"data": make_attachment_data(att_id="new_async_att")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            attachment = await client.attachments.create(
                filename="async.txt",
                content_type="text/plain",
                content=b"Async content",
            )
            assert attachment.id == "new_async_att"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_attachment_from_url(self):
        """Should create attachment from URL asynchronously."""
        respx.post("https://api.usepylon.com/attachments/from-url").mock(
            return_value=httpx.Response(
                201, json={"data": make_attachment_data(att_id="async_url_att")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            attachment = await client.attachments.create_from_url(
                file_url="https://example.com/async.pdf",
            )
            assert attachment.id == "async_url_att"


def make_kb_data(
    kb_id: str = "kb_123", name: str = "Test KB", **overrides: Any
) -> dict[str, Any]:
    """Create valid knowledge base data for tests."""
    base_data = {
        "id": kb_id,
        "name": name,
        "description": "Test knowledge base",
        "article_count": 5,
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


def make_article_data(
    article_id: str = "article_123",
    kb_id: str = "kb_123",
    title: str = "Test Article",
    **overrides: Any,
) -> dict[str, Any]:
    """Create valid article data for tests."""
    base_data = {
        "id": article_id,
        "title": title,
        "content": "Article content",
        "knowledge_base_id": kb_id,
        "status": "published",
        "created_at": "2024-01-01T00:00:00Z",
    }
    base_data.update(overrides)
    return base_data


def make_message_data(msg_id: str = "msg_123", **overrides: Any) -> dict[str, Any]:
    """Create valid message data for tests."""
    base_data = {
        "id": msg_id,
        "message_html": "<p>Test message</p>",
        "message_text": "Test message",
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "web",
        "is_private": False,
    }
    base_data.update(overrides)
    return base_data


class TestKnowledgeBaseResource:
    """Integration tests for knowledge base resource."""

    @respx.mock
    def test_list_knowledge_bases(self):
        """Should list all knowledge bases."""
        respx.get("https://api.usepylon.com/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_kb_data(kb_id=f"kb_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            kbs = list(client.knowledge_bases.list())
            assert len(kbs) == 3

    @respx.mock
    def test_get_knowledge_base(self):
        """Should get a specific knowledge base by ID."""
        respx.get("https://api.usepylon.com/knowledge-bases/kb_123").mock(
            return_value=httpx.Response(200, json={"data": make_kb_data()})
        )

        with PylonClient(api_key="test-key") as client:
            kb = client.knowledge_bases.get("kb_123")
            assert kb.id == "kb_123"
            assert kb.name == "Test KB"

    @respx.mock
    def test_list_articles(self):
        """Should list articles in a knowledge base."""
        respx.get("https://api.usepylon.com/knowledge-bases/kb_123/articles").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_article_data(article_id=f"art_{i}") for i in range(3)
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            articles = list(client.knowledge_bases.list_articles("kb_123"))
            assert len(articles) == 3

    @respx.mock
    def test_get_article(self):
        """Should get a specific article by ID."""
        respx.get(
            "https://api.usepylon.com/knowledge-bases/kb_123/articles/article_123"
        ).mock(return_value=httpx.Response(200, json={"data": make_article_data()}))

        with PylonClient(api_key="test-key") as client:
            article = client.knowledge_bases.get_article("kb_123", "article_123")
            assert article.id == "article_123"
            assert article.title == "Test Article"

    @respx.mock
    def test_create_article(self):
        """Should create a new article."""
        respx.post("https://api.usepylon.com/knowledge-bases/kb_123/articles").mock(
            return_value=httpx.Response(
                201, json={"data": make_article_data(article_id="new_article")}
            )
        )

        with PylonClient(api_key="test-key") as client:
            article = client.knowledge_bases.create_article(
                "kb_123",
                title="New Article",
                content="New content",
            )
            assert article.id == "new_article"


class TestAsyncKnowledgeBaseResource:
    """Integration tests for async knowledge base resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_knowledge_bases(self):
        """Should list knowledge bases asynchronously."""
        respx.get("https://api.usepylon.com/knowledge-bases").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_kb_data(kb_id="async_kb")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            kbs = []
            async for kb in client.knowledge_bases.list():
                kbs.append(kb)
            assert len(kbs) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_knowledge_base(self):
        """Should get knowledge base asynchronously."""
        respx.get("https://api.usepylon.com/knowledge-bases/async_kb").mock(
            return_value=httpx.Response(
                200, json={"data": make_kb_data(kb_id="async_kb")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            kb = await client.knowledge_bases.get("async_kb")
            assert kb.id == "async_kb"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_articles(self):
        """Should list articles asynchronously."""
        respx.get("https://api.usepylon.com/knowledge-bases/async_kb/articles").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_article_data(article_id="async_article", kb_id="async_kb")
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            articles = []
            async for article in client.knowledge_bases.list_articles("async_kb"):
                articles.append(article)
            assert len(articles) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_article(self):
        """Should get article asynchronously."""
        respx.get(
            "https://api.usepylon.com/knowledge-bases/async_kb/articles/async_article"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_article_data(
                        article_id="async_article", kb_id="async_kb"
                    )
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            article = await client.knowledge_bases.get_article(
                "async_kb", "async_article"
            )
            assert article.id == "async_article"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_article(self):
        """Should create article asynchronously."""
        respx.post("https://api.usepylon.com/knowledge-bases/async_kb/articles").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_article_data(
                        article_id="new_async_article", kb_id="async_kb"
                    )
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            article = await client.knowledge_bases.create_article(
                "async_kb",
                title="Async Article",
                content="Async content",
            )
            assert article.id == "new_async_article"


class TestMessagesResource:
    """Integration tests for messages resource."""

    @respx.mock
    def test_list_messages(self):
        """Should list messages for an issue."""
        respx.get("https://api.usepylon.com/issues/issue_123/messages").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_message_data(msg_id=f"msg_{i}") for i in range(3)],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            messages = list(client.messages.list("issue_123"))
            assert len(messages) == 3

    @respx.mock
    def test_get_message(self):
        """Should get a specific message by ID."""
        respx.get("https://api.usepylon.com/issues/issue_123/messages/msg_123").mock(
            return_value=httpx.Response(200, json={"data": make_message_data()})
        )

        with PylonClient(api_key="test-key") as client:
            message = client.messages.get("issue_123", "msg_123")
            assert message.id == "msg_123"
            assert message.message_text == "Test message"

    @respx.mock
    def test_create_message(self):
        """Should create a new message."""
        respx.post("https://api.usepylon.com/issues/issue_123/messages").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_message_data(
                        msg_id="new_msg", message_text="New message"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            message = client.messages.create(
                "issue_123",
                content="New message",
            )
            assert message.id == "new_msg"


class TestAsyncMessagesResource:
    """Integration tests for async messages resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_messages(self):
        """Should list messages asynchronously."""
        respx.get("https://api.usepylon.com/issues/async_issue/messages").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_message_data(msg_id="async_msg")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            messages = []
            async for msg in client.messages.list("async_issue"):
                messages.append(msg)
            assert len(messages) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_message(self):
        """Should get message asynchronously."""
        respx.get(
            "https://api.usepylon.com/issues/async_issue/messages/async_msg"
        ).mock(
            return_value=httpx.Response(
                200, json={"data": make_message_data(msg_id="async_msg")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            message = await client.messages.get("async_issue", "async_msg")
            assert message.id == "async_msg"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_message(self):
        """Should create message asynchronously."""
        respx.post("https://api.usepylon.com/issues/async_issue/messages").mock(
            return_value=httpx.Response(
                201, json={"data": make_message_data(msg_id="new_async_msg")}
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            message = await client.messages.create(
                "async_issue",
                content="Async message",
            )
            assert message.id == "new_async_msg"
