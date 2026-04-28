import re
from abc import ABC, abstractmethod
import copy
from typing import Literal


class MetaChar:
    ESCAPED = (r'\.', r'\*', r'\+', r'\?', r'\^', r'\$', r'\|', r'\(', r'\)', r'\{', r'\}', r'\\')
    RAW = ('.', '*', '+', '?', '^', '$', '|', '(', ')', '{', '}', '\\')
    CHAR_SET = ('^', ']', '-', '\\')


class IElem(ABC):
    @abstractmethod
    def zero_or_more(self):
        pass

    @abstractmethod
    def one_or_more(self):
        pass

    @abstractmethod
    def zero_or_one(self):
        pass

    @abstractmethod
    def repeat(self, times):
        pass

    @abstractmethod
    def repeat_range(self, min_times, max_times=None):
        pass

    @property
    @abstractmethod
    def ignore_case(self):
        pass

    @property
    @abstractmethod
    def dot_all(self):
        pass

    @property
    @abstractmethod
    def multiline(self):
        pass

    @property
    @abstractmethod
    def close_ignore_case(self):
        pass

    @property
    @abstractmethod
    def close_dot_all(self):
        pass

    @property
    @abstractmethod
    def close_multiline(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __add__(self, other) -> IElem:
        return CombineElem(f"{str(self)}{ElemFactory.create(other)}")

    def __radd__(self, other) -> IElem:
        return CombineElem(f"{ElemFactory.create(other)}{str(self)}")

    def to_regex(self):
        return Regexp(str(self))


class Elem(IElem):

    def __init__(self, content: str):
        self.__content = ''.join(['\\' + char if char in MetaChar.RAW else char for char in content])

    def zero_or_more(self):
        if len(self.__content) == 1 or self.__content in MetaChar.ESCAPED:
            return ElemWithOp(f"{self.__content}*")
        else:
            return ElemWithOp(f"(?:{self.__content})*")

    def one_or_more(self):
        if len(self.__content) == 1 or self.__content in MetaChar.ESCAPED:
            return ElemWithOp(f"{self.__content}+")
        else:
            return ElemWithOp(f"(?:{self.__content})+")

    def zero_or_one(self):
        if len(self.__content) == 1 or self.__content in MetaChar.ESCAPED:
            return ElemWithOp(f"{self.__content}?")
        else:
            return ElemWithOp(f"(?:{self.__content})?")

    def repeat(self, times):
        if len(self.__content) == 1 or self.__content in MetaChar.ESCAPED:
            return ElemWithOp(f"{self.__content}{{{times}}}")
        else:
            return ElemWithOp(f"(?:{self.__content}){{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        if len(self.__content) == 1 or self.__content in MetaChar.ESCAPED:
            return ElemWithOp(f"{self.__content}{{{min_times},{max_times}}}")
        else:
            return ElemWithOp(f"(?:{self.__content}){{{min_times},{max_times}}}")

    @property
    def ignore_case(self):
        return Group(self).ignore_case

    @property
    def dot_all(self):
        return Group(self).dot_all

    @property
    def multiline(self):
        return Group(self).multiline

    @property
    def close_ignore_case(self):
        return Group(self).close_ignore_case

    @property
    def close_dot_all(self):
        return Group(self).close_dot_all

    @property
    def close_multiline(self):
        return Group(self).close_multiline

    def __str__(self):
        return self.__content


class Group(IElem):

    def __init__(self, *content: str | int | IElem):
        self.__content = []

        self.__is_non_catch = False

        self.__is_ignore_case = False
        self.__is_dot_all = False
        self.__is_multiline = False

        self.__is_close_ignore_case = False
        self.__is_close_dot_all = False
        self.__is_close_multiline = False

        self.__non_catch_prop = ""

        for e in content:
            self.__content.append(ElemFactory.create(e))

    def __update_non_catch_prop(self):
        if any([self.__is_non_catch
                   , self.__is_ignore_case, self.__is_dot_all, self.__is_multiline
                   , self.__is_close_ignore_case, self.__is_close_dot_all, self.__is_close_multiline]):
            non_catch_prop_list = ['', '', '']

            if self.__is_close_ignore_case:
                non_catch_prop_list[0] = '-i'
            if self.__is_ignore_case:
                non_catch_prop_list[0] = 'i'
            if self.__is_close_dot_all:
                non_catch_prop_list[1] = '-s'
            if self.__is_dot_all:
                non_catch_prop_list[1] = 's'
            if self.__is_close_multiline:
                non_catch_prop_list[2] = '-m'
            if self.__is_multiline:
                non_catch_prop_list[2] = 'm'

            self.__non_catch_prop = f"?{''.join(non_catch_prop_list)}:"
        else:
            self.__non_catch_prop = ''

    def zero_or_more(self):
        return ElemWithOp(f"({self.__non_catch_prop}{'|'.join(self.__content)})*")

    def one_or_more(self):
        return ElemWithOp(f"({self.__non_catch_prop}{'|'.join(self.__content)})+")

    def zero_or_one(self):
        return ElemWithOp(f"({self.__non_catch_prop}{'|'.join(self.__content)})?")

    def repeat(self, times):
        return ElemWithOp(f"({self.__non_catch_prop}{'|'.join(self.__content)}){{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        return ElemWithOp(f"({self.__non_catch_prop}{'|'.join(self.__content)}){{{min_times},{max_times}}}")

    @property
    def non_catch(self):
        new = copy.deepcopy(self)
        new.__is_non_catch = True
        new.__update_non_catch_prop()
        return new

    @property
    def ignore_case(self):
        new = copy.deepcopy(self)
        new.__is_ignore_case = True
        new.__update_non_catch_prop()
        return new

    @property
    def dot_all(self):
        new = copy.deepcopy(self)
        new.__is_dot_all = True
        new.__update_non_catch_prop()
        return new

    @property
    def multiline(self):
        new = copy.deepcopy(self)
        new.__is_multiline = True
        new.__update_non_catch_prop()
        return new

    @property
    def close_ignore_case(self):
        new = copy.deepcopy(self)
        new.__is_close_ignore_case = True
        new.__update_non_catch_prop()
        return new

    @property
    def close_dot_all(self):
        new = copy.deepcopy(self)
        new.__is_close_dot_all = True
        new.__update_non_catch_prop()
        return self

    @property
    def close_multiline(self):
        new = copy.deepcopy(self)
        new.__is_close_multiline = True
        new.__update_non_catch_prop()
        return new

    def __str__(self):
        return f"({self.__non_catch_prop}{'|'.join([str(elem) for elem in self.__content])})"


class ElemWithOp(IElem):

    def __init__(self, content: str):
        self.__content = content

    def zero_or_more(self):
        return ElemWithOp(f"(?:{self.__content})*")

    def one_or_more(self):
        return ElemWithOp(f"(?:{self.__content})+")

    def zero_or_one(self):
        return ElemWithOp(f"(?:{self.__content})?")

    def repeat(self, times):
        return ElemWithOp(f"(?:{self.__content}){{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        return ElemWithOp(f"(?:{self.__content}){{{min_times},{max_times}}}")

    @property
    def ignore_case(self):
        return Group(self).ignore_case

    @property
    def dot_all(self):
        return Group(self).dot_all

    @property
    def multiline(self):
        return Group(self).multiline

    @property
    def close_ignore_case(self):
        return Group(self).close_ignore_case

    @property
    def close_dot_all(self):
        return Group(self).close_dot_all

    @property
    def close_multiline(self):
        return Group(self).close_multiline

    def __str__(self):
        return self.__content


class ElemFactory:
    @staticmethod
    def create(content) -> IElem:
        if isinstance(content, str):
            return Elem(content)
        elif isinstance(content, int):
            return Elem(str(content))
        elif isinstance(content, list):
            return CharSet(*content)
        elif isinstance(content, tuple):
            return Group(*content)
        elif any([isinstance(content, IElem), isinstance(content, Assert), isinstance(content, Flag)]):
            return content
        else:
            raise TypeError("Unsupported type for this function: " + str(type(content)))


class Regexp:
    def __init__(self, expr: str):
        self.__expr = expr

    def test(self, *examples: str) -> dict[str, bool]:
        pattern = re.compile(self.__expr)

        results = {}

        for example in examples:
            results[example] = pattern.fullmatch(example) is not None

        return results

    def __str__(self):
        return self.__expr


class CombineElem(IElem):

    def __init__(self, content):
        self.__content = content

    def zero_or_more(self):
        return ElemWithOp(f"(?:{self.__content})*")

    def one_or_more(self):
        return ElemWithOp(f"(?:{self.__content})+")

    def zero_or_one(self):
        return ElemWithOp(f"(?:{self.__content})?")

    def repeat(self, times):
        return ElemWithOp(f"(?:{self.__content}){{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        return ElemWithOp(f"(?:{self.__content}){{{min_times},{max_times}}}")

    @property
    def ignore_case(self):
        return Group(self).ignore_case

    @property
    def dot_all(self):
        return Group(self).dot_all

    @property
    def multiline(self):
        return Group(self).multiline

    @property
    def close_ignore_case(self):
        return Group(self).close_ignore_case

    @property
    def close_dot_all(self):
        return Group(self).close_dot_all

    @property
    def close_multiline(self):
        return Group(self).close_multiline

    def __str__(self):
        return self.__content


class CharRange:
    def __init__(self, _from: str | int, _to: str | int):

        from_str = str(_from)
        to_str = str(_to)

        if len(from_str) != 1:
            raise ValueError(f"Range 'from' must be a single character, got: {from_str}")
        if len(to_str) != 1:
            raise ValueError(f"Range 'to' must be a single character, got: {to_str}")

        if ord(from_str) > ord(to_str):
            raise ValueError(f"Invalid range: {from_str}-{to_str}. Start must be <= End.")

        self.__content = f"{_from}-{_to}"

    def __str__(self):
        return self.__content

    def __add__(self, other: CharRange):
        if isinstance(other, CharRange):
            return CombinedCharRange(self, other)
        else:
            raise TypeError(f"Invalid char type: {type(other)}")


class CombinedCharRange:
    def __init__(self, *content: CharRange | CombinedCharRange):
        self.__content = ''.join([str(elem) for elem in content])

    def __str__(self):
        return self.__content

    def __add__(self, other: CharRange | CombinedCharRange):
        if isinstance(other, CharRange):
            return CombinedCharRange(self, other)
        else:
            raise TypeError(f"Invalid char type: {type(other)}")


class CharSet(IElem):
    def to_regex(self):
        return Regexp(str(self))

    def __init__(self, *chars: str | int | CharRange | CombinedCharRange):
        self.__chars = []
        for e in chars:
            if isinstance(e, str) or isinstance(e, int):
                for c in str(e):
                    if c in MetaChar.CHAR_SET:
                        self.__chars.append('\\' + c)
                    else:
                        self.__chars.append(c)
            elif isinstance(e, CharRange) or isinstance(e, CombinedCharRange):
                self.__chars.append(str(e))

        self.__is_negated = False

        self.__char_set_prop = ""

    def __update_char_set_prop(self):
        if self.__is_negated:
            self.__char_set_prop = "^"

    def zero_or_more(self):
        return ElemWithOp(f"[{self.__char_set_prop}{''.join(self.__chars)}]*")

    def one_or_more(self):
        return ElemWithOp(f"[{self.__char_set_prop}{''.join(self.__chars)}]+")

    def zero_or_one(self):
        return ElemWithOp(f"[{self.__char_set_prop}{''.join(self.__chars)}]?")

    def repeat(self, times):
        return ElemWithOp(f"[{self.__char_set_prop}{''.join(self.__chars)}]{{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        return ElemWithOp(f"[{self.__char_set_prop}{''.join(self.__chars)}]{{{min_times},{max_times}}}")

    @property
    def ignore_case(self):
        return Group(self).ignore_case

    @property
    def dot_all(self):
        return Group(self).dot_all

    @property
    def multiline(self):
        return Group(self).multiline

    @property
    def close_ignore_case(self):
        return Group(self).close_ignore_case

    @property
    def close_dot_all(self):
        return Group(self).close_dot_all

    @property
    def close_multiline(self):
        return Group(self).close_multiline

    @property
    def negated(self):
        new = CharSet(*self.__chars)
        new.__is_negated = True
        new.__update_char_set_prop()

        return new

    def __str__(self):
        return f"[{self.__char_set_prop}{''.join(self.__chars)}]"

    def __invert__(self):
        new = CharSet(*self.__chars)
        new.__is_negated = not self.__is_negated
        new.__update_char_set_prop()
        return new


class Anchor:
    @staticmethod
    def look_right():
        return Assert("right")

    @staticmethod
    def look_left():
        return Assert("left")

    @staticmethod
    def start_with():
        return Flag('^')

    @staticmethod
    def end_with():
        return Flag('$')


class Assert:
    def __init__(self, right_or_left: Literal["right", "left"]):
        self.__rule_symbol = {
            "right": {
                "must": "?=",
                "cant": "?!"
            },
            "left": {
                "must": "?<=",
                "cant": "?<!"
            }
        }
        self.__content = None
        self.__must_or_cant = None
        self.__right_or_left = right_or_left

    def must_be(self, content):
        new = copy.deepcopy(self)
        new.__must_or_cant = "must"
        new.__content = ElemFactory.create(content)
        return new

    def cant_be(self, content):
        new = copy.deepcopy(self)
        new.__must_or_cant = "cant"
        new.__content = ElemFactory.create(content)
        return new

    def __str__(self):
        return f"({self.__rule_symbol[self.__right_or_left][self.__must_or_cant]}{self.__content})"

    def __add__(self, other):
        return CombineElem(f"{self}{ElemFactory.create(other)}")

    def __radd__(self, other):
        return CombineElem(f"{ElemFactory.create(other)}{self}")


class Flag:
    def __init__(self, content: str):
        self.__content = content

    def __str__(self):
        return self.__content

    def __add__(self, other):
        return CombineElem(f"{self}{ElemFactory.create(other)}")

    def __radd__(self, other):
        return CombineElem(f"{ElemFactory.create(other)}{self}")


class Prop:
    def __init__(self):
        self.__start_anchor = ''
        self.__end_anchor = ''

        self.__ignore_case = False
        self.__dot_all = False
        self.__multiline = False

        self.__non_catch_prop = ''

    def __update_non_catch_prop(self):
        if any([self.__ignore_case, self.__dot_all, self.__multiline]):
            non_catch_prop_list = []
            if self.__ignore_case:
                non_catch_prop_list.append('i')
            if self.__dot_all:
                non_catch_prop_list.append('s')
            if self.__multiline:
                non_catch_prop_list.append('m')
            self.__non_catch_prop = f"(?{''.join(non_catch_prop_list)})"

    @property
    def start_with(self):
        new = copy.deepcopy(self)
        new.__start_anchor = Anchor.start_with()
        return new

    @property
    def end_with(self):
        new = copy.deepcopy(self)
        new.__end_anchor = Anchor.end_with()
        return new

    @property
    def ignore_case(self):
        new = copy.deepcopy(self)
        new.__ignore_case = True
        new.__update_non_catch_prop()
        return new

    @property
    def dot_all(self):
        new = copy.deepcopy(self)
        new.__dot_all = True
        new.__update_non_catch_prop()
        return new

    @property
    def multiline(self):
        new = copy.deepcopy(self)
        new.__multiline = True
        new.__update_non_catch_prop()
        return new

    def __add__(self, other):
        return CombineElem(
            f"{self.__non_catch_prop}{self.__start_anchor}{ElemFactory.create(other)}{self.__end_anchor}"
        )


class CharClassShort(IElem):
    def to_regex(self):
        return Regexp(str(self))

    def __init__(self, char: str):
        self.__char = char

    def zero_or_more(self):
        return ElemWithOp(f"{self.__char}*")

    def one_or_more(self):
        return ElemWithOp(f"{self.__char}+")

    def zero_or_one(self):
        return ElemWithOp(f"{self.__char}?")

    def repeat(self, times):
        return ElemWithOp(f"{self.__char}{{{times}}}")

    def repeat_range(self, min_times, max_times=None):
        if max_times is None:
            max_times = ""

        return ElemWithOp(f"{self.__char}{{{min_times},{max_times}}}")

    def ignore_case(self):
        return Group(self).ignore_case

    def dot_all(self):
        return Group(self).dot_all

    def multiline(self):
        return Group(self).multiline

    def close_ignore_case(self):
        return Group(self).close_ignore_case

    def close_dot_all(self):
        return Group(self).close_dot_all

    def close_multiline(self):
        return Group(self).close_multiline

    def __str__(self):
        return self.__char


class R:
    cr_0_9 = CharRange('0', '9')
    cr_1_9 = CharRange('1', '9')
    cr_a_z = CharRange('a', 'z')
    cr_A_Z = CharRange('A', 'Z')
    cr_a_z_A_Z = cr_a_z + cr_A_Z
    cr_0_9_a_z_A_Z = cr_0_9 + cr_a_z + cr_A_Z
    cr_m_n = CharRange

    digit = CharClassShort('\\d')
    word = CharClassShort('\\w')
    space = CharClassShort('\\s')
    non_digit = CharClassShort('\\D')
    non_word = CharClassShort('\\W')
    non_space = CharClassShort('\\S')
    any_char = CharClassShort('.')

    def __add__(self, other):
        return ElemFactory.create(other)

    def __radd__(self, other):
        return ElemFactory.create(other)

    @staticmethod
    def any_of(*content):
        return Group(*[ElemFactory.create(elem) for elem in content])


if __name__ == "__main__":
    pass
