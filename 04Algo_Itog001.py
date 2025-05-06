#04 Алгоритмы и структуры данных
# Итоговый практикум №2
# Симулятор магазина с корзиной покупок с использованием алгоритмов сортировки

import json
import time
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List, Dict, Optional, Callable

# класс товаров
class Product:

    # товар: ID, название, категория, цена, вес, описание
    def __init__(self, id: int, name: str, category: str, price: float, weight: float, description: str = ""):

        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.weight = weight
        self.description = description

    def __str__(self):   # строка - товар
        return (f"Товар: {self.name} (ID: {self.id})\n"
                f"Категория: {self.category}\n"
                f"Цена: {self.price:.2f} руб.\n"
                f"Вес: {self.weight:.2f} кг\n"
                f"Описание: {self.description}")

    def to_dict(self) -> Dict:          # товар - словарь
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'weight': self.weight,
            'description': self.description
        }

# класс для управления каталогом товаров
class ProductCatalog:

    def __init__(self):                 # каталога товаров
        self.products = []
        self.next_id = 1

    # + новый товар: название, категория, цена, вес, описание, объект
    def add_product(self, name: str, category: str, price: float, weight: float, description: str = "") -> Product:

        if price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом")

        product = Product(self.next_id, name, category, price, weight, description)
        self.products.append(product)
        self.next_id += 1
        return product

    # редактирование товара: ID, название, категория, цена, вес, описание
    def edit_product(self, product_id: int, **kwargs) -> Optional[Product]:

        product = self.find_product_by_id(product_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key):
                if key in ['price', 'weight'] and value <= 0:
                    raise ValueError(f"{key.capitalize()} должен быть положительным числом")
                setattr(product, key, value)

        return product

    # удаление товара из каталога: ID
    def remove_product(self, product_id: int) -> bool:

        product = self.find_product_by_id(product_id)
        if product:
            self.products.remove(product)
            return True
        return False

    # поиск товара по ID
    def find_product_by_id(self, product_id: int) -> Optional[Product]:

        for product in self.products:
            if product.id == product_id:
                return product
        return None

    # вывод списка товаров по категории
    def get_products_by_category(self, category: str) -> List[Product]:

        return [product for product in self.products if product.category.lower() == category.lower()]

    # сохранение каталога в файл
    def save_to_file(self, filename: str) -> bool:

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.products], f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении каталога: {e}")
            return False

    # загрузка каталога из файла
    def load_from_file(self, filename: str) -> bool:

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = []
                max_id = 0
                for item in data:
                    product = Product(
                        item['id'],
                        item['name'],
                        item['category'],
                        item['price'],
                        item['weight'],
                        item.get('description', '')
                    )
                    self.products.append(product)
                    if product.id > max_id:
                        max_id = product.id
                self.next_id = max_id + 1
            return True
        except Exception as e:
            print(f"Ошибка при загрузке каталога: {e}")
            return False

    # вывод всего каталога товаров
    def display_catalog(self):

        if not self.products:
            print("Каталог товаров пуст.")
            return

        print("\n============== КАТАЛОГ ТОВАРОВ ==============")
        for product in self.products:
            print(f"{product.id}. {product.name} - {product.price:.2f} руб. ({product.category})")
        print("==============================================")

# класс управления товара в корзине
class CartItem:

    # товара в корзине: объект и кол-во
    def __init__(self, product: Product, quantity: int = 1):

        self.product = product
        self.quantity = quantity

    # общая стоимость товара, цена * кол-во
    @property
    def total_price(self) -> float:

        return self.product.price * self.quantity

    # общий вес товара, вес * кол-во
    @property
    def total_weight(self) -> float:

        return self.product.weight * self.quantity

    # строка - товар в корзине
    def __str__(self):

        return (f"{self.product.name} (ID: {self.product.id}) - "
                f"{self.quantity} шт. x {self.product.price:.2f} руб. = {self.total_price:.2f} руб.")

