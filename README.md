# Reclear

Reclear is a Python gadget that was born to solve the pain point of regular expressions being difficult to read and
maintain.

Reclear是一个python小工具，它的诞生旨在解决正则表达式难以阅读、维护的痛点。

## Quick Start 快速开始

Required version \>= Python 3.8

~~~python
from reclear import R
from reclear import Prop, CharSet

r = R()

# ^1[3-9]\d{9}$
phone_no_regexp = Prop().start_with.end_with + \
                  (
                          r + "1"
                          + [r.cr_m_n(_from=3, _to=9)]
                          + r.digit.repeat(9)
                  )
print(phone_no_regexp.to_regex().test("17359678365"))

# ^(http|https)://[0-9a-zA-Z.]+$
url_regexp = Prop().start_with.end_with + \
             (
                     r + ("http", "https")
                     + "://"
                     + CharSet(r.cr_0_9_a_z_A_Z, '.').one_or_more()
             )
print(url_regexp.to_regex().test("https://www.google.com", "https://www.baidu.com"))
~~~

## Concept 概念

### Element 元素

The basic components of regular expressions, including regular characters, strings, groups, character sets, etc.

正则表达式的基础组成部分，包括普通字符、字符串、分组、字符集等。

| DSL                                                          | Regexp         | Description 说明                                             |
| ------------------------------------------------------------ | -------------- | ------------------------------------------------------------ |
| Elem(".abc")、R() + ".abc"                                   | \\.abc         | Regular string element objects, with automatic escape function for meta char. Using the addition of R objects and ordinary strings gives a regular string element object.    正则字符串元素对象，对于元字符meta char有自动转义功能。使用R对象和普通字符串相加可以得到正则字符串元素对象。 |
| CharSet(r.cr_0_9_a_z_A_Z, '-')、R() + [r.cr_0_9_a_z_A_Z, '-'] | [0-9a-zA-Z\\-] | Character set object, which provides predetermined character range templates and automatic escape functions. Using R objects and list summing gives you character set objects.    字符集对象，提供预定的字符范围模板、自动转义功能。使用R对象和列表相加可以得到字符集对象。 |
| Group("http", "https")、R() + ("http", "https")              | (http\|https)  | Group objects. Using the sum of R objects and tuple gives the grouping object.    分组对象。使用R对象和元祖相加可以得到分组对象。 |

### Action 动作

The number of times the element is repeatedly matched. In DSL, it is called in the form of a method with parentheses at the end.

元素重复匹配的次数。DSL里以方法的形式调用，结尾带括号。

| DSL                                | Regexp |
| ---------------------------------- | ------ |
| zero_or_more()                     | *      |
| one_or_more()                      | +      |
| zero_or_one()                      | ?      |
| repeat(times)                      | {n}    |
| repeat_range(min_times, max_times) | {m,n}  |

### Attribute 属性

Used to configure the properties of the element. In DSL, it is called as an attribute without parentheses at the end.

用来配置元素的属性。DSL里以属性的方式调用，结尾不带括号。

| DSL               | Regexp | Description 说明                                             |
| ----------------- | ------ | ------------------------------------------------------------ |
| ignore_case       | (?i:)  | Ignore case.    忽略大小写。                                 |
| dot_all           | (?s:)  | Make the `.` sign match the line break `\n`.    让`.`号可以匹配换行符`\n`。 |
| multiline         | (?m:)  | Make `^` and `$` match the beginning and end of each line.    让`^` 和 `$`能够匹配每一行的开头和结尾。 |
| close_ignore_case | (?-i:) | Partial disability of ignore_case function.    局部关闭ignore_case功能。 |
| close_dot_all     | (?-s:) | Partial disability of dot_all function.    局部关闭dot_all功能。 |
| close_multiline   | (?-m:) | Partial disability of close_multiline function.    局部关闭close_multiline功能。 |

## Main Class 主要类

### R

The most important tool class can convert list into CharSet objects, tuples into Group objects, and str into Elem objects through additive operations. It also provides predefined characters, character set templates and other members to simplify regular development.

