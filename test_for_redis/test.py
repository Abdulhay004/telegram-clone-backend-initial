from django.core.cache import cache

# Ma'lumotni qo'shish
cache.set('key', 'value', timeout=30)

# Ma'lumotni olish
value = cache.get('key')
print(value) # value