# класс управления корзиной покупок
class ShoppingCart:

    # пустая корзина
    def __init__(self):

        self.items = []
        self.discount = 0            # скидка в процентах

    # + товара в корзине, кол-во
    def add_item(self, product: Product, quantity: int = 1) -> bool:

        if quantity <= 0:
            raise ValueError("Количество должно быть положительным числом")

        # проверка наличия такого товара в корзине
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return True

        # если товара нет в корзине, + новый элемент
        self.items.append(CartItem(product, quantity))
        return True

    # - товар из корзины, ID, кол-во
    def remove_item(self, product_id: int, quantity: int = None) -> bool:

        for item in self.items:
            if item.product.id == product_id:
                if quantity is None or item.quantity <= quantity:
                    self.items.remove(item)
                else:
                    item.quantity -= quantity
                return True
        return False

    # отчистка корзины
    def clear(self):

        self.items = []
        self.discount = 0

    # общая стоимость всех товаров в корзине со скидкой
    @property
    def total_price(self) -> float:

        subtotal = sum(item.total_price for item in self.items)
        return subtotal * (1 - self.discount / 100)

    # общий вес всех товаров в корзине
    @property
    def total_weight(self) -> float:

        return sum(item.total_weight for item in self.items)

    # общее кол-во товаров в корзине
    @property
    def item_count(self) -> int:

        return len(self.items)

    # общее кол-во единиц товаров в корзине
    @property
    def total_quantity(self) -> int:

        return sum(item.quantity for item in self.items)

    # + скидки к корзине 0-50%
    def apply_discount(self, percent: float):

        if percent < 0 or percent > 50:
            raise ValueError("Скидка должна быть в диапазоне от 0 до 50%")
        self.discount = percent

    # вывод содержимого корзины
    def display(self, show_details: bool = False):

        if not self.items:
            print("Ваша корзина пуста.")
            return

        print("\n=========== ВАША КОРЗИНА ==========")
        for idx, item in enumerate(self.items, 1):
            print(f"{idx}. {item}")
            if show_details:
                print(f"   Категория: {item.product.category}")
                print(f"   Вес: {item.total_weight:.2f} кг")

        print("\nИтого:")
        print(f"Количество позиций: {self.item_count}")
        print(f"Общее количество товаров: {self.total_quantity}")
        print(f"Общий вес: {self.total_weight:.2f} кг")
        if self.discount > 0:
            print(f"Скидка: {self.discount}%")
        print(f"Общая стоимость: {self.total_price:.2f} руб.")
        print("=============================================")

# класс выбора сортировки
class SortStrategy(ABC):

    # метод сортировки
    @abstractmethod
    def sort(self, items: List[CartItem], reverse: bool = False) -> List[CartItem]:
        pass

    # функции ключ сортировки, цена, вес, категория
    @staticmethod
    def get_key_function(key: str) -> Callable[[CartItem], float]:

        if key == 'price':
            return lambda item: item.product.price
        elif key == 'weight':
            return lambda item: item.product.weight
        elif key == 'category':
            return lambda item: item.product.category
        else:
            raise ValueError("Недопустимый выбор сортировки. Допустимые значения: 'цена', 'вес', 'категория'")

# класс пузырьковой сортировки
class BubbleSortStrategy(SortStrategy):

    # сортировка пузырьком
    def sort(self, items: List[CartItem], key: str = 'price', reverse: bool = False) -> List[CartItem]:

        key_func = self.get_key_function(key)
        n = len(items)
        items = deepcopy(items)             # копия, оригинал оставляем

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):       # сравнение элементов по ключу
                a = key_func(items[j])
                b = key_func(items[j + 1])

                if (a > b) if not reverse else (a < b):
                    items[j], items[j + 1] = items[j + 1], items[j]
                    swapped = True

            if not swapped:
                break

        return items

# класс сортировки вставками
class InsertionSortStrategy(SortStrategy):

    # сортировка вставками
    def sort(self, items: List[CartItem], key: str = 'price', reverse: bool = False) -> List[CartItem]:

        key_func = self.get_key_function(key)
        items = deepcopy(items)             # копия, оригинал оставляем

        for i in range(1, len(items)):
            current = items[i]
            j = i - 1

            while j >= 0 and (
            (key_func(items[j]) > key_func(current)) if not reverse else (key_func(items[j]) < key_func(current))):
                items[j + 1] = items[j]
                j -= 1

            items[j + 1] = current

        return items

