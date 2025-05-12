import csv
from enum import Enum
from datetime import datetime
from io import StringIO
from typing import Iterable, List, Dict


class ColumnType(Enum):
    DATE = "date"
    NUMERIC = "numérique"
    STRING = "chaîne"

    def parse_value(self, value: str):
        if self == ColumnType.DATE:
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {value}")
        elif self == ColumnType.NUMERIC:
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Invalid numeric value: {value}")
        return value

    def value_to_string(self, value) -> str:
        if self == ColumnType.DATE:
            return value.strftime("%d/%m/%Y")
        return str(value)


class FixedFileFormatConverter:
    """Convert fixed-width file format to CSV based on metadata."""

    def __init__(self, metadata_file_path: str):
        self.metadata = self._load_metadata(metadata_file_path)

    def _load_metadata(self, metadata_file: str) -> List[Dict]:
        """Load and validate metadata from CSV file."""
        metadata = []
        with open(metadata_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 3:
                    raise ValueError(
                        f"Invalid metadata row: {row}. Expected 3 columns."
                    )
                name, length, col_type_id = row
                try:
                    length = int(length)
                except ValueError:
                    raise ValueError(f"Invalid length value: {length}")
                if length <= 0:
                    raise ValueError(f"Length must be positive: {length}")
                col_type = ColumnType(col_type_id.strip().lower())
                metadata.append(
                    {"name": name.strip(), "length": length, "type": col_type}
                )
        return metadata

    def _parse_line(self, line: str) -> List[str]:
        """Parse a single line according to metadata specifications."""
        line = line.rstrip()
        values = []
        for col in self.metadata:
            raw_value = line[: col["length"]]
            first_space_index = raw_value.find(" ")
            if first_space_index != -1:
                raw_value = raw_value[:first_space_index]
                line = line[len(raw_value) + 1 :]  # +1 to skip the space
            else:
                line = line[len(raw_value) :]
            parsed_value = col["type"].parse_value(raw_value)
            value_string = col["type"].value_to_string(parsed_value)
            values.append(value_string)
        return values

    def convert(
        self,
        lines: Iterable[str],
    ):
        """
        Convert lines from fixed format to
        CSV format based on metadata.

        yields: (csv_line, error_message) for each input line
        """
        with (
            StringIO() as outfile,
        ):
            writer = csv.writer(outfile)
            writer.writerow([col["name"] for col in self.metadata])
            yield outfile.getvalue(), None
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip()
                try:
                    values = self._parse_line(line)
                    outfile.seek(0)
                    outfile.truncate(0)
                    writer.writerow(values)
                    yield outfile.getvalue(), None
                except ValueError as e:
                    error_message = f"ERROR: {line}: {e} (line {line_num})"
                    yield None, error_message
