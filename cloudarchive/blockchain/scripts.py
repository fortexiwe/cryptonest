from blockchain.models import GraphicsCard

def fill_graphics_cards():
    cards = [
        {"name": "GeForce RTX 4090", "brand": "NVIDIA", "memory_size": 24576, "price": 1599.99, "stock_quantity": 10, 'MH': 50},
        {"name": "Radeon RX 7900 XTX", "brand": "AMD", "memory_size": 24576, "price": 1799.99, "stock_quantity": 8, 'MH': 45},
        {"name": "GeForce RTX 4080", "brand": "NVIDIA", "memory_size": 16384, "price": 1199.99, "stock_quantity": 15, 'MH' : 42},
        {"name": "Radeon RX 6800 XT", "brand": "AMD", "memory_size": 16384, "price": 999.99, "stock_quantity": 5, 'MH': 36},
        {"name": "GeForce RTX 4070 Ti", "brand": "NVIDIA", "memory_size": 12288, "price": 799.99, "stock_quantity": 20, 'MH': 33},
        {"name": "Radeon RX 6700 XT", "brand": "AMD", "memory_size": 12288, "price": 629.99, "stock_quantity": 12, 'MH': 24},
        {"name": "GeForce GTX 1660 Ti", "brand": "NVIDIA", "memory_size": 6144, "price": 279.99, "stock_quantity": 50, 'MH': 20},
    ]

    for card in cards:
        GraphicsCard.objects.create(
            name=card["name"],
            brand=card["brand"],
            memory_size=card["memory_size"],
            price=card["price"],
            stock_quantity=card["stock_quantity"]
        )
