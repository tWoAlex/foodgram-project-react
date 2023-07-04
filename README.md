# Foodgram
## Социальная сеть для кулинаров!
![master push workflow status](https://github.com/tWoAlex/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg?branch=master)

### Социальная сеть, где вы можете:

 * Публиковать свои рецепты,

 * Подписываться на авторов,

 * Хранить список избранных рецептов,

 * Собирать список покупок для похода в магазин.

---


#### Запуск проекта на вашем сервере
<details>
  <summary>Инструкция</summary>

---

**Шаг 1. Склонируйте репозиторий.**

---

**Шаг 2. Перейдите в папку infra, подготовьте .env и запустите проект.**

```
cd infra/
```

```
touch .env
```

Пример содержания .env:

```
SECRET_KEY=yoursecretkeyfordjango         # Секретный ключ Django

DB_ENGINE=django.db.backends.postgresql   # Движок базы данных 
DB_NAME=postgres                          # Имя базы данных
POSTGRES_USER=postgres                    # Пользователь
POSTGRES_PASSWORD=postgres                # и пароль для подключения к БД
DB_HOST=db                                # Адрес сервера с БД
DB_PORT=5432                              # Порт для подключения к БД
```

Запуск проекта:

```
sudo docker-compose up -d
```

---

**Шаг 3. Постройте базу данных, загрузите ингредиенты и тэги, соберите статику.**

Для начала узнаем ID контейнера с бэкендом:

```
sudo docker container ls
```

Выберите ID контейнера (первый столбик) под названием `twoalex/foodgram_backend:latest`

```
sudo docker exec -it {{ container_id }} python manage.py migrate
```

```
sudo docker exec -it {{ container_id }} python manage.py loaddata fixtures.json
```

```
sudo docker exec -it {{ container_id }} python manage.py collectstatic
```

**Шаг 4 (опциональный). Создайте суперпользователя для управления содержимым проекта.**

```
sudo docker exec -it {{ container_id }} python manage.py createsuperuser
```

Следуйте инструкциям на экране, введите **Логин**, **E-Mail** и **Пароль** суперпользователя.

</details>

---

#### API проекта также доступен отдельно, в виде образа `twoalex/foodgram_backend:latest` на Docker Hub.

Документация расположена по адресу `http://158.160.22.254/api/docs/`

### Тестовый экземпляр

#### Протестируйте живую версию проекта по адресу `http://158.160.22.254`
<details>
  <summary>Аккаунт администратора</summary>

>Логин:
>
>```
>dungeonmaster
>```
>
>E-Mail:
>
>```
>dungeonmaster@dungeon.gym
>```
>
>Пароль:
>
>```
>holdyourpython
>```

</details>
<details>
  <summary>Тестовые пользователи</summary>

><details>
><summary>Альберт Эйнштейн</summary>
>
>Логин:
>
>```
>albert_genius
>```
>
>E-Mail:
>
>```
>genius@dungeon.gym
>```
>
>Пароль:
>
>```
>flexingthroughthewind
>```
>
></details>

><details>
><summary>Наполеон Бонапарт</summary>
>
>Логин:
>
>```
>buonaparte
>```
>
>E-Mail:
>
>```
>buonaparte@strategy.genius
>```
>
>Пароль:
>
>```
>antiquehero
>```
>
></details>

><details>
><summary>Алан Тьюринг</summary>
>
>Логин:
>
>```
>turing
>```
>
>E-Mail:
>
>```
>enigma@ohmy.math
>```
>
>Пароль:
>
>```
>howareyoudescendants
>```
>
></details>

</details>
