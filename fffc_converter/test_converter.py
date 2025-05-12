import unittest
import tempfile
import os
from datetime import datetime
from .converter import ColumnType, FixedFileFormatConverter


class TestColumnType(unittest.TestCase):
    def test_parse_value_date(self):
        # Test valid date
        date_str = "2024-03-20"
        result = ColumnType.DATE.parse_value(date_str)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 20)

        # Test invalid date
        with self.assertRaises(ValueError):
            ColumnType.DATE.parse_value("invalid-date")

    def test_parse_value_numeric(self):
        # Test valid numeric
        self.assertEqual(ColumnType.NUMERIC.parse_value("123.45"), 123.45)
        self.assertEqual(ColumnType.NUMERIC.parse_value("0"), 0.0)
        self.assertEqual(ColumnType.NUMERIC.parse_value("-42"), -42.0)

        # Test invalid numeric
        with self.assertRaises(ValueError):
            ColumnType.NUMERIC.parse_value("not-a-number")

    def test_parse_value_string(self):
        # Test string parsing (should return as is)
        test_str = "hello world"
        self.assertEqual(ColumnType.STRING.parse_value(test_str), test_str)

    def test_value_to_string(self):
        # Test date to string
        date = datetime(2024, 3, 20)
        self.assertEqual(ColumnType.DATE.value_to_string(date), "20/03/2024")

        # Test numeric to string
        self.assertEqual(ColumnType.NUMERIC.value_to_string(123.45), "123.45")

        # Test string to string
        self.assertEqual(ColumnType.STRING.value_to_string("test"), "test")


class TestFixedFileFormatConverter(unittest.TestCase):
    def setUp(self):
        # Create a temporary metadata file for testing
        self.metadata_content = """Date de naissance,10,date
Prénom,15,chaîne
Nom de famille,15,chaîne
Poids,5,numérique"""
        self.temp_dir = tempfile.mkdtemp()
        self.metadata_file_path = os.path.join(self.temp_dir, "test_metadata.csv")
        with open(self.metadata_file_path, "w", encoding="utf-8") as f:
            f.write(self.metadata_content)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.metadata_file_path):
            os.remove(self.metadata_file_path)
        os.rmdir(self.temp_dir)

    def test_load_metadata(self):
        converter = FixedFileFormatConverter(self.metadata_file_path)
        metadata = converter.metadata

        self.assertEqual(len(metadata), 4)
        self.assertEqual(metadata[0]["name"], "Date de naissance")
        self.assertEqual(metadata[0]["length"], 10)
        self.assertEqual(metadata[0]["type"], ColumnType.DATE)

        self.assertEqual(metadata[1]["name"], "Prénom")
        self.assertEqual(metadata[1]["length"], 15)
        self.assertEqual(metadata[1]["type"], ColumnType.STRING)

        self.assertEqual(metadata[2]["name"], "Nom de famille")
        self.assertEqual(metadata[2]["length"], 15)
        self.assertEqual(metadata[2]["type"], ColumnType.STRING)

        self.assertEqual(metadata[3]["name"], "Poids")
        self.assertEqual(metadata[3]["length"], 5)
        self.assertEqual(metadata[3]["type"], ColumnType.NUMERIC)

    def test_invalid_metadata(self):
        # Test invalid number of columns
        invalid_metadata_path = os.path.join(self.temp_dir, "invalid_metadata.csv")
        with open(invalid_metadata_path, "w", encoding="utf-8") as f:
            f.write("name,10")
        with self.assertRaises(ValueError):
            FixedFileFormatConverter(invalid_metadata_path)
        os.remove(invalid_metadata_path)

        # Test invalid length
        invalid_length_path = os.path.join(self.temp_dir, "invalid_length.csv")
        with open(invalid_length_path, "w", encoding="utf-8") as f:
            f.write("name,-10,chaîne")
        with self.assertRaises(ValueError):
            FixedFileFormatConverter(invalid_length_path)
        os.remove(invalid_length_path)

        # Test invalid type
        invalid_type_path = os.path.join(self.temp_dir, "invalid_type.csv")
        with open(invalid_type_path, "w", encoding="utf-8") as f:
            f.write("name,10,invalid_type")
        with self.assertRaises(ValueError):
            FixedFileFormatConverter(invalid_type_path)
        os.remove(invalid_type_path)

    def test_parse_line(self):
        converter = FixedFileFormatConverter(self.metadata_file_path)

        # Test valid line with exact column lengths
        line = "1970-01-01John Smith 81.5"
        values = converter._parse_line(line)
        self.assertEqual(values, ["01/01/1970", "John", "Smith", "81.5"])

        line = "1975-01-31Jane Doe 61"
        values = converter._parse_line(line)
        self.assertEqual(values, ["31/01/1975", "Jane", "Doe", "61.0"])

        # Test line that's too short
        with self.assertRaises(ValueError):
            converter._parse_line("John")

    def test_convert(self):
        converter = FixedFileFormatConverter(self.metadata_file_path)

        # Test valid conversion with exact column lengths
        # name (10 chars) + age (3 chars) + birth_date (10 chars)
        input_lines = [
            "1970-01-01John Smith 81.5",
            "1975-01-31Jane Doe 61",
            "1988-11-28Bob Big 102.4",
        ]

        results = list(converter.convert(input_lines))

        # First result should be header
        self.assertIsNotNone(results[0][0])
        self.assertIn("Date de naissance,Prénom,Nom de famille,Poids", results[0][0])

        # Check converted lines
        self.assertEqual(results[1][0], "01/01/1970,John,Smith,81.5\r\n")
        self.assertEqual(results[2][0], "31/01/1975,Jane,Doe,61.0\r\n")
        self.assertEqual(results[3][0], "28/11/1988,Bob,Big,102.4\r\n")

        # Test invalid line
        invalid_lines = ["Invalid Data"]
        results = list(converter.convert(invalid_lines))
        self.assertIsNone(results[1][0])  # No CSV output
        self.assertIsNotNone(results[1][1])  # Error message present


if __name__ == "__main__":
    unittest.main()
