def test2(a=[]):
	a.append("b")

def test(a=[]):
	test2(a)
	test2(a)

a = []

test(a)

print(a)
