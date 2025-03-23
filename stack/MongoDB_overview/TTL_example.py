import pandas as pd
from pymongo import MongoClient, ASCENDING
from datetime import datetime

# Создание DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# Подключение к MongoDB и создание коллекции
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']
collection.delete_many({})

# Сериализация и сохранение в MongoDB с временем создания
df['createdAt'] = datetime.now()  # Добавляем поле с текущей датой
collection.insert_many(df.to_dict(orient='records'))

# Создание TTL индекса на поле createdAt
collection.create_index([("createdAt", ASCENDING)], expireAfterSeconds=86400)

# Извлечение данных из MongoDB
result = collection.find()
data_from_mongo = list(result)

# Преобразование обратно в DataFrame
df_from_mongo = pd.DataFrame(data_from_mongo)

# Очистка данных
df_from_mongo = df_from_mongo.drop(columns='_id')  # Удаляем поле _id

# Проверка
print(df_from_mongo)
