import sys
import typing
import string
import secrets
import itertools
import random
# import pyperclip

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


class Options(object):
    @staticmethod
    def to_int(value : T, default: int) -> int:
        try:
            result = int(value)
        except TypeError:
            result = default
        finally:
            return result


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
            raise Exception('Values must meet: 0 <= PASS_MIN <= PASS_MAX')

    def __init__(self, **kwargs : Dict[str, T]):
        self.PASS_MIN = Options.to_int(kwargs.get('PASS_MIN', 0), 0)
        self.PASS_MAX = Options.to_int(kwargs.get('PASS_MAX', 0), 0)
        self.validate_pass_len(self.PASS_MIN, self.PASS_MAX)
        self.LETTERS_MIN = Options.to_int(kwargs.get('LETTERS_MIN', 0), 0)
        self.DIGITS_MIN = Options.to_int(kwargs.get('DIGITS_MIN', 0), 0)
        self.NO_NEXT_MATCH = Options.to_bool(kwargs.get('NO_NEXT_MATCH', False))
        self.PASS_LEN = random.choice(range(self.PASS_MIN, self.PASS_MAX)) if self.PASS_MIN != self.PASS_MAX else self.PASS_MIN

    @staticmethod
    def countUntil(items: Iterable[T], limit: int) -> (Dict, T, bool):
        dict_r = {}
        for i in items:
            counter = dict_r.get(i, 0) + 1
            dict_r[i] = counter
            if counter == limit:
                return dict_r, i, True
        return dict_r, i, False

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
    def countConsecutiveUntil(items: Iterable[T], limit: int) -> (Dict, T, bool):
        dict_r, count, item, found = {}, 1, None, False
        for a, b in PasswordConstraints.pairwise(items):
            if a == b:
                count += 1
            else:
                dict_r[a] = count
                count = 1
            if count == limit:
                dict_r[a], item, found = count, a, True
                break
        return dict_r, item, found

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

    @property
    def get_constraints(self) -> Iterable[Callable[Chars, bool]]:
        return [
            lambda passwd: sum(c.isdigit() for c in passwd) >= self.DIGITS_MIN,
            lambda passwd: sum(c.isalpha() for c in passwd) >= self.LETTERS_MIN,
            lambda passwd: PasswordConstraints.no_next_match(passwd) if self.NO_NEXT_MATCH else True,
        ]


class PasswordGeneratorOptions(Options):
    def __init__(self, **kwargs : Dict[str, T]):
        self.SECONDS_IN_CLIPBOARD = Options.to_int(kwargs.get('SECONDS_IN_CLIPBOARD', 10), 10)
        self.MAX_RETRY = Options.to_int(kwargs.get('MAX_RETRY', 10), 10)


class PasswordGenerator(object):
    @classmethod
    def from_dicts(cls, gen_opts: Dict[str, T], opts : Dict[str, T]):
        pass_gen = cls(PasswordGeneratorOptions(**gen_opts), PasswordConstraints(**opts))
        return pass_gen

    def __init__(self, gen_opts: PasswordGeneratorOptions, opts : PasswordConstraints):
        self.gen_opts = gen_opts
        self.opts = opts

    


mine = Alphabet.from_dict(CASE_SENSITIVE = True, INCLUDE_UPPER_CASE = True, INCLUDE_DIGITS = True, INCLUDE_CONSONANTS = True)
alphabet = mine.sub_alphabet


while True:
    
    password = ''.join(secrets.choice(alphabet) for i in range(PASS_LEN))
    if (sum(c.isdigit() for c in password) >= DIGITS_MIN
        and sum(c.isalpha() for c in password) >= LETTERS_MIN
        and no_next_match(password)
        ):
        break

try:
    pyperclip.copy(password)
    capture = pyperclip.paste()  # Capture paste and begin countdown
    try:
        print('Password generated and copied to clipboard')
        pyperclip.waitForNewPaste(SECONDS_IN_CLIPBOARD)
    except:
        pyperclip.copy('')
        pass
except:
    print('Password generated:\n{}'.format(password))

print('--Password-Generator end---')

# Todo:
# 3. Call functions and saved values only if needed
# 4. Change to check by conditions added instead of adding them by hand
# 5. Add params
# - argparse
# - sys, getopt
