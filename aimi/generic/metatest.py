from Config import Meta, CT, XRAY

# assertions
m1 = Meta("a", "b")
m2 = Meta() + {"a": "b"}
m3 = Meta().ext({"a": "b"})
m4 = Meta().ext([m1, m2])
assert m1 == m2 and m2 == m3 and m3 == m4

m1 += {"c": "d"}
m5 = m1 + {"c": "d"}
assert m1 == m5

m6 = Meta()
m6.mdict = {'a': 'b', 'c': 'd', 'e': 'f'}

assert m6 <= m1
assert not m1 <= m6
assert m1 <= m6 - ['e', 'c']
assert not m6 - ['e', 'c'] <= m1
assert not m1 <= m6 - ['c']
assert not m1 == m6
assert m1 == m6 - ['e']
assert m6['c'] == 'd'
assert (m6 - ['e'])['a'] == 'b'
assert 'a' in m1
assert not 'e' in m1 

# some examples
m1 = Meta().ext({"a": "b", "c": "d"})

print("m1                                       ", m1)
print("m1 == m1                                 ", m1 == m1)
print("m1 == m1 + {'e': 'f'}                    ", m1 == m1 + {'e': 'f'})
print("m1 == {'a': 'b', 'c': 'd'}               ", m1 == {'a': 'b', 'c': 'd'})
print("Meta() == {}                             ", Meta() == {})
print("m1 <= m1                                 ", m1 <= m1)
print("m1 <= m1 + {'e': 'f'}                    ", m1 <= m1 + {'e': 'f'})
print("m1 - ['a']                               ", m1 - ['a'])
print("m1 - ['a'] <= m1                         ", m1 - ['a'] <= m1)
print("m1 <= m1 - ['a']                         ", m1 <= m1 - ['a'])

