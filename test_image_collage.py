import os
import tempfile
import unittest

from PIL import Image, ImageColor

from image_collage import LayoutParseError, combine_images


class ImageCollageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    @property
    def tmp_dir(self) -> str:
        return self._tmp_dir.name

    def _create_image(self, filename: str, size: tuple[int, int], colour: str) -> str:
        path = os.path.join(self.tmp_dir, filename)
        Image.new("RGB", size, colour).save(path)
        return path

    def test_long_layout_respects_spacing_and_margin(self) -> None:
        img1 = self._create_image("img1.png", (100, 50), "#CCCCCC")
        img2 = self._create_image("img2.png", (80, 100), "#333333")
        output_path = os.path.join(self.tmp_dir, "long.png")

        collage = combine_images(
            [img1, img2],
            layout="long",
            spacing=10,
            margin=5,
            background_colour="#123456",
            output_path=output_path,
        )

        self.assertEqual(collage.size, (110, 170))
        self.assertTrue(os.path.exists(output_path))

        margin_colour = collage.getpixel((2, 2))
        expected_colour = ImageColor.getcolor("#123456", "RGBA")
        self.assertEqual(margin_colour, expected_colour)

    def test_grid_layout_uses_background_colour_for_spacing(self) -> None:
        images = [
            self._create_image(f"grid_{idx}.png", (40, 40), "#FFFFFF")
            for idx in range(4)
        ]

        collage = combine_images(
            images,
            layout="2x2",
            spacing=10,
            background_colour="#FF0000",
        )

        self.assertEqual(collage.size, (90, 90))

        horizontal_gap_colour = collage.getpixel((45, 20))
        vertical_gap_colour = collage.getpixel((20, 45))
        expected_gap_colour = ImageColor.getcolor("#FF0000", "RGBA")
        self.assertEqual(horizontal_gap_colour, expected_gap_colour)
        self.assertEqual(vertical_gap_colour, expected_gap_colour)

    def test_background_image_takes_precedence_over_colour(self) -> None:
        image_path = self._create_image("single.png", (20, 20), "#FFFFFF")
        background_path = self._create_image("background.png", (10, 10), "#0000FF")

        collage = combine_images(
            [image_path],
            layout="long",
            spacing=0,
            margin=5,
            background_colour="#FF0000",
            background_image=background_path,
        )

        background_colour = collage.getpixel((2, 2))
        expected_colour = ImageColor.getcolor("#0000FF", "RGBA")
        self.assertEqual(background_colour, expected_colour)

    def test_invalid_layout_raises(self) -> None:
        image_path = self._create_image("single.png", (10, 10), "#FFFFFF")

        with self.assertRaises(LayoutParseError):
            combine_images([image_path], layout="invalid-layout")

    def test_negative_spacing_rejected(self) -> None:
        image_path = self._create_image("single.png", (10, 10), "#FFFFFF")

        with self.assertRaises(ValueError):
            combine_images([image_path], spacing=-1)


if __name__ == "__main__":
    unittest.main()
