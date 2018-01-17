def generate_block_ranges(starting_block, ending_block, range_size):
    if range_size == 0:
        return []

    start = starting_block
    while start + range_size <= ending_block:
        end = start + range_size
        yield start, end
        start = end + 1
    yield start, ending_block
