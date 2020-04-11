import sys
import typing
import string
import secrets
import itertools
import random
import pyperclip

""" Types """
T = typing.T  # Can be anything
Type = typing.Type
Tuple = typing.Tuple
Dict = typing.Dict
Sequence = typing.Sequence
Iterable = typing.Iterable
Optional = typing.Optional
NoReturn = typing.NoReturn
Callable = typing.Callable
Chars = Iterable[str]
Ords = Iterable[int]

class StrFromIterable(str):
    def __new__(cls, *args):
        super(StrFromIterable, cls).__new__(cls, *args)
        value = ''
        for arg in args:
            if isinstance(arg, Iterable):
                value += ''.join(map(str, (i for i in arg)))
            else:
                value += str(arg)
        return value


def emptyGen() -> Iterable[T]:
    return
    yield

def emptySeq(seqType : Optional[Type] = None) -> Iterable[T]:
    return emptyGen() if seqType is None else seqType()


class Options(object):
    @staticmethod
    def to_uint(value : T, default: int) -> int:
        default = default if default > 0 else 0
        try:
            result = int(value)
            result = result
        except TypeError:
            result = default
        finally:
            return result if result > 0 else default

    @staticmethod
    def to_bool(value : T) -> bool:
        return 'true' == value.lower() if isinstance(value, str) else bool(value)

class AlphabetOptions(Options):
    def __init__(self, **kwargs : Dict[str, T]):
        self.CASE_SENSITIVE = Options.to_bool(kwargs.get('CASE_SENSITIVE', False))
        self.INCLUDE_LOWER_CASE = Options.to_bool(kwargs.get('INCLUDE_LOWER_CASE', False))
        self.INCLUDE_UPPER_CASE = Options.to_bool(kwargs.get('INCLUDE_UPPER_CASE', False))
        self.INCLUDE_DIGITS = Options.to_bool(kwargs.get('INCLUDE_DIGITS', False))
        self.INCLUDE_OTHERS = Options.to_bool(kwargs.get('INCLUDE_OTHERS', False))
        self.INCLUDE_VOWELS = Options.to_bool(kwargs.get('INCLUDE_VOWELS', False))
        self.INCLUDE_CONSONANTS = Options.to_bool(kwargs.get('INCLUDE_CONSONANTS', False))


class Alphabet(object):
    seqType = StrFromIterable

    """ METHODS """
    @staticmethod
    def _chrs_to_ords(_chrs: Chars, seqType : Optional[Type] = seqType) -> Ords:
        if seqType is None:
            return (ord(c) for c in _chrs)
        else:
            return seqType(ord(c) for c in _chrs)

    @staticmethod
    def _ords_to_chrs(_ords: Ords, seqType : Optional[Type] = seqType) -> Chars:
        if seqType is None:
            return (chr(o) for o in _ords)
        else:
            return seqType(chr(o) for o in _ords)

    @staticmethod
    def _remove_from_sequence(_seq: Iterable[T], *args: Tuple[T], seqType : Optional[Type] = seqType) -> Iterable[T]:
        if seqType is None:
            return (e for e in _seq if e not in args)
        elif seqType == set:
            return set(_seq) - set(args)
        else:
            return seqType(e for e in _seq if e not in args)

    # Rougly equivalent to itertools.chain
    @staticmethod
    def _chain(*iterables: Tuple[Iterable[T]]) -> Iterable[T]:
        for it in iterables:
            for element in it:
                yield element


