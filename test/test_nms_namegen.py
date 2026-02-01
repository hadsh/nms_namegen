import unittest
from unittest.mock import patch
import namegen
from contextlib import redirect_stdout
from io import StringIO


class TestGenerator(unittest.TestCase):
    @patch("sys.argv", ["namegen.py", "system", "-p", "0001ff234533", "-g", "120"])
    def test_main_with_arguments(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Yatiiat-Suz I\n")

    @patch("sys.argv", ["namegen.py", "region", "-p", "0001ff234533", "-g", "120"])
    def test_main_region(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Nuriange\n")

    @patch("sys.argv", ["namegen.py", "system", "0001ff234533"])
    def test_main_with_missing_argument(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["namegen.py", "sysem", "-p0001ff234533", "-g120"])
    def test_main_with_bad_command(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["namegen.py", "system", "-p00M1ff234533", "-g120"])
    def test_main_with_bad_portal_code(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["namegen.py", "system", "-p0001ff234533", "-gX"])
    def test_main_with_bad_galaxy_id(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["namegen.py", "system", "-p", "0001ff234533", "-g", "1000"])
    def test_main_with_out_of_range_galaxy_id(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["namegen.py", "--help"])
    def test_main_help_command_does_not_error(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 0)

    @patch("sys.argv", ["namegen.py", "planet", "-s", "578CC780BAEB5C94"])
    def test_main_planet_command(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Akotap XIX\n")

    @patch("sys.argv", ["namegen.py", "planet", "-p", "0x1003ff285671", "-g", "9"])
    def test_main_planet_from_portal_code_command(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Bedalmbe Tau\n")