# класс быстрой сортировки
class QuickSortStrategy(SortStrategy):

    # быстрая сортировка
    def sort(self, items: List[CartItem], key: str = 'price', reverse: bool = False) -> List[CartItem]:

        key_func = self.get_key_function(key)
        items = deepcopy(items)                 # копия, оригинал оставляем

        def partition(arr, low, high):
            pivot = key_func(arr[high])
            i = low - 1

            for j in range(low, high):
                compare = (key_func(arr[j]) <= pivot) if not reverse else (key_func(arr[j]) >= pivot)
                if compare:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def quick_sort(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                quick_sort(arr, low, pi - 1)
                quick_sort(arr, pi + 1, high)

        quick_sort(items, 0, len(items) - 1)
        return items

# класс сортировки слиянием
class MergeSortStrategy(SortStrategy):

    # сортировка слиянием
    def sort(self, items: List[CartItem], key: str = 'price', reverse: bool = False) -> List[CartItem]:

        key_func = self.get_key_function(key)
        items = deepcopy(items)                 # копия, оригинал оставляем

        def merge_sort(arr):
            if len(arr) > 1:
                mid = len(arr) // 2
                left = arr[:mid]
                right = arr[mid:]

                merge_sort(left)
                merge_sort(right)

                i = j = k = 0

                while i < len(left) and j < len(right):
                    if (key_func(left[i]) <= key_func(right[j])) if not reverse else (
                            key_func(left[i]) >= key_func(right[j])):
                        arr[k] = left[i]
                        i += 1
                    else:
                        arr[k] = right[j]
                        j += 1
                    k += 1

                while i < len(left):
                    arr[k] = left[i]
                    i += 1
                    k += 1

                while j < len(right):
                    arr[k] = right[j]
                    j += 1
                    k += 1

        merge_sort(items)
        return items

# класс управления сортировками в корзине
class CartSorter:

    # выбор сортировки
    def __init__(self):
        self.strategies = {
            'bubble': BubbleSortStrategy(),
            'insertion': InsertionSortStrategy(),
            'quick': QuickSortStrategy(),
            'merge': MergeSortStrategy()
        }

    # сортировка корзины с использованием выбранной вида сортировки
    def sort_cart(self, cart: ShoppingCart, strategy_name: str, key: str = 'price', reverse: bool = False) -> List[CartItem]:
        strategy = self.strategies.get(strategy_name.lower())
        if not strategy:
            raise ValueError(f"Неизвестная сортировки: {strategy_name}")

        return strategy.sort(cart.items, key, reverse)

# класс меню магазина
class ShopUI:

    # меню каталог, корзина и сортировка
    def __init__(self):
        self.catalog = ProductCatalog()
        self.cart = ShoppingCart()
        self.sorter = CartSorter()
        self.setup_sample_data()

    # начальные продукты данных
    def setup_sample_data(self):
        self.catalog.add_product("Ноутбук", "Электроника", 12300.0, 2.5, "Мощный ноутбук для работы и игр")
        self.catalog.add_product("Смартфон", "Электроника", 8690.99, 0.3, "Флагманский смартфон")
        self.catalog.add_product("Кофеварка", "Бытовая техника", 1157.0, 1.8, "Автоматическая кофеварка")
        self.catalog.add_product("Футболка", "Одежда", 250.0, 0.2, "Хлопковая футболка")
        self.catalog.add_product("Книга", "Книги", 700.0, 0.5, "Интересная книга")
        self.catalog.add_product("Наушники", "Электроника", 999.99, 0.4, "Беспроводные наушники")
        self.catalog.add_product("Чайник", "Бытовая техника", 1200.0, 1.2, "Супер чайник")
        self.catalog.add_product("PS5", "Электроника", 49000.0, 3.0, "Мега игровая консоль")
        self.catalog.add_product("Телевизор 65", "Электроника", 96900.0, 23.0, "УльтраМегаHD картинка")

    # вывод главного меню
    def display_menu(self):
        print("\n===== ВИРТУАЛЬНЫЙ ИНТЕРНЕТ-МАГАЗИН =====")
        print(" 1. Просмотр каталога товаров")
        print(" 2. Добавить товар в корзину")
        print(" 3. Удалить товар из корзины")
        print(" 4. Просмотр корзину")
        print(" 5. Отчистить корзину")
        print(" 6. Применить скидку")
        print(" 7. Сортировать корзину")
        print(" 8. Сохранить каталог в файл")
        print(" 9. Загрузить каталог из файла")
        print("10. Добавить новый товар в каталог")
        print("11. Редактировать товар в каталоге")
        print("12. Удалить товар из каталога")
        print(" 0. Выход")

    # запуск основного цикла меню
    def run(self):

        while True:
            self.display_menu()
            choice = input("Выберите действие: ")

            try:
                if choice == '1':
                    self.show_catalog()
                elif choice == '2':
                    self.add_to_cart()
                elif choice == '3':
                    self.remove_from_cart()
                elif choice == '4':
                    self.show_cart()
                elif choice == '5':
                    self.clear_cart()
                elif choice == '6':
                    self.apply_discount()
                elif choice == '7':
                    self.sort_cart()
                elif choice == '8':
                    self.save_catalog()
                elif choice == '9':
                    self.load_catalog()
                elif choice == '10':
                    self.add_product_to_catalog()
                elif choice == '11':
                    self.edit_product_in_catalog()
                elif choice == '12':
                    self.remove_product_from_catalog()
                elif choice == '0':
                    print("\nСпасибо за посещение нашего Интернет-магазина! Ждем вас в гости!")
                    break
                else:
                    print("Неверный выбор. Пожалуйста, попробуйте снова.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

    # вывод каталога товаров
    def show_catalog(self, detailed: bool = False):
        self.catalog.display_catalog()

        if detailed:
            product_id = input("Введите ID товара для просмотра деталей (или 0 для возврата): ")
            if product_id != '0':
                product = self.catalog.find_product_by_id(int(product_id))
                if product:
                    print("\n" + str(product))
                else:
                    print("Товар не найден.")

    # функция + товара в корзину
    def add_to_cart(self):
        self.show_catalog()

        product_id = input("Введите ID товара для добавления в корзину (или 0 для отмены): ")
        if product_id == '0':
            return

        product = self.catalog.find_product_by_id(int(product_id))
        if not product:
            print("Товар не найден.")
            return

        try:
            quantity = int(input(f"Введите количество (доступно: {product.name}): ") or "1")
            if quantity <= 0:
                print("Количество должно быть положительным числом.")
                return

            self.cart.add_item(product, quantity)
            print(f"Товар '{product.name}' добавлен в корзину.")
        except ValueError:
            print("Неверный формат количества.")

    # функция - товара из корзины
    def remove_from_cart(self):
        if not self.cart.items:
            print("Корзина пуста.")
            return

        self.cart.display()

        try:
            item_num = int(input("Введите номер позиции для удаления (или 0 для отмены): "))
            if item_num == 0:
                return

            if 1 <= item_num <= len(self.cart.items):
                item = self.cart.items[item_num - 1]
                quantity = input(f"Введите количество для удаления (макс. {item.quantity}, Enter - удалить все): ")

                if quantity:
                    try:
                        quantity = int(quantity)
                        if quantity <= 0 or quantity > item.quantity:
                            print("Неверное количество.")
                            return
                        self.cart.remove_item(item.product.id, quantity)
                        print(f"Удалено {quantity} шт. товара '{item.product.name}'.")
                    except ValueError:
                        print("Неверный формат количества.")
                else:
                    self.cart.remove_item(item.product.id)
                    print(f"Товар '{item.product.name}' полностью удален из корзины.")
            else:
                print("Неверный номер позиции.")
        except ValueError:
            print("Неверный формат номера.")

    # вывод содержимого корзины
    def show_cart(self):
        self.cart.display(show_details=True)

    # функция отчистка корзины
    def clear_cart(self):
        if not self.cart.items:
            print("Корзина уже пуста.")
            return

        confirm = input("Вы уверены, что хотите очистить корзину? (д/н): ").lower()
        if confirm == 'д':
            self.cart.clear()
            print("Корзина очищена.")

    # вывод скидки к корзине
    def apply_discount(self):
        if not self.cart.items:
            print("Корзина пуста. Невозможно применить скидку.")
            return

        try:
            discount = float(input("Введите размер скидки (0-50) %: "))
            self.cart.apply_discount(discount)
            print(f"Скидка {discount}% применена к корзине.")
            self.cart.display()
        except ValueError as e:
            print(f"Ошибка: {e}")

    # функция сортировка корзины
    def sort_cart(self):
        if not self.cart.items:
            print("Корзина пуста. Невозможно отсортировать.")
            return

        print("\n       Доступные виды сортировки:")
        print("1. Пузырьковая сортировка (Bubble Sort)")
        print("2. Сортировка вставками (Insertion Sort)")
        print("3. Быстрая сортировка (Quick Sort)")
        print("4. Сортировка слиянием (Merge Sort)")

        algorithm = input("Выберите вид сортировки (1-4): ")

        algorithms = {
            '1': 'bubble',
            '2': 'insertion',
            '3': 'quick',
            '4': 'merge'
        }

        if algorithm not in algorithms:
            print("Неверный выбор вида.")
            return

        print("\nКритерии сортировки:")
        print("1. По цене")
        print("2. По весу")
        print("3. По категории")

        criterion = input("Выберите критерий сортировки (1-3): ")

        criteria = {
            '1': 'price',
            '2': 'weight',
            '3': 'category'
        }

        if criterion not in criteria:
            print("Неверный выбор критерия.")
            return

        order = input("Сортировать по возрастанию (1) или убыванию (2)? ")
        reverse = order == '2'

        print("\nИсходная корзина:")
        self.cart.display()

        print("\nПроцесс сортировки...")
        start_time = time.time()

        try:
            sorted_items = self.sorter.sort_cart(
                self.cart,
                algorithms[algorithm],
                criteria[criterion],
                reverse
            )

            end_time = time.time()
            print(f"Сортировка завершена за {end_time - start_time:.6f} секунд.")

            print("\nОтсортированная корзина:")
            temp_cart = ShoppingCart()
            temp_cart.items = sorted_items
            temp_cart.display(show_details=True)

            apply = input("Применить сортировку к корзине? (д/н): ").lower()
            if apply == 'д':
                self.cart.items = sorted_items
                print("Сортировка применена.")
        except Exception as e:
            print(f"Ошибка при сортировке: {e}")

    # функция сохранение каталога в файл
    def save_catalog(self):
        filename = input("Введите имя файла для сохранения (по умолчанию: catalog.json): ") or "catalog.json"
        if self.catalog.save_to_file(filename):
            print(f"Каталог успешно сохранен в файл {filename}")
        else:
            print("Не удалось сохранить каталог.")

    # функция загрузка каталога из файла
    def load_catalog(self):

        if self.catalog.products:
            confirm = input("Текущий каталог будет заменен. Продолжить? (д/н): ").lower()
            if confirm != 'д':
                return

        filename = input("Введите имя файла для загрузки (по умолчанию: catalog.json): ") or "catalog.json"
        if self.catalog.load_from_file(filename):
            print(f"Каталог успешно загружен из файла {filename}")
            self.catalog.display_catalog()
        else:
            print("Не удалось загрузить каталог.")

    # функция + нового товара в каталог
    def add_product_to_catalog(self):
        print("\n       Добавление нового товара в каталог:")

        try:
            name = input("Название товара: ")
            if not name:
                print("Название не может быть пустым.")
                return

            category = input("Категория товара: ")
            if not category:
                print("Категория не может быть пустой.")
                return

            price = float(input("Цена товара (руб.): "))
            if price <= 0:
                print("Цена должна быть положительной.")
                return

            weight = float(input("Вес товара (кг): "))
            if weight <= 0:
                print("Вес должен быть положительным.")
                return

            description = input("Описание товара (необязательно): ")

            product = self.catalog.add_product(name, category, price, weight, description)
            print(f"\nТовар успешно добавлен в каталог (сохранить каталог в файл в основном меню):\n{product}")
        except ValueError:
            print("Ошибка ввода данных. Пожалуйста, введите корректные значения.")

    # функция редактирование товара в каталоге
    def edit_product_in_catalog(self):
        self.show_catalog()

        product_id = input("Введите ID товара для редактирования (или 0 для отмены): ")
        if product_id == '0':
            return

        product = self.catalog.find_product_by_id(int(product_id))
        if not product:
            print("Товар не найден.")
            return

        print("\nТекущие данные товара:")
        print(product)

        print("\nВведите новые данные (оставьте пустым, чтобы не изменять):")

        try:
            updates = {}
            name = input(f"Название [{product.name}]: ")
            if name:
                updates['name'] = name

            category = input(f"Категория [{product.category}]: ")
            if category:
                updates['category'] = category

            price = input(f"Цена (руб.) [{product.price}]: ")
            if price:
                updates['price'] = float(price)

            weight = input(f"Вес (кг) [{product.weight}]: ")
            if weight:
                updates['weight'] = float(weight)

            description = input(f"Описание [{product.description}]: ")
            if description:
                updates['description'] = description

            if not updates:
                print("Ничего не изменено.")
                return

            updated_product = self.catalog.edit_product(product.id, **updates)
            if updated_product:
                print("\nТовар успешно обновлен (сохранить каталог в файл в основном меню):")
                print(updated_product)
            else:
                print("Не удалось обновить товар.")
        except ValueError as e:
            print(f"Ошибка ввода данных: {e}")

    # функция - товара из каталога
    def remove_product_from_catalog(self):
        self.show_catalog()

        product_id = input("Введите ID товара для удаления (или 0 для отмены): ")
        if product_id == '0':
            return

        try:
            product_id = int(product_id)
            product = self.catalog.find_product_by_id(product_id)
            if not product:
                print("Товар не найден.")
                return

            confirm = input(f"Вы уверены, что хотите удалить товар '{product.name}'? (д/н): ").lower()
            if confirm == 'д':
                if self.catalog.remove_product(product_id):
                    print("Товар успешно удален из каталога.")
                else:
                    print("Не удалось удалить товар.")
        except ValueError:
            print("Неверный формат ID.")

if __name__ == "__main__":
    ui = ShopUI()
    ui.run()
