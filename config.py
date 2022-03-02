from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Optional

import constants as c


class BaseParser:
    """This class defines command line arguments that are used by the application"""

    POSSIBLE_CURRENCIES = [c.CURRENCY_EUR, c.CURRENCY_RON, c.CURRENCY_USD]

    def __init__(self):
        parser = self.construct_parser()
        self.args = self.parse_arguments(parser)
        self.args.run_name = self.construct_run_name(self.args)

    def construct_parser(self) -> ArgumentParser:
        """Constructs and returns the parser object

        Returns:
            argparse.ArgumentParser: parser object
        """
        parser = ArgumentParser(description="Wise Monthly Statements Retrieval Automatic Retrieval")
        parser.add_argument("--start_date", help="", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), required=False)
        parser.add_argument("--end_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), required=False, help="")
        parser.add_argument("--")

        return parser

    def parse_arguments(self, parser: argparse.ArgumentParser) -> argparse.Namespace:
        """Parses and returns the command line arguments.
        Raises an error on unknown arguments.

        Args:
            parser (argparse.ArgumentParser): parser object

        Returns:
            argparse.Namespace: parsed command line arguments
        """
        args, unknown_args = parser.parse_known_args()
        if len(unknown_args) > 0:
            print(f"Warning: Unknown arguments detected {unknown_args}")

        return args


class Config:
    def __init__(self, args: Namespace):
        self.start_date = args.start_date
        self.end_date = args.end_date

    @classmethod
    def from_parser(cls, parser: Optional[BaseParser] = None):
        """Initialize a config object from a given parser. If no parser is given, a base parser is initialized.

        Args:
            parser (Optional[BaseParser]): parser from which to initalize

        Returns:
            Config: config
        """
        parser = parser or BaseParser()
        return cls(parser.args)
