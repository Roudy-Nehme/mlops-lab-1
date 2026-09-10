from pathlib import Path
from PIL import Image

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

CATEGORIES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

SPLITS = ["training", "evaluation", "validation"]
IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100


def get_category(filename):
    category_number = filename.split("_")[0]
    return CATEGORIES.get(category_number)


def process_dataset():
    for split in SPLITS:
        source_folder = RAW_DIR / split
        counters = {category: 0 for category in CATEGORIES.values()}

        for image_path in source_folder.iterdir():
            if not image_path.is_file():
                continue

            category = get_category(image_path.name)

            if category is None:
                continue

            processed_folder = PROCESSED_DIR / split / category
            mini_folder = MINI_DIR / split / category

            processed_folder.mkdir(parents=True, exist_ok=True)
            mini_folder.mkdir(parents=True, exist_ok=True)

            with Image.open(image_path) as image:
                image = image.convert("RGB")
                image = image.resize(IMAGE_SIZE)

                image.save(processed_folder / image_path.name)

                if counters[category] < MINI_LIMIT:
                    image.save(mini_folder / image_path.name)
                    counters[category] += 1

    print("Food-11 processing completed.")


if __name__ == "__main__":
    process_dataset()