class Alphabet(object):
    """Valid symbols/chars for passwords"""
    seqType = Alphabet.seqType

    #- Digit chars
    digits_chrs = string.digits
    #- Lower case chars
    all_chars_lower = string.ascii_lowercase
    vowels_chrs_lower = 'aeiou'
    consonants_chars_lower = Alphabet._remove_from_sequence(all_chars_lower,
                                                            *vowels_chrs_lower,
                                                            seqType=seqType)
    #- Upper case chars
    all_chars_upper = string.ascii_uppercase
    vowels_chrs_upper = 'AEIOU'
    consonants_chars_upper = Alphabet._remove_from_sequence(all_chars_upper,
                                                            *vowels_chrs_upper,
                                                            seqType=seqType)
    #- Other chars
    other_chars = string.punctuation

    #- Restore previous static methods
    _chrs_to_ords = staticmethod(Alphabet._chrs_to_ords)
    _ords_to_chrs = staticmethod(Alphabet._ords_to_chrs)
    _remove_from_sequence = staticmethod(Alphabet._remove_from_sequence)
    _chain = staticmethod(itertools.chain)  # Alphabet._chain

    #- New static methods
    @staticmethod
    def _concat(*_seqs : Tuple[Iterable[T]], seqType : Optional[Type] = seqType) -> Chars:
        if seqType is None:
            return _chain(*_seqs)
        else:
            _r_seq = seqType()
            for _seq in _seqs:
                _r_seq += _seq
            return _r_seq

    @staticmethod
    def _alphabet(opts : AlphabetOptions, seqType : Optional[Type] = seqType) -> Chars:
        _alphabet_r, _empty_seq = emptySeq(seqType), emptySeq(seqType)
        if opts.CASE_SENSITIVE:
            _alphabet_r = Alphabet._concat(
                _alphabet_r,

                Alphabet.all_chars_lower if opts.INCLUDE_LOWER_CASE and opts.INCLUDE_VOWELS and opts.INCLUDE_CONSONANTS else \
                Alphabet.vowels_chrs_lower if opts.INCLUDE_LOWER_CASE and opts.INCLUDE_VOWELS else \
                Alphabet.consonants_chars_lower if opts.INCLUDE_LOWER_CASE and opts.INCLUDE_CONSONANTS else \
                _empty_seq,

                Alphabet.all_chars_upper if opts.INCLUDE_UPPER_CASE and opts.INCLUDE_VOWELS and opts.INCLUDE_CONSONANTS else \
                Alphabet.vowels_chrs_upper if opts.INCLUDE_UPPER_CASE and opts.INCLUDE_VOWELS else \
                Alphabet.consonants_chars_upper if opts.INCLUDE_UPPER_CASE and opts.INCLUDE_CONSONANTS else \
                _empty_seq,

                Alphabet.digits_chrs if opts.INCLUDE_DIGITS else _empty_seq,
                Alphabet.other_chars if opts.INCLUDE_OTHERS else _empty_seq,
                seqType=seqType
            )
        else:
            _alphabet_r = Alphabet._concat(
                _alphabet_r,

                Alphabet.all_chars_lower if opts.INCLUDE_VOWELS and opts.INCLUDE_CONSONANTS else \
                Alphabet.vowels_chrs_lower if opts.INCLUDE_VOWELS else \
                Alphabet.consonants_chars_lower if opts.INCLUDE_CONSONANTS else \
                _empty_seq,

                Alphabet.digits_chrs if opts.INCLUDE_DIGITS else _empty_seq,
                Alphabet.other_chars if opts.INCLUDE_OTHERS else _empty_seq,
                seqType=seqType
            )
        return _alphabet_r

    @classmethod
    def from_dict(cls, **kwargs : Dict[str, T]):
        opts = AlphabetOptions(**kwargs)
        alphabet = cls(opts)
        return alphabet

    def __init__(self, opts : AlphabetOptions):
        self._sub_alphabet = Alphabet._alphabet(opts, Alphabet.seqType)

    @property
    def sub_alphabet(self):
        return self._sub_alphabet


