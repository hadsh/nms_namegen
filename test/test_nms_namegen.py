import unittest
from unittest.mock import patch
import namegen
from contextlib import redirect_stdout
from io import StringIO


class TestGenerator(unittest.TestCase):
    @patch("sys.argv", ["nms_namegen.py", "system", "0001ff234533", "120"])
    def test_main_with_arguments(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Yatiiat-Suz I\n")

    @patch("sys.argv", ["nms_namegen.py", "system", "0001ff234533"])
    def test_main_with_missing_argument(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 1)

    @patch("sys.argv", ["nms_namegen.py", "sysem", "0001ff234533", "120"])
    def test_main_with_bad_command(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["nms_namegen.py", "system", "00M1ff234533", "120"])
    def test_main_with_bad_portal_code(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["nms_namegen.py", "system", "001ff234533", "120"])
    def test_main_with_short_portal_code(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["nms_namegen.py", "system", "0001ff234533", "1X"])
    def test_main_with_bad_galaxy_id(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["nms_namegen.py", "system", "0001ff234533", "1000"])
    def test_main_with_out_of_range_galaxy_id(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 2)

    @patch("sys.argv", ["nms_namegen.py", "help"])
    def test_main_help_command_does_not_error(self):
        with self.assertRaises(SystemExit) as co:
            namegen.main()
        self.assertEqual(co.exception.code, 0)

    @patch("sys.argv", ["nms_namegen.py", "planet", "578CC780BAEB5C94"])
    def test_main_planet_command(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Akotap XIX\n")
    
    @patch("sys.argv", ["nms_namegen.py", "planet", "0x1003ff285671", "9", "6"])
    def test_main_planet_from_portal_code_command(self):
        with redirect_stdout(StringIO()) as buffer:
            try:
                namegen.main()
            except SystemExit:
                pass
        self.assertEqual(buffer.getvalue(), "Bedalmbe Tau\n")