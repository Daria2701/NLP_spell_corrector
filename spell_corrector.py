import re
from collections import Counter


def words(text): return re.findall(r'\w+', text.lower())


WORDS = Counter(words(open('big.txt').read()))


def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N


def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)


def candidates(word):
    "Generate possible spelling corrections for word."
    return known([word]) or known(duplicate_letter(word)) or known(swap_similar_letters(word)) or known(edits3(word)) \
           or known(edits1(word)) or known(edits2(word)) \
           or known(edits5(word)) \
           or [word]


def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)


def duplicate_letter(word):
    "Add an extra of the same letter"
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    duplicated = [L + R[0] + R[0] + R[1:] for L, R in splits if R]

    return set(duplicated)


def swap_similar_letters(word):
    "Change some letters that are easily mistaken for one another (eg. c and s)"
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    swapped = []
    for L, R in splits:
        if (R):
            if (R[0] == 'c'):
                swapped.append(L + "s" + R[1:])
            elif (R[0] == 's'):
                swapped.append(L + "c" + R[1:])
            elif (R[0] == 'a'):
                swapped.append(L + "e" + R[1:])
            elif (R[0] == 'e'):
                swapped.append(L + "a" + R[1:])
            elif (R[0] == 't'):
                swapped.append(L + "d" + R[1:])
            elif (R[0] == 'd'):
                swapped.append(L + "t" + R[1:])
            elif (R[0] == 'b'):
                swapped.append(L + "p" + R[1:])
            elif (R[0] == 'p'):
                swapped.append(L + "b" + R[1:])
            elif (R[0] == 'n'):
                swapped.append(L + "m" + R[1:])
            elif (R[0] == 'm'):
                swapped.append(L + "n" + R[1:])
    return set(swapped)


def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]

    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def edits3(word):
    "Apply edits1 in set of words with duplicated letters"
    return (e2 for e1 in duplicate_letter(word) for e2 in edits1(e1))


def edits5(word):
    "First duplicate, then swap common letters"
    return (e2 for e1 in duplicate_letter(word) for e2 in swap_similar_letters(e1))


################ Test Code
def unit_tests():
    assert correction('speling') == 'spelling'  # insert
    assert correction('korrectud') == 'corrected'  # replace 2
    assert correction('bycycle') == 'bicycle'  # replace
    assert correction('inconvient') == 'inconvenient'  # insert 2
    assert correction('arrainged') == 'arranged'  # delete
    assert correction('peotry') == 'poetry'  # transpose
    assert correction('peotryy') == 'poetry'  # transpose + delete
    assert correction('word') == 'word'  # known
    assert correction('quintessential') == 'quintessential'  # unknown
    assert words('This is a TEST.') == ['this', 'is', 'a', 'test']
    assert Counter(words('This is a test. 123; A TEST this is.')) == (
        Counter({'123': 1, 'a': 2, 'is': 2, 'test': 2, 'this': 2}))
    # assert len(WORDS) == 32192
    # assert sum(WORDS.values()) == 1115504
    # assert WORDS.most_common(10) == [
    #  ('the', 79808),
    #  ('of', 40024),
    #  ('and', 38311),
    #  ('to', 28765),
    #  ('in', 22020),
    #  ('a', 21124),
    #  ('that', 12512),
    #  ('he', 12401),
    #  ('was', 11410),
    #  ('it', 10681)]
    # assert WORDS['the'] == 79808
    assert P('quintessential') == 0
    assert 0.07 < P('the') < 0.08
    return 'unit_tests pass'


def spelltest(tests, verbose=False):
    "Run correction(wrong) on all (right, wrong) pairs; report results."
    import time
    start = time.time()
    good, unknown = 0, 0
    n = len(tests)
    #    daten = []
    for right, wrong in tests:
        w = correction(wrong)
        good += (w == right)
        if w != right:
            unknown += (right not in WORDS)
            #        IMPROVEMENT
            #        if right not in WORDS:
            #            daten.append(right)
            #            with open('big.txt', "a") as file:
            #                for right in daten:
            #                    file.write(right + "\n")
            #            print('correction({}) => {} ({}); expected {} ({})'
            #                  .format(wrong, w, WORDS[w], right, WORDS[right]))
            if verbose:
                print('correction({}) => {} ({}); expected {} ({})'
                      .format(wrong, w, WORDS[w], right, WORDS[right]))
    dt = time.time() - start
    print('{:.0%} of {} correct ({:.0%} unknown) at {:.0f} words per second'
          .format(good / n, n, unknown / n, n / dt))


#    print(len(daten))


def Testset(lines):
    "Parse 'right: wrong1 wrong2' lines into [('right', 'wrong1'), ('right', 'wrong2')] pairs."
    return [(right, wrong)
            for (right, wrongs) in (line.split(':') for line in lines)
            for wrong in wrongs.split()]


if __name__ == '__main__':
    print(len(WORDS))
    print(spelltest(Testset(open('spell-testset1.txt'))))
    print(spelltest(Testset(open('spell-testset2.txt'))))
