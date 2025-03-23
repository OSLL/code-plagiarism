from pymongo import MongoClient

# Подключение к локальному серверу MongoDB (по умолчанию работает на порту 27017)
client = MongoClient("mongodb://localhost:27017/")

# Проверяем список доступных баз данных
print(client.list_database_names())

# Выбираем (или создаем, если не существует) базу данных "mydatabase"
db = client["mydatabase"]

# Выбираем (или создаем) коллекцию "users"
collection = db["users"]

# отчистка коллекции
collection.delete_many({})

# Проверяем существующие коллекции
print(db.list_collection_names())

user = {
    "name": "Alice",
    "age": 25,
    "email": "alice@example.com"
}

# Вставляем документ в коллекцию
insert_result = collection.insert_one(user)

# Получаем ID вставленного документа
print(f"Inserted document ID: {insert_result.inserted_id}")

users = [
    {"name": "Bob", "age": 30, "email": "bob@example.com"},
    {"name": "Charlie", "age": 35, "email": "charlie@example.com"},
]

insert_many_result = collection.insert_many(users)

# Получаем список вставленных ID
print(insert_many_result.inserted_ids)

user = collection.find_one({"name": "Alice"})
print(user)

all_users = collection.find()
for user in all_users:
    print(user)

print('filtration')

# фильтрация
# Поиск всех пользователей старше 30 лет
filtered_users = collection.find({"age": {"$gt": 30}})
for user in filtered_users:
    print(user)

# получение отдельных полей
# Получаем только имена всех пользователей
users_projection = collection.find({}, {"name": 1, "_id": 0})
for user in users_projection:
    print(user)

print('update')
# обновление одного документа
collection.update_one({"name": "Alice"}, {"$set": {"age": 26}})

# обновление нескольких документов
collection.update_many({"age": {"$gt": 30}}, {"$set": {"status": "senior"}})

all_users = collection.find()
for user in all_users:
    print(user)

print('deleting')
# удаление одного документа
collection.delete_one({"name": "Charlie"})
all_users = collection.find()
for user in all_users:
    print(user)

# удаление документов с фильтрацией
collection.delete_many({"age": {"$gt": 30}})
all_users = collection.find()
for user in all_users:
    print(user)

print('index')
# работа с индексами
collection.create_index("email", unique=True)
print(collection.index_information())

# закрытие соединения
client.close()