class PasswordConstraints(Options):
    @staticmethod
    def validate_pass_len(pass_min : int, pass_max: int) -> NoReturn:
        if 0 > pass_min or pass_min > pass_max:
            raise Exception('Values must meet: 0 <= min <= max')

    @staticmethod
    def validate_group(group_min : int, group_max: int, chars_max: int, non_group: int) -> NoReturn:
        if 0 > group_min or group_min > group_max or group_max+non_group > chars_max:
            raise Exception('Values must meet: 0 <= min <= max and max+others <= max_chars')

    def __init__(self, **kwargs : Dict[str, T]):
        self.PASS_MIN = Options.to_uint(kwargs.get('PASS_MIN'), 0)
        self.PASS_MAX = Options.to_uint(kwargs.get('PASS_MAX'), self.PASS_MIN)
        self.validate_pass_len(self.PASS_MIN, self.PASS_MAX)
        self.PASS_LEN = random.choice(range(self.PASS_MIN, self.PASS_MAX)) if self.PASS_MIN != self.PASS_MAX else self.PASS_MIN

        self.LETTERS_MIN = Options.to_uint(kwargs.get('LETTERS_MIN'), 0)
        self.LETTERS_MAX = Options.to_uint(kwargs.get('LETTERS_MAX'), self.LETTERS_MIN)  #LETTERS_MIN
        self.DIGITS_MIN = Options.to_uint(kwargs.get('DIGITS_MIN'), 0)
        self.DIGITS_MAX = Options.to_uint(kwargs.get('DIGITS_MAX'), self.DIGITS_MIN)  #DIGITS_MIN
        self.OTHERS_MIN = Options.to_uint(kwargs.get('OTHERS_MIN'), 0)
        self.OTHERS_MAX = Options.to_uint(kwargs.get('OTHERS_MAX'), self.OTHERS_MIN)  #OTHERS_MIN

        self.validate_group(self.LETTERS_MIN, self.LETTERS_MAX, self.PASS_MAX, self.DIGITS_MAX + self.OTHERS_MAX)
        self.validate_group(self.DIGITS_MIN, self.DIGITS_MAX, self.PASS_MAX, self.LETTERS_MAX + self.OTHERS_MAX)
        self.validate_group(self.OTHERS_MIN, self.OTHERS_MAX, self.PASS_MAX, self.LETTERS_MAX + self.DIGITS_MAX)
        self.NO_NEXT_MATCH = Options.to_bool(kwargs.get('NO_NEXT_MATCH', False))

    @staticmethod
    def pairwise(iterable: Iterable[T]) -> Iterable[Tuple[T]]:
        """iterates pairwise without holding an extra copy of iterable in memory"""
        a, b = itertools.tee(iterable)  # Create copy of iterable
        next(b, None)  # Move b iterable to next
        return itertools.zip_longest(a, b, fillvalue=None)

    @staticmethod
    def no_next_match(password: Chars) -> bool:
        return not any(a == b for a,b in PasswordConstraints.pairwise(password))

    @staticmethod
    def isDigit(value: str) -> bool:
        return value.isdigit()

    @staticmethod
    def isLetter(value: str) -> bool:
        return value.isalpha()

    @staticmethod
    def isLower(value: str) -> bool:
        return value.islower()

    @staticmethod
    def isUpper(value: str) -> bool:
        return value.isupper()

    @staticmethod
    def isOther(value: str) -> bool:
        return not value.isalnum() and not value.isspace()

    @staticmethod
    def countGroup(value: str, dict_r: Dict[str, int]) -> Dict[str, int]:
        if PasswordConstraints.isLetter(value):
            dict_r['letters'] = dict_r.get('letters', 0) + 1
            dict_r['lowers'] = dict_r.get('lowers', 0) + int(PasswordConstraints.isLower(value))
            dict_r['uppers'] = dict_r.get('uppers', 0) + int(PasswordConstraints.isUpper(value))
        else:
            dict_r['digits'] = dict_r.get('digits', 0) + int(PasswordConstraints.isDigit(value))
            dict_r['others'] = dict_r.get('others', 0) + int(PasswordConstraints.isOther(value))
        return dict_r

    @staticmethod
    def countGroups(items: Chars) -> Dict[str, int]:
        dict_r = {}
        for i in items:
            dict_r = PasswordConstraints.countGroup(i, dict_r)
        return dict_r

    @staticmethod
    def group_between_min_max(vmin: int, v: int, vmax: int) -> bool:
        return (vmin <= v) if vmin == vmax else (vmin <= v <= vmax)

    def check(self, passwd: str) -> Iterable[bool]:
        countedGroups = PasswordConstraints.countGroups(passwd)
        return [
            PasswordConstraints.no_next_match(passwd) if self.NO_NEXT_MATCH else True,
            PasswordConstraints.group_between_min_max(self.DIGITS_MIN, countedGroups.get('digits', 0), self.DIGITS_MAX),
            PasswordConstraints.group_between_min_max(self.LETTERS_MIN, countedGroups.get('letters', 0), self.LETTERS_MAX),
            PasswordConstraints.group_between_min_max(self.OTHERS_MIN, countedGroups.get('others', 0), self.OTHERS_MAX),
        ]


