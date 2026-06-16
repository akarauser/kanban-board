import json
import os
from datetime import datetime
from pathlib import Path
from time import sleep

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track
from rich.table import Table
from utils._logger import logger
from utils._validation import config_args

boards_path = Path(__file__).parent / "boards"
boards_path.mkdir(exist_ok=True)
boards_dir = str(boards_path) + "/"


class Kanban:
    console = Console()

    def __init__(self):
        self.id = 1
        self.console.print()
        self.console.print(Markdown("Welcome to Kanban Board", justify="center"))
        self.console.print()
        self.initialize_board()

    def initialize_board(self):
        """Creates a board or loads saved one."""
        self.console.print(
            Markdown("1.Create new board\t2.Load a board", justify="center")
        )

        start_choice: str = input("Enter your choice: ")
        self.console.print()
        if start_choice == "1":
            self.filename: str = input("Enter the name of the board: ").strip()
            if not self.filename:
                self.filename = boards_dir + "kanban.json"
            else:
                self.filename = boards_dir + self.filename + ".json"
            try:
                with open(self.filename) as f:
                    self.data = json.load(f)
            except FileNotFoundError:
                self.data = {
                    "id": 0,
                    "columns": [
                        f"{config_args.color[0]}Todo",
                        f"{config_args.color[1]}Doing",
                        f"{config_args.color[2]}Done",
                    ],
                    "tasks": [],
                }
                self.save_kanban_data(self.data)  # Create the file
                logger.info("Kanban data file created.")
        elif start_choice == "2":
            self.console.print("List of the saved boards: ")
            self.console.print(
                " | ".join(
                    [board.split(".json")[0] for board in os.listdir(boards_dir)]
                )
            )
            print()
            self.filename = input("Enter the name of the board: ").strip()
            if not self.filename:
                try:
                    self.filename = boards_dir + "kanban.json"
                    with open(self.filename) as f:
                        self.data = json.load(f)
                except FileNotFoundError:
                    self.data = {
                        "id": 0,
                        "columns": [
                            f"{config_args.color[0]}Todo",
                            f"{config_args.color[1]}Doing",
                            f"{config_args.color[2]}Done",
                        ],
                        "tasks": [],
                    }
                    self.save_kanban_data(self.data)  # Create the file
                    logger.info("Kanban data file created.")
            else:
                try:
                    self.filename = boards_dir + self.filename + ".json"
                    with open(self.filename) as f:
                        self.data = json.load(f)
                except FileNotFoundError:
                    self.data = {
                        "id": 0,
                        "columns": [
                            f"{config_args.color[0]}Todo",
                            f"{config_args.color[1]}Doing",
                            f"{config_args.color[2]}Done",
                        ],
                        "tasks": [],
                    }
                    self.save_kanban_data(self.data)  # Create the file
                    logger.info("Kanban data file created.")
        else:
            for _ in track(range(100), description="[green]Closing the program"):
                self.process_data()

    def process_data(self) -> None:
        """Sleep for 0.01 second."""
        sleep(0.01)

    def save_kanban_data(self, data) -> None:
        """Saves kanban data to a JSON file."""
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)
            for _ in track(range(100), description="[green]Processing data"):
                self.process_data()
            logger.info("Kanban data saved to file.")  # Log saving
        except Exception as e:
            logger.error(f"Saving Kanban data failed: {e}")

    def display_kanban_board(self, data, filter_status=None):
        """Displays the kanban board using rich."""
        try:
            table = Table(box=box.HORIZONTALS, expand=True)
            table.add_column("[pale_turquoise1]ID")
            table.add_column("[pale_turquoise1]Date")
            table.add_column("[pale_turquoise1]Name")
            table.add_column("[pale_turquoise1]Description", overflow="fold")
            table.add_column("[pale_turquoise1]Status", justify="right")

            for task in data["tasks"]:
                if filter_status is None or task["status"] == filter_status:
                    table.add_row(
                        task["id"],
                        task["date"],
                        task["name"],
                        task["description"],
                        task["status"],
                    )

            self.console.print(table)
            logger.info("Kanban board displayed.")

        except Exception as e:
            logger.error(f"Displaying Kanban board failed: {e}")

    def add_task(self, data):
        """Adds a new task to the kanban board."""
        try:
            task_date: str = datetime.now().strftime("%y-%m-%d")
            name: str = input("Task Name: ")
            description: str = input("Task Description: ")
            status: str = (
                input("Status (Todo, Doing, Done - Default: Todo): ")
                .strip()
                .capitalize()
                or "Todo"
            )

            if status == "Todo":
                new_task: dict[str, str] = {
                    "id": f"{config_args.color[3]}{data['id'] + 1}",
                    "date": task_date,
                    "name": name,
                    "description": description,
                    "status": f"{config_args.color[0]}{status}",
                }
            elif status == "Doing":
                new_task = {
                    "id": f"{config_args.color[3]}{data['id'] + 1}",
                    "date": task_date,
                    "name": name,
                    "description": description,
                    "status": f"{config_args.color[1]}{status}",
                }
            else:
                new_task = {
                    "id": f"{config_args.color[3]}{data['id'] + 1}",
                    "date": task_date,
                    "name": name,
                    "description": description,
                    "status": f"{config_args.color[2]}{status}",
                }

            data["tasks"].append(new_task)
            data["id"] += 1
            self.save_kanban_data(data)
            print("Task added!")
            logger.info("Task added successfully.")

        except Exception as e:
            logger.error(f"Adding task failed: {e}")

    def move_task(self, data):
        """Moves a task between columns."""
        try:
            task_id: str = input("Enter the ID of the task to move: ").strip()

            task_found = False
            for task in data["tasks"]:
                if task["id"] == f"{config_args.color[3]}{task_id}":
                    task_found = True
                    current_column = None
                    for i, col in enumerate(data["columns"]):
                        if task["status"] == col:
                            current_column = i
                            break
                    if current_column is not None:
                        new_column_index: int = (current_column + 1) % len(
                            data["columns"]
                        )
                        # Move the task
                        data["tasks"].remove(task)
                        task["status"] = data["columns"][new_column_index]
                        data["tasks"].append(task)
                        self.save_kanban_data(data)
                        print("Task moved!")
                        logger.info("Task moved successfully.")
                        break

            if not task_found:
                print("Task not found.")
                logger.warning(f"Task '{task_id}' not found.")

        except Exception as e:
            logger.error(f"Moving task failed: {e}")

    def edit_task(self, data):
        """Edits an existing task."""
        try:
            task_date = datetime.now().strftime("%y-%m-%d")
            task_id = input("Enter the ID of the task to edit: ").strip()

            task_found = False
            for task in data["tasks"]:
                if task["id"] == f"{config_args.color[3]}{task_id}":
                    task_found = True
                    print("Editing Task:")
                    print("Current Name:", task["name"])
                    task["date"] = task_date
                    new_name: str = input(
                        "New Name (leave blank to keep current): "
                    ).strip()
                    if new_name:
                        task["name"] = new_name

                    print("Current Description:", task["description"])
                    new_description = input(
                        "New Description (leave blank to keep current): "
                    ).strip()
                    if new_description:
                        task["description"] = new_description

                    print("Current Status:", task["status"])
                    new_status = (
                        input(
                            "New Status (Todo, Doing, Done - leave blank to keep current): "
                        )
                        .strip()
                        .capitalize()
                        or task["status"]
                    )
                    if new_status == "Todo":
                        task["status"] = f"{config_args.color[0]}{new_status}"
                    elif new_status == "Doing":
                        task["status"] = f"{config_args.color[1]}{new_status}"
                    else:
                        task["status"] = f"{config_args.color[2]}{new_status}"

                    self.save_kanban_data(data)
                    print("Task updated!")
                    logger.info("Task updated successfully.")
                    break

            if not task_found:
                print("Task not found.")
                logger.warning(f"Task '{task_id}' not found.")

        except Exception as e:
            logger.error(f"Editing task failed: {e}")

    def delete_task(self, data):
        """Deletes a task from the kanban board."""
        try:
            task_id: str = input("Enter the ID of the task to delete: ").strip()

            task_found = False
            for i, task in enumerate(data["tasks"]):
                if task["id"] == f"{config_args.color[3]}{task_id}":
                    task_found = True
                    del data["tasks"][i]
                    self.save_kanban_data(data)
                    print("Task deleted!")
                    logger.info("Task deleted successfully.")
                    break

            if not task_found:
                print("Task not found.")
                logger.warning(f"Task '{task_id}'' not found.")

        except Exception as e:
            logger.error(f"Deleting task failed: {e}")

    def run(self):
        """Main function to run the kanban board application."""
        filter = None
        try:
            while True:
                print()
                self.display_kanban_board(self.data, filter_status=filter)

                options: list[str] = [
                    "1. Add Task",
                    "2. Move Task",
                    "3. Edit Task",
                    "4. Delete Task",
                    "5. Filter Tasks",
                    "6. Exit",
                ]
                self.console.print(Columns(options, expand=True, equal=True, title=" "))
                print()

                choice: str = input("Enter your choice: ")

                if choice == "1":
                    self.add_task(self.data)
                elif choice == "2":
                    self.move_task(self.data)
                elif choice == "3":
                    self.edit_task(self.data)
                elif choice == "4":
                    self.delete_task(self.data)
                elif choice == "5":
                    try:
                        filter: str | None = (
                            input(
                                "Enter the status to filter tasks (Todo, Doing, Done - leave blank to show all): "
                            )
                            .strip()
                            .capitalize()
                            or None
                        )
                        if filter == "Todo":
                            filter = f"{config_args.color[0]}{filter}"
                        elif filter == "Doing":
                            filter = f"{config_args.color[1]}{filter}"
                        elif filter == "Done":
                            filter = f"{config_args.color[2]}{filter}"
                        else:
                            filter = None
                    except Exception as e:
                        logger.error(f"Filter failed: {e}")
                elif choice == "6":
                    for _ in track(
                        range(100), description="[green]Closing the program"
                    ):
                        self.process_data()
                    logger.info("Board closed.")
                    break
                else:
                    print("Invalid choice. Please try again.")
        except Exception as e:
            logger.critical(f"Unhandled exception in run: {e}")


if __name__ == "__main__":
    board = Kanban()
    board.run()
