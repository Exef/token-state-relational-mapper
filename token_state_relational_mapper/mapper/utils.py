def generate_block_ranges(starting_block, ending_block, range_size):
    if range_size == 0:
        return []

    start = int(starting_block)
    end_block_number = int(ending_block)
    while start + range_size <= end_block_number:
        end = start + range_size
        yield start, end
        start = end + 1
    yield start, end_block_number


def convert_to_real_value_string(number, decimals):
    real_number = number / 10 ** decimals
    return str(real_number)