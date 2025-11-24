from app.cache.redis_cache import cache_set, cache_get, redis_cache, make_cache_key

def test_cache_set_and_get():
    ip = "1.1.1.1"
    model = "openai"
    key = make_cache_key(ip, model)

    data = {"risk_level": "Low"}
    
    cache_set(ip, data, model=model, ttl=30)
    result = cache_get(ip, model)

    assert result == data

def test_cache_delete():
    ip = "2.2.2.2"
    model = "openai"
    key = make_cache_key(ip, model)

    cache_set(ip, {"a": 1}, model=model)
    redis_cache.delete(key)

    assert cache_get(ip, model) is None
