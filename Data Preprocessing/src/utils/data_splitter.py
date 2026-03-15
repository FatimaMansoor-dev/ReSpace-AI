import numpy as np

def train_test_split(records: list, test_size: float = 0.2, shuffle: bool = True, random_seed: int = 42):
    """
    Splits records into train and test sets.

    Args:
        records    : Full list of records (e.g. dicts from Supabase)
        test_size  : Fraction of data for test set (default 0.2 → 80/20 split)
        shuffle    : Whether to shuffle before splitting (default True)
        random_seed: Seed for reproducibility (default 42)

    Returns:
        train_records, test_records
    """
    if not records:
        raise ValueError("Records list is empty.")

    if not (0.0 < test_size < 1.0):
        raise ValueError("test_size must be between 0 and 1.")

    data = records.copy()

    if shuffle:
        rng = np.random.default_rng(random_seed)
        rng.shuffle(data)

    split_index = int(len(data) * (1 - test_size))

    train_records = data[:split_index]
    test_records  = data[split_index:]

    print(f"Total: {len(data)} | Train: {len(train_records)} | Test: {len(test_records)}")

    return train_records, test_records
