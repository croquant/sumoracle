import unittest

from .name import RikishiNameGenerator


class TestRikishiNameGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = RikishiNameGenerator()

    def test_transliterate(self):
        # Test transliteration of a Japanese name
        name_jp = "山田"
        expected_transliteration = "yamada"
        self.assertEqual(
            self.generator._RikishiNameGenerator__transliterate(name_jp),
            expected_transliteration,
        )

    def test_get_len(self):
        # Test the length of generated names
        for _ in range(100):
            length = len(self.generator.get())
            self.assertTrue(2 <= length <= 5)

    def test_fix_phonemes(self):
        # Test fixing phonemes in a name
        name = "samurai"
        expected_fixed_name = "ji"
        self.assertEqual(
            self.generator._RikishiNameGenerator__fix_phonemes(name),
            expected_fixed_name,
        )

    def test_check_no(self):
        # Test checking if a name contains "no" character
        valid_name_jp = "山田"
        invalid_name_jp = "山田の"
        self.assertTrue(
            self.generator._RikishiNameGenerator__check_no(valid_name_jp)
        )
        self.assertFalse(
            self.generator._RikishiNameGenerator__check_no(invalid_name_jp)
        )

    def test_check_valid(self):
        # Test checking if a name is valid
        valid_name = "yamada"
        valid_name_jp = "山田"
        invalid_name = "yamadano"
        invalid_name_jp = "山田の"
        self.assertTrue(
            self.generator._RikishiNameGenerator__check_valid(
                valid_name, valid_name_jp
            )
        )
        self.assertFalse(
            self.generator._RikishiNameGenerator__check_valid(
                invalid_name, invalid_name_jp
            )
        )


if __name__ == "__main__":
    unittest.main()
