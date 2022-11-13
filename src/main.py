#!/usr/bin/env python

import os
from dataclasses import dataclass

import click
from dotenv import load_dotenv

from src import PROJECT_ROOT


class Config:
    def __init__(self):
        load_dotenv(PROJECT_ROOT / ".env")

        self.API_TOKEN = os.environ['TODOIST_API_TOKEN']


@dataclass(frozen=True)
class ClickChoice:
    add_: str = "add"
    list_: str = "list"

    def as_type(self):
        return click.Choice([self.add_, self.list_])


class TodoistClient:
    def __init__(self, API_TOKEN: str):
        client = self.get_client(API_TOKEN)
        self.client = client

    def get_client(self, API_TOKEN: str):
        from pytodoist import todoist
        from yaspin import yaspin

        print("")
        with yaspin(text="fetch Todoist...", color="yellow") as spinner:
            try:
                user = todoist.login_with_api_token(API_TOKEN)
                works = user.get_project('Inbox')
                spinner.ok("✅ ")
            except Exception as err:
                spinner.fail("💥 ")
                raise err
        return works

    def add(self, task_name: str):
        task = self.client.add_task(task_name)
        print('"' + task.content + '" を追加しました')

    def list(self):
        print("=" * 25)
        print("= タスク一覧")
        for task in self.client.get_tasks():
            print(f"・ {task.content}")


click_choice = ClickChoice()


@click.command()
@click.argument('option', type=click_choice.as_type())
@click.option('-t', '--task', type=str, default="")
def main(option, task):
    cfg = Config()
    todoist = TodoistClient(cfg.API_TOKEN)

    match option:
        case click_choice.add_:
            if not task:
                raise ValueError
            todoist.add(task)
        case click_choice.list_:
            todoist.list()


if __name__ == '__main__':
    main()
