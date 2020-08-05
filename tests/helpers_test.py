import string

from golem import helpers


class TestRandomFloat:

    def test_random_float(self):
        randfloat = helpers.random_float()
        assert isinstance(randfloat, float)
        assert 1.0 <= randfloat <= 100.0

        randfloat = helpers.random_float(-5.5, 5.5)
        assert -5.5 <= randfloat <= 5.5

        randfloat = helpers.random_float(5, 5)
        assert isinstance(randfloat, float)

        randfloat = helpers.random_float(min=1, max=2, decimals=3)
        assert len(str(randfloat)) <= 5

        randfloat = helpers.random_float(min=1, max=2, decimals=0)
        assert len(str(randfloat)) == 3  # either '1.0' or '2.0'


class TestRandomInt:

    def test_random_int(self):
        randint = helpers.random_int()
        assert 1 <= randint <= 100

        randint = helpers.random_int(-5, 5)
        assert -5 <= randint <= 5

        randint = helpers.random_int(-5.0, 5.0)
        assert isinstance(randint, int)


class TestRandomStr:

    def test_random_str(self):
        random_string = helpers.random_str()
        assert len(random_string) == 10
        assert all(c in string.ascii_lowercase for c in random_string)

    def test_random_str_length(self):
        random_string = helpers.random_str(length=0)
        assert len(random_string) == 0
        assert random_string == ''
        random_string = helpers.random_str(length=5)
        assert len(random_string) == 5

    def test_random_str_prefix_suffix(self):
        random_string = helpers.random_str(prefix='pre')
        assert random_string.startswith('pre')
        random_string = helpers.random_str(suffix='suf')
        assert random_string.endswith('suf')

    def test_random_str_sample(self):
        sample = ['a', 'b', 'c']
        random_string = helpers.random_str(sample=sample)
        assert all(c in sample for c in random_string)

        sample = ['LOWERCASE']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.ascii_lowercase for c in random_string)

        sample = ['UPPERCASE']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.ascii_uppercase for c in random_string)

        sample = ['DIGITS']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.digits for c in random_string)

        sample = ['SPECIAL']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.punctuation for c in random_string)

        sample = 'this is a string sample'
        random_string = helpers.random_str(sample=sample)
        assert all(c in sample for c in random_string)

        sample = ['LOWERCASE', 'DIGITS']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.ascii_lowercase or c in string.digits for c in random_string)

        sample = ['DIGITS', 'a', 'b', 'c']
        random_string = helpers.random_str(sample=sample)
        assert all(c in string.digits or c in ['a', 'b', 'c'] for c in random_string)

        sample = [1, 2, 3]
        random_string = helpers.random_str(sample=sample)
        assert all(c in ['1', '2', '3'] for c in random_string)
