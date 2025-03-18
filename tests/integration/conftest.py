"""
Shared fixtures for integration tests.
"""

import pytest
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture(scope="function", autouse=True)
def debug_test_name(request):
    """Print the test name before and after each test."""
    print(f"\n{'='*50}\nSTARTING TEST: {request.node.name}\n{'='*50}")
    yield
    print(f"\n{'='*50}\nFINISHED TEST: {request.node.name}\n{'='*50}")


@pytest.fixture(autouse=True)
def mock_scheduler(monkeypatch):
    """Mock the scheduler to prevent it from running during tests."""
    print("MOCKING SCHEDULER")
    
    def mock_start_scheduler_thread():
        """Mock start_scheduler_thread to do nothing."""
        print("MOCK START SCHEDULER CALLED")
        pass
    
    def mock_stop_scheduler_thread():
        """Mock stop_scheduler_thread to do nothing."""
        print("MOCK STOP SCHEDULER CALLED")
        pass
    
    # Mock both scheduler functions
    monkeypatch.setattr("news.news_scheduler.start_scheduler_thread", mock_start_scheduler_thread)
    monkeypatch.setattr("news.news_scheduler.stop_scheduler_thread", mock_stop_scheduler_thread)
        

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    print("CREATING TEST CLIENT")
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_background_tasks(monkeypatch):
    """Mock background tasks to avoid actually running them during tests."""
    # This is a universal fixture that can be used across different tests
    # to prevent background tasks from running
    
    # Store called tasks for inspection
    called_tasks = []
    
    def mock_add_task(self, func, *args, **kwargs):
        """Record the task rather than scheduling it."""
        task_name = getattr(func, "__name__", str(func))
        print(f"MOCK BACKGROUND TASK: {task_name}")
        called_tasks.append((func, args, kwargs))
    
    # Patch the add_task method
    from fastapi import BackgroundTasks
    monkeypatch.setattr(BackgroundTasks, "add_task", mock_add_task)
    
    return called_tasks 