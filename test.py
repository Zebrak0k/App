from requests import get, post, delete

print(get('http://localhost:5000/api/news').json())
print(get('http://localhost:5000/api/news/1').json())
print(get('http://localhost:5000/api/news/1000').json())
print(post('http://localhost:5000/api/news', json={}).json())
print(post('http://localhost:5000/api/news', json={'title': 'Заголовок 1'}).json())
print(post('http://localhost:5000/api/news', json={
    'title': 'Заголовок',
    'content': 'Контент',
    'user_id': '1',
    'is_private': False
}).json())

print(delete('http://localhost:5000/api/news/2').json())
print(delete('http://localhost:5000/api/news/1000').json())