最主要的工具类，通过相加的操作能将list转化为CharSet对象、tuple转化为Group对象、str转化为Elem对象。并且提供了预定义字符、字符集模板等成员，简化正则开发。

~~~python
from reclear import R

r = R()

r + ("abc", "ABC")    # (abc|ABC)
r + ".abc"    # \.abc
r + ['a', 'b', 'c']    # [abc]

r + [r.cr_0_9]    # [0-9]    cr means char range
r + [r.cr_a_z_A_Z]    # [a-zA-Z]
r + [r.cr_m_n(3, 9)]    # [3-9]    support unicode
r + [r.cr_m_n('f', 'j')]    # [f-j]

r.digit.repeat(10)    # \d{10}
r.non_space.one_or_more()    # \S+
r.any_char.zero_or_more()    # .*
~~~

### Prop

The configuration object of the regular expression, the object of a prop class controls the configuration of the entire regular expression.

正则表达式的配置对象，一个Prop类的对象控制一整个正则表达式的配置。

~~~python
from reclear import R
from reclear import Prop

r = R()

# ^abc
Prop().start_with + \
	(
    	r + "abc"
    )

# ^abc$
Prop().start_with.end_with + \
	(
    	r + "abc"
    )

# (?i)^abc
Prop().start_with.ignore_case + \
	(
    	r + "abc"
    )

# (?is)^abc.
Prop().start_with.ignore_case.dot_all + \
(
        r + "abc" + r.any_char
)
~~~

### Elem

The string class in the regular has an automatic transfer function. It also has the function of converting ordinary python types to Elem, Group, and CharSet.

正则里的字符串类，具有自动转义功能。也具有将普通python类型转为Elem、Group、CharSet的功能。

~~~python
from reclear import Elem

Elem("abc")    # abc
Elem(".abc")    # \.abc

Elem("abc")	+ ".123"    # abc\.123
Elem("abc") + [1, 2, 3]    # abc[123]
Elem("abc")	+ ("aa", "bb")    # abc(aa|bb)
~~~

### CharSet

The character set class in the regular can be transformed by list. Automatic transfer is also available, so you don't need to think extra about manual escaping when writing code. Reverse can be controlled by the attribute `negated`.

正则里的字符集类，可以通过list转化而来。也提供自动转义功能，编写代码时不需要额外考虑手动转义。可以通过属性`negated`来控制取反。

~~~python
from reclear import R
from reclear import CharSet

CharSet(r.cr_0_9_a_z_A_Z, '-', ']', '^')    # [0-9a-zA-Z\-\]\^]
R() + [1, 3, 7]    # [137]

CharSet(r.cr_a_z).negated	# [^a-z]
~~~

### Group

The grouping types in the regular can be transformed by tuple. Controlling whether a Group is a capture group is controlled by the attribute `non_catch`.

正则里的分组类型，可以通过tuple转化而来。通过属性`non_catch`控制Group是否为捕获组。

~~~python
from reclear import R
from reclear import Group

Group("http", "https")    # (http|https)
R() + ("http", "https")    # (http|https)

Group("http", "https").non_catch    # (?:http|https)
Group("http", "https").ignore_case	# (?i:http|https)
~~~

### Anchor

The main function of anchor classes is to mark a position in the regex, and then use the zero-width assertion function at that position.

锚点类主要功能是在正则里标记一个位置，然后在这个位置上使用零宽断言功能。

~~~python
# (?i)^(?=a)\w+(?<!ing)$
(
        Anchor.look_right().must_be("a")
        + r.word.one_or_more()
        + Anchor.look_left().cant_be("ing")
)
.to_regex().test("apple", "banana", "amazing", "alike")
# {'apple': True, 'banana': False, 'amazing': False, 'alike': True}
~~~

### Regexp

Regular Expression object, which provides the regular expression written by the test method.

正则表达式对象，提供test方法测试编写的正则表达式。
