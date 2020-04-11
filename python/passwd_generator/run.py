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


seqType = StrFromIterable


""" Castings """
def _chrs_to_ords(_chrs: Chars, seqType : Optional[Type] = None) -> Ords:
    if seqType is None:
        return (ord(c) for c in _chrs)
    else:
        return seqType(ord(c) for c in _chrs)

def _ords_to_chrs(_ords: Ords, seqType : Optional[Type] = None) -> Chars:
    if seqType is None:
        return (chr(o) for o in _ords)
    else:
        return seqType(chr(o) for o in _ords)

def _remove_from_sequence(_seq: Iterable[T], *args: Tuple[T], seqType : Optional[Type] = None) -> Iterable[T]:
    if seqType is None:
        return (e for e in _seq if e not in args)
    elif seqType == set:
        return set(_seq) - set(args)
    else:
        return seqType(e for e in _seq if e not in args)

# Rougly equivalent to itertools.chain
def chain(*iterables: Tuple[Iterable[T]]) -> Iterable[T]:
    for it in iterables:
        for element in it:
            yield element

""" Digits """
digits_chrs = string.digits

""" Lower case chars """
all_chars_lower = string.ascii_lowercase
vowels_chrs_lower = 'aeiou'
consonants_chars_lower = _remove_from_sequence(all_chars_lower,
                                               *vowels_chrs_lower, seqType=seqType)

""" Upper case chars """
all_chars_upper = string.ascii_uppercase
vowels_chrs_upper = 'AEIOU'
consonants_chars_upper = _remove_from_sequence(all_chars_upper,
                                               *vowels_chrs_upper, seqType=seqType)
other_chars = string.punctuation

""" Constraints
"""
SECONDS_IN_CLIPBOARD = 10
PASS_MIN = 8
PASS_MAX = 16
LETTERS_MIN = 4
DIGITS_MIN = 4

CASE_SENSITIVE = True
INCLUDE_LOWER_CASE = False
INCLUDE_UPPER_CASE = True
INCLUDE_DIGITS = True
INCLUDE_OTHERS = False
INCLUDE_VOWELS = False
INCLUDE_CONSONANTS = True
NO_NEXT_MATCH = True


def _concat(*_seqs: Tuple[Iterable[T]], seqType : Optional[Type] = None) -> Chars:
    if seqType is None:
        return itertools.chain(*_seqs)
    else:
        _r_seq = seqType()
        for _seq in _seqs:
            _r_seq += _seq
        return _r_seq

def emptyGen() -> Iterable[T]:
    return
    yield

def emptySeq(seqType : Optional[Type] = None) -> Iterable[T]:
    return emptyGen() if seqType is None else seqType()

def _alphabet(seqType : Optional[Type] = None) -> Chars:
    _alphabet_r, _empty_seq = emptySeq(seqType), emptySeq(seqType)
    if CASE_SENSITIVE:
        if INCLUDE_CONSONANTS and INCLUDE_VOWELS:
            _alphabet_r = _concat(
                _alphabet_r,
                all_chars_lower if INCLUDE_LOWER_CASE else _empty_seq,
                all_chars_upper if INCLUDE_UPPER_CASE else _empty_seq,
                digits_chrs if INCLUDE_DIGITS else _empty_seq,
                other_chars if INCLUDE_OTHERS else _empty_seq,
                seqType=seqType
            )
        elif INCLUDE_VOWELS:
            _alphabet_r = _concat(
                _alphabet_r,
                vowels_chrs_lower if INCLUDE_LOWER_CASE else _empty_seq,
                vowels_chrs_upper if INCLUDE_UPPER_CASE else _empty_seq,
                digits_chrs if INCLUDE_DIGITS else _empty_seq,
                other_chars if INCLUDE_OTHERS else _empty_seq,
                seqType=seqType
            )
        elif INCLUDE_CONSONANTS:
            _alphabet_r = _concat(
                _alphabet_r,
                consonants_chars_lower if INCLUDE_LOWER_CASE else _empty_seq,
                consonants_chars_upper if INCLUDE_UPPER_CASE else _empty_seq,
                digits_chrs if INCLUDE_DIGITS else _empty_seq,
                other_chars if INCLUDE_OTHERS else _empty_seq,
                seqType=seqType
            )
    elif INCLUDE_LOWER_CASE or INCLUDE_UPPER_CASE:
        _alphabet_r = _concat(
            _alphabet_r,
            vowels_chrs_lower if INCLUDE_VOWELS else _empty_seq,
            consonants_chars_lower if INCLUDE_CONSONANTS else _empty_seq,
            digits_chrs if INCLUDE_DIGITS else _empty_seq,
            other_chars if INCLUDE_OTHERS else _empty_seq,
            seqType=seqType
        )
    return _alphabet_r

def no_next_match(password: Chars) -> bool:
    if NO_NEXT_MATCH:
        comp_tuple = zip(password, password[1:])
        return not any(i[0] == i[1] for i in comp_tuple)
    else:
        return True

def countUntil(items: Iterable[T], limit: int) -> (Dict, T, bool):
    dict_r = {}
    for i in items:
        counter = dict_r.get(i, 0) + 1
        dict_r[i] = counter
        if counter == limit:
            return dict_r, i, True
    return dict_r, i, False

def countConsecutiveUntil_M1(items: Sequence[T], limit: int) -> (Dict, T, bool):
    dict_r, count, item, found = {}, 1, None, False
    if len(items) > 1:
        for i in range(1, len(items)):
            if items[i-1] == items[i]:
                count += 1
            else:
                dict_r[items[i-1]] = count
                count = 1
            if count == limit:
                item = items[i-1]
                dict_r[item], found = count, True
                break
    elif len(items) == 1:
        item = items[0]
        dict_r[item], found = count, True if limit == 1 else False
    return dict_r, item, found


def pairwise(iterable):
    """iterates pairwise without holding an extra copy of iterable in memory"""
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.zip_longest(a, b, fillvalue=None)

def countConsecutiveUntil(items: Iterable[T], limit: int) -> (Dict, T, bool):
    dict_r, count, item, found = {}, 1, None, False
    for a, b in pairwise(items):
        if b is not None and a == b:
            count += 1
        else:
            dict_r[a] = count
            count = 1
        if count == limit:
            dict_r[a], item, found = count, a, True
            break
    return dict_r, item, found

alphabet = _alphabet(seqType=seqType)


print('Alphabet used:\n{}'.format(alphabet))

while True:
    PASS_LEN = random.choice(range(PASS_MIN, PASS_MAX))
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
