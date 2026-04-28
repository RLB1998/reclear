from reclear import *

r = R()


def test_phone_no():
    phone_no_regexp = Prop().start_with.end_with + \
                      (
                              r + "1"
                              + [r.cr_m_n(_from=3, _to=9)]
                              + r.digit.repeat(9)
                      )

    print(phone_no_regexp)
    print(phone_no_regexp.to_regex().test("17359678365"))


def test_website():
    url_regexp = Prop().start_with.end_with + \
                 (
                         r + ("http", "https")
                         + "://"
                         + CharSet(r.cr_0_9_a_z_A_Z, '.').one_or_more()
                 )

    print(url_regexp)
    print(url_regexp.to_regex().test("https://www.google.com", "https://www.baidu.com"))


if __name__ == '__main__':
    # test_phone_no()
    # test_website()
    print(Prop().start_with.ignore_case.dot_all + \
          (
                  r + "abc" + r.any_char
          ))
