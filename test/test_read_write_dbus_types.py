# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020  igo95862

# This file is part of py_sd_bus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from unittest import TestCase, main

from py_sd_bus import sd_bus_open_user


class TestDbusTypes(TestCase):
    def setUp(self) -> None:
        self.bus = sd_bus_open_user()
        self.message = self.bus.new_method_call_message(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1',
            'org.freedesktop.systemd1.Manager',
            'GetUnit')

    def test_unsigned(self) -> None:
        int_t_max = 2**64
        unsigned_integers = ((2**8)-1, (2**16)-1, (2**32)-1, int_t_max-1)
        self.message.append_data("yqut", *unsigned_integers)
        # Test overflows
        self.assertRaises(
            OverflowError, self.message.append_data, "y", 2**8)

        self.assertRaises(
            OverflowError, self.message.append_data, "q", 2**16)

        self.assertRaises(
            OverflowError, self.message.append_data, "u", 2**32)

        self.assertRaises(
            OverflowError, self.message.append_data, "t", 2**64)

        self.assertRaises(
            OverflowError, self.message.append_data, "y", -1)
        self.assertRaises(
            OverflowError, self.message.append_data, "q", -1)
        self.assertRaises(
            OverflowError, self.message.append_data, "u", -1)
        self.assertRaises(
            OverflowError, self.message.append_data, "t", -1)

        self.message.seal()
        return_integers = self.message.get_contents()
        self.assertEqual(unsigned_integers, return_integers)

    def test_signed(self) -> None:
        int_n_max = (2**(16-1))-1
        int_i_max = (2**(32-1))-1
        int_x_max = (2**(64-1))-1
        signed_integers_positive = (int_n_max, int_i_max, int_x_max)
        self.message.append_data("nix", *signed_integers_positive)

        self.assertRaises(
            OverflowError, self.message.append_data, "n", int_n_max + 1)

        self.assertRaises(
            OverflowError, self.message.append_data, "i", int_i_max + 1)

        self.assertRaises(
            OverflowError, self.message.append_data, "x", int_x_max + 1)

        int_n_min = -(2**(16-1))
        int_i_min = -(2**(32-1))
        int_x_min = -(2**(64-1))
        signed_integers_negative = (int_n_min, int_i_min, int_x_min)
        self.message.append_data("n", int_n_min)
        self.assertRaises(
            OverflowError, self.message.append_data, "n", int_n_min - 1)

        self.message.append_data("i", int_i_min)
        self.assertRaises(
            OverflowError, self.message.append_data, "i", int_i_min - 1)

        self.message.append_data("x", int_x_min)
        self.assertRaises(
            OverflowError, self.message.append_data, "x", int_x_min - 1)

        self.message.seal()
        return_integers = self.message.get_contents()
        self.assertEqual(signed_integers_positive +
                         signed_integers_negative, return_integers)

    def test_strings(self) -> None:
        test_string = "test"
        test_path = "/test/object"
        test_signature = "say(xsai)o"

        self.message.append_data("sog", test_string, test_path, test_signature)

        self.message.seal()
        self.assertEqual(self.message.get_contents(),
                         (test_string, test_path, test_signature))

    def test_double(self) -> None:
        test_double = 1.0
        self.message.append_data("d", test_double)

        self.message.seal()
        self.assertEqual(self.message.get_contents(), test_double)

    def test_bool(self) -> None:
        test_booleans = (True, False, False, True, 1 == 1)

        self.message.append_data("bbbbb", *test_booleans)

        self.assertRaises(TypeError, self.message.append_data, 'b', 'asdasad')

        self.message.seal()
        self.assertEqual(self.message.get_contents(), test_booleans)

    def test_array(self) -> None:
        test_string_array = ["Ttest", "serawer", "asdadcxzc"]
        self.message.append_data("as", test_string_array)

        test_bytes_array = b"asdasrddjkmlh\ngnmflkdtgh\0oer27852y4785823"
        self.message.append_data("ay", test_bytes_array)

        test_int_list = [1234, 123123, 764523]
        self.message.append_data("ai", test_int_list)

        self.message.append_data("ax", [])

        self.assertRaises(TypeError, self.message.append_data,
                          "a", test_int_list)

        self.message.seal()

        self.assertEqual(
            self.message.get_contents(),
            (test_string_array, test_bytes_array, test_int_list, []))

    def test_array_compound(self) -> None:
        test_string_array = ["Ttest", "serawer", "asdadcxzc"]
        test_bytes_array = b"asdasrddjkmlh\ngnmflkdtgh\0oer27852y4785823"
        test_int_list = [1234, 123123, 764523]

        self.message.append_data(
            "asayai", test_string_array, test_bytes_array, test_int_list)

        self.message.seal()

        self.assertEqual(self.message.get_contents(),
                         (test_string_array, test_bytes_array, test_int_list))

    def test_nested_array(self) -> None:
        test_string_array_one = ["Ttest", "serawer", "asdadcxzc"]
        test_string_array_two = ["asdaf", "seragdsfrgdswer", "sdfsdgg"]

        self.message.append_data(
            "aas", [test_string_array_one, test_string_array_two])

        self.message.seal()

        self.assertEqual(self.message.get_contents(),
                         [test_string_array_one, test_string_array_two])

    def test_struct(self) -> None:
        struct_data = (123123, "test")
        self.message.append_data("(xs)", struct_data)

        self.message.seal()

        self.assertEqual(self.message.get_contents(), struct_data)

    def test_dict(self) -> None:
        test_dict = {'test': 'a', 'asdaefd': 'cvbcfg'}
        self.message.append_data("{ss}", test_dict)

        self.message.seal()

        self.assertEqual(self.message.get_contents(), test_dict)

    def test_dict_nested_array(self) -> None:
        test_array_one = [12, 1234234, 5, 2345, 24, 5623, 46, 2546, 68798]
        test_array_two = [124, 5, 356, 3, 57, 35,
                          67, 356, 2, 647, 36, 5784, 8, 809]
        test_dict = {'test': test_array_one, 'asdaefd': test_array_two}
        self.message.append_data("{sax}", test_dict)

        self.message.seal()

        self.assertEqual(self.message.get_contents(), test_dict)

    def test_variant(self) -> None:
        test_signature = "x"
        test_int = 1241354
        self.message.open_container("v", test_signature)
        self.message.append_data("x", test_int)
        self.message.close_container()

        self.message.seal()

        self.assertEqual(self.message.get_contents(),
                         (test_signature, test_int))

    def test_array_of_variant(self) -> None:
        self.message.open_container("a", "v")

        test_signature_one = "x"
        test_int = 1241354
        self.message.open_container("v", test_signature_one)
        self.message.append_data("x", test_int)
        self.message.close_container()

        test_signature_two = "ai"
        test_array = [12, 1234234, 5, 2345, 24, 5623, 46, 2546, 68798]
        self.message.open_container("v", test_signature_two)
        self.message.open_container("a", "i")
        for i in test_array:
            self.message.append_data("i", i)
        self.message.close_container()
        self.message.close_container()

        self.message.close_container()

        self.message.seal()
        self.assertEqual(self.message.get_contents(),
                         [(test_signature_one, test_int),
                          (test_signature_two, test_array)
                          ])


if __name__ == "__main__":
    main()
