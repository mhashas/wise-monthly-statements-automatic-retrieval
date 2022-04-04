import calendar
import datetime
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

    def construct_parser(self) -> ArgumentParser:
        """Constructs and returns the parser object

        Returns:
            argparse.ArgumentParser: parser object
        """
        parser = ArgumentParser(description="Wise Monthly Statements Retrieval Automatic Retrieval")
        parser.add_argument("--start_date", type=lambda s: datetime.strftime(s, "%Y-%m-%d %H:%M:%S %Z"), required=False)
        parser.add_argument("--end_date", type=lambda s: datetime.strftime(s, "%Y-%m-%d %H:%M:%S %Z"), required=False)
        parser.add_argument("--month", type=str, required=False)
        parser.add_argument("--year", type=str, required=False)
        parser.add_argument(
            "--output_dir",
            help="directory in which the generated pdfs are saved",
            required=False,
            default="./",
        )

        return parser

    def parse_arguments(self, parser: ArgumentParser) -> Namespace:
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

        if not args.month and (not args.start_date or args.end_date):
            # default to previous month
            month_index = datetime.now().month - 1
            args.month = calendar.month_abbr[month_index]
            print(f"Defaulting to previous month {args.month}")

        if args.month:
            month = list(calendar.month_abbr).index(args.month.capitalize())
            year = args.year or datetime.now().date().year
            
            first_day = 1
            _, last_day = calendar.monthrange(year, month)

            first_day = datetime(year, month, first_day, 0, 0, 0).strftime('%Y-%m-%dT%H:%M:%SZ')
            last_day = datetime(year, month, last_day, 23, 59, 59).strftime('%Y-%m-%dT%H:%M:%SZ')

            args.start_date = first_day
            args.end_date = last_day

        return args


class Config:
    def __init__(self, args: Namespace):
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.output_dir = args.output_dir

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
