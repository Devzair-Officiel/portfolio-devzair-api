import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_project_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/projects/",
        json={"title": "Test", "description": "desc", "stack": ["Python"]},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_get_project(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/projects/",
        json={
            "title": "devZair",
            "description": "Mon portfolio",
            "stack": ["React", "FastAPI"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "devZair"
    assert "id" in data

    get = await auth_client.get(f"/api/v1/projects/{data['id']}")
    assert get.status_code == 200
    assert get.json()["title"] == "devZair"


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projects/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(auth_client: AsyncClient) -> None:
    create = await auth_client.post(
        "/api/v1/projects/",
        json={"title": "Original", "description": "desc", "stack": ["Python"]},
    )
    project_id = create.json()["id"]

    update = await auth_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "Modifié"},
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Modifié"
    assert update.json()["description"] == "desc"


@pytest.mark.asyncio
async def test_delete_project(auth_client: AsyncClient) -> None:
    create = await auth_client.post(
        "/api/v1/projects/",
        json={"title": "À supprimer", "description": "desc", "stack": ["Python"]},
    )
    project_id = create.json()["id"]

    delete = await auth_client.delete(f"/api/v1/projects/{project_id}")
    assert delete.status_code == 204

    get = await auth_client.get(f"/api/v1/projects/{project_id}")
    assert get.status_code == 404
