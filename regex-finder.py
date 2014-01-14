'''
Contents of this file is taken from http://nbviewer.ipython.org/url/norvig.com/ipython/xkcd1313.ipynb

This code is used to generate regular expressions that match all
strings in a list of winners but don't match any strings in a list of losers.

In the original context winners and losers refer to the names of
US presidential candidates.
'''


import re


def verify(regex, winners, losers):
    "Return true iff the regex matches all winners but no losers."
    missed_winners = {w for w in winners if not re.search(regex, w)}
    matched_losers = {L for L in losers if re.search(regex, L)}
    if missed_winners:
        print("Error: should match but did not:", ', '.join(missed_winners))
    if matched_losers:
        print("Error: should not match but did:", ', '.join(matched_losers))
    return not (missed_winners or matched_losers)

def findregex(winners, losers):
    "Find a regex that matches all winners but no losers (sets of strings)."
    # Make a pool of regex components, then pick from them to cover winners.
    # On each iteration, add the 'best' component to 'cover',
    # remove winners covered by best, and keep in 'pool' only components
    # that still match some winner.
    pool = regex_components(winners, losers)
    cover = []
    while winners:
        best = max(pool, key=lambda c: 3 * len(matches(c, winners)) - len(c))
        cover.append(best)
        winners = winners - matches(best, winners)
        pool = {c for c in pool if matches(c, winners)}
    return '|'.join(cover)

def regex_components(winners, losers):
    "Return components that match at least one winner, but no loser."
    wholes = {'^'+winner+'$' for winner in winners}
    parts = {d for w in wholes for p in subparts(w) for d in dotify(p)
             if not matches(d, losers)}
    return wholes | parts

def subparts(word):
    "Return a set of subparts of word, consecutive characters up to length 4."
    return set(word[i:i+n] for i in range(len(word)) for n in (1, 2, 3, 4))

def dotify(part):
    "Return all ways to replace a subset of chars in part with '.'."
    if part == '':
        return {''}
    else:
        return {c+rest for rest in dotify(part[1:]) for c in replacements(part[0])}

def replacements(char):
    "Return possible replacement characters for char (char + '.' unless char is special)."
    return char if (char in '^$') else char + '.'

def matches(regex, strings):
    "Return a set of all the strings that are matched by regex."
    return {s for s in strings if re.search(regex, s)}

def test():
    assert regex_components({'win'}, {'losers', 'bin', 'won'}) == {
      '^win$', '^win', '^wi.', 'wi.',  'wi', '^wi', 'win$', 'win', 'wi.$'}
    assert subparts('^it$') == {'^', 'i', 't', '$', '^i', 'it', 't$', '^it', 'it$', '^it$'}
    assert subparts('this') == {'t', 'h', 'i', 's', 'th', 'hi', 'is', 'thi', 'his', 'this'}
    assert dotify('it') == {'it', 'i.', '.t', '..'}
    assert dotify('^it$') == {'^it$', '^i.$', '^.t$', '^..$'}
    assert dotify('this') == {'this', 'thi.', 'th.s', 'th..', 't.is', 't.i.', 't..s', 't...',
                              '.his', '.hi.', '.h.s', '.h..', '..is', '..i.', '...s', '....'}
    assert replacements('x') == 'x.'
    assert replacements('^') == '^'
    assert replacements('$') == '$'
    assert matches('a|b|c', {'a', 'b', 'c', 'd', 'e'}) == {'a', 'b', 'c'}
    assert matches('a|b|c', {'any', 'bee', 'succeed', 'dee', 'eee!'}) == {'any', 'bee', 'succeed'}
    assert verify('a+b+', {'ab', 'aaabb'}, {'a', 'bee', 'a b'})
    assert findregex({"ahahah", "ciao"},  {"ahaha", "bye"}) == 'a.$'
    return 'test passes'

test()
