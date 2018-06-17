import random
from functools import wraps

def RandomChance(chance: float):
	def RandomChanceDecorator(fn):
		chance_min = random.random()
		chance_max = chance_min + chance

		if chance_max > 1:
			chance_min -= chance_max - 1

		@wraps(fn)
		async def new_fn(*args, **kwargs):
			if chance_min <= random.random() <= chance_max:
				#print('im doin it')
				return await fn(*args, **kwargs)
			else:
				return False

		return new_fn

	return RandomChanceDecorator