class PasswordGeneratorOptions(Options):
    def __init__(self, **kwargs : Dict[str, T]):
        self.SECONDS_IN_CLIPBOARD = Options.to_uint(kwargs.get('SECONDS_IN_CLIPBOARD'), 10)
        self.MAX_RETRY = Options.to_uint(kwargs.get('MAX_RETRY'), 100)


class PasswordGenerator(object):
    seqType = StrFromIterable

    @classmethod
    def from_dicts(cls, gen_opts: Dict[str, T], opts : Dict[str, T]):
        pass_gen = cls(PasswordGeneratorOptions(**gen_opts), PasswordConstraints(**opts))
        return pass_gen

    def __init__(self, gen_opts: PasswordGeneratorOptions, opts : PasswordConstraints, alphabet: Chars):
        self.gen_opts = gen_opts
        self.opts = opts
        self.alphabet = alphabet
        self.password = None
        self.valid = False

    def generate(self, seqType : Optional[Type] = seqType) -> (Iterable[T], bool):
        i = 0
        while True:
            if seqType is None:
                password = (secrets.choice(self.alphabet) for i in range(self.opts.PASS_LEN))
            else:
                password = seqType(secrets.choice(self.alphabet) for i in range(self.opts.PASS_LEN))
            valid = all(self.opts.check(password))
            i += 1
            if valid or i == self.gen_opts.MAX_RETRY:
                break
        self.valid = valid
        self.password = password
        return password, valid

    def deliver(self) -> NoReturn:
        if not self.valid:
            raise Exception('Sorry, could not find any valid password for your options.')
        else:
            try:
                pyperclip.copy(self.password)
                capture = pyperclip.paste()  # Capture paste and begin countdown
                try:
                    print('Password generated and copied to clipboard')
                    pyperclip.waitForNewPaste(self.gen_opts.SECONDS_IN_CLIPBOARD)
                except:
                    pyperclip.copy('')
                    pass
            except:
                print('Password generated:\n{}'.format(self.password))
            finally:
                self.password = ''
                self.valid = False
                print('--Password-Generator end---')


mine = Alphabet.from_dict(CASE_SENSITIVE = True, INCLUDE_UPPER_CASE = True, INCLUDE_DIGITS = True, INCLUDE_CONSONANTS = True, INCLUDE_OTHERS = True)
alphabet = mine.sub_alphabet
print(alphabet)

passwd_gen = PasswordGenerator(PasswordGeneratorOptions(),
                               PasswordConstraints(PASS_MIN=8, PASS_MAX=16,
                                                   LETTERS_MIN=4,
                                                   DIGITS_MIN=4,
                                                   OTHERS_MIN=0,
                                                   NO_NEXT_MATCH = True),
                               alphabet)
passwd_gen.generate()
passwd_gen.deliver()


# Todo:
# 4. Change to check by conditions added instead of adding them by hand
# 5. Add params
# - argparse
# - sys, getopt
# 6. Add if options are valid and could generate a password
