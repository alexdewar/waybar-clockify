"""A script to output the currently running task on waybar."""
import json
import sys
from time import sleep

from clockify_api_client.client import ClockifyAPIClient

API_URL = "api.clockify.me/v1"


def get_project_name(
    client: ClockifyAPIClient, workspace_id: str, project_id: str | None
):
    """Get the name of the project specified by workspace and project IDs."""
    if not project_id:
        return "(none)"

    url = f"{client.projects.base_url}/workspaces/{workspace_id}/projects/{project_id}"
    return client.projects.get(url)["name"]


def output_waybar(text: str, cls: str | None = None, **kwargs):
    """Output text to waybar."""
    output = {"text": text, "tooltip": "Clockify"} | kwargs
    if cls:
        output["class"] = cls
    print(json.dumps(output))
    sys.stdout.flush()


def main() -> None:
    """Main entry point of program."""
    client = ClockifyAPIClient().build(sys.argv[1], API_URL)
    workspaces = client.workspaces.get_workspaces()
    workspace_id = workspaces[0]["id"]  # TODO: CHECK
    user_id = client.users.get_current_user()["id"]

    prev_entry = None
    while True:
        time_entries = client.time_entries.get_time_entries(workspace_id, user_id)
        entry = time_entries[0]
        if entry != prev_entry:
            project = get_project_name(client, workspace_id, entry["projectId"])
            icon = "not-running" if entry["timeInterval"]["end"] else "running"
            output_waybar(project, icon, alt=icon)
            prev_entry = entry
        sleep(10)
