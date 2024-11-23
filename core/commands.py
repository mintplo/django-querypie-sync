from abc import abstractmethod

from django.core.management import BaseCommand


class CommonBaseCommand(BaseCommand):
    command_name = None

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options) -> None:
        self.run(*args, **options)

    @abstractmethod
    def run(self, *args, **options) -> None:
        pass
