from token_state_relational_mapper.mapper.utils import generate_block_ranges

def generate(start, end, size):
    ranges = []
    for r in generate_block_ranges(start, end, size):
        ranges.append(r)
    return ranges


def test_generate_block_ranges_returns_all_ranges():
    assert [(0, 3), (4, 7), (8, 10)] == generate(0, 10, 3)


def test_generate_block_ranges_always_returns_smallest_range():
    assert generate(0, 1, 2) == [(0,1)]


def test_generate_block_ranges_always_returns_start_and_end():
    start = 1000
    end = 2001
    ranges = generate(start, end, 100)
    assert len(ranges) == 10
    assert start, 1100 == ranges[1]
    assert 2000, end == ranges[-1]


def test_generate_block_ranges_returns_empty_list_when_range_is_zero():
    assert [] == generate(1, 10, 0)