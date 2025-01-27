from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import GraphicsCard, CardsUser, Tokens, MiningStatus, Order
from .utils import mining_income
from decimal import Decimal
from django.db.models import F
import threading
import time
from .forms import OrderForm
import random
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404



def blockchain_page(request):
    return render(request, 'blockchain.html')



def store_view(request):
    graphics_cards = GraphicsCard.objects.all()  
    return render(request, 'store.html', {'graphics_cards': graphics_cards})


def buy_card(request, name):
    card = GraphicsCard.objects.get(name=name)
    try:
        user = Tokens.objects.get(id=request.session['id'])
    except:
        user = Tokens.objects.create(id=request.session['id'])
    if card.price > user.CLT:
        return JsonResponse({'error': 'Недосточно монет CLT'})
    new_balance = float(user.CLT) - float(card.price)
    Tokens.objects.filter(id=request.session['id']).update(CLT=new_balance)
    CardsUser.objects.create(
        user=request.session['id'],
        name=card.name,
        brand=card.brand,
        memory_size=card.memory_size,
        price=card.price,
        stock_quantity=card.stock_quantity,
        MH=card.MH
    )
    return JsonResponse({'RESULT': f'Вы купили видеокарту {card}'})




def mining_simulator(request):
    # Стандартные значения
    network_hashrate = 1000000  # Хэшрейт сети (например, 1,000,000 MH/s)
    reward_per_block = 2  # Вознаграждение за блок (например, 2 ETH)
    block_time = 13  # Время нахождения блока (например, 13 секунд)
    simulation_duration_hours = 24  # Продолжительность симуляции (например, 24 часа)

    # Получаем все видеокарты пользователя
    cards = CardsUser.objects.filter(user=request.session['id'])

    # Суммируем хэшрейты всех карт
    total_hashrate = sum(card.MH for card in cards)

    # Рассчитываем доход
    user_income = mining_income(
        user_hashrate=total_hashrate, 
        network_hashrate=network_hashrate, 
        reward_per_block=reward_per_block, 
        block_time=block_time, 
        simulation_duration_hours=simulation_duration_hours
    )

    # Передаем данные в шаблон
    return render(request, 'mining_simulator.html', {
        'user_income': user_income,
        'total_hashrate': total_hashrate,
        'network_hashrate': network_hashrate,
        'reward_per_block': reward_per_block,
        'block_time': block_time,
        'simulation_duration_hours': simulation_duration_hours,
        'cards': cards
    })


def calculate_mining_income(user_hashrate, network_hashrate, reward_per_block, block_time, duration_hours):
    """
    Рассчитывает доход от майнинга на основе хэшрейта пользователя и других параметров.
    """
    # Количество блоков, найденных за указанный период
    blocks_mined = (duration_hours * 3600) / block_time

    # Доля пользователя в сети (user_hashrate / network_hashrate)
    user_share = user_hashrate / network_hashrate if network_hashrate > 0 else 0

    # Общий доход пользователя
    user_income = blocks_mined * reward_per_block * user_share
    return user_income

    

def start_mining(request):
    # Проверяем статус майнинга
    mining_status, created = MiningStatus.objects.get_or_create(user=request.session['id'])

    if mining_status.is_mining:
        return render(request, 'mining.html', {
            'message': "Майнинг уже запущен."
        })

    # Устанавливаем статус майнинга
    mining_status.is_mining = True
    mining_status.save()

    # Параметры сети
    network_hashrate = 1000000  # MH/s
    reward_per_block = 2  # ETH
    block_time = 13  # секунд

    # Получаем видеокарты пользователя
    cards = CardsUser.objects.filter(user=request.session['id'])

    # Рассчитываем общий хэшрейт пользователя
    total_hashrate = sum(card.MH for card in cards)

    # Поток для майнинга
    def mining_process():
        tokens = Tokens.objects.get(id=request.session['id'])
        while True:
            # Проверяем статус
            status = MiningStatus.objects.get(user=request.session['id'])
            if not status.is_mining:
                break

            # Расчет дохода за один цикл (например, за 1 минуту)
            cycle_duration_seconds = 60
            user_income = 2
            
            # Обновляем баланс пользователя
            tokens.CLT += user_income
            tokens.save()
            

            

            # Задержка до следующего цикла
            time.sleep(cycle_duration_seconds)

    # Запускаем поток
    threading.Thread(target=mining_process).start()
    status = MiningStatus.objects.get(user=request.session['id'])
    tokens = Tokens.objects.get(id=request.session['id'])
    context = {
            'message': "Майнинг запущен." if status.is_mining else "Майнинг остановлен.",
            'total_balance': tokens.CLT,  # Замените user_tokens на соответствующий объект
            'seconds_to_next_reward': 60,  # Вычислите это значение
            'total_hashrate': total_hashrate,  # Укажите общую скорость хэширования
        }

    return render(request, 'mining.html', context=context)

def stop_mining(request):
    # Останавливаем майнинг
    MiningStatus.objects.filter(user=request.session['id']).update(is_mining=False)
    return render(request, 'mining.html', {
        'message': "Майнинг остановлен."
    })


def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.session['id']

            # Проверка на доступность средств при продаже
            if order.order_type == 'sell':
                user_tokens = Tokens.objects.get(id=request.session['id'])
                if user_tokens.CLT < order.amount:
                    return render(request, 'create_order.html', {
                        'form': form,
                        'error': 'Недостаточно средств для создания ордера на продажу.'
                    })

                # Вычитаем монеты у продавца
                user_tokens.CLT -= order.amount
                user_tokens.save()

            order.save()
            return redirect('marketplace')  # Перенаправляем на биржу

    else:
        form = OrderForm()

    return render(request, 'create_order.html', {'form': form})



def marketplace(request):
    """
    Отображает страницу биржи с балансом пользователя.
    """
    buy_orders = Order.objects.filter(order_type='buy').order_by('-created_at')
    sell_orders = Order.objects.filter(order_type='sell').order_by('-created_at')

    tokens = Tokens.objects.get(id=request.session['id'])

    return render(request, 'marketplace.html', {
        'buy_orders': buy_orders,
        'sell_orders': sell_orders,
        'user_tokens': tokens, 
    })


def fulfill_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    user_tokens = Tokens.objects.get(id=request.session['id'])

    # Покупка ордера
    if order.order_type == 'buy':
        if user_tokens.NBM < order.amount:
            messages.error(request, 'Недостаточно монет для выполнения ордера на продажу.')
            return redirect('marketplace')

        # Выполняем перевод монет и денег
        buyer_tokens = Tokens.objects.get(id=order.user.id_user)
        buyer_tokens.NBM += order.amount
        buyer_tokens.save()

        user_tokens.NBM -= order.amount
        user_tokens.CLT += order.amount * order.price_per_unit
        user_tokens.save()

    # Продажа ордера
    elif order.order_type == 'sell':
        total_price = order.amount * order.price_per_unit
        if user_tokens.CLT < total_price:
            messages.error(request, 'Недостаточно средств для выполнения ордера на покупку.')
            return redirect('marketplace')

        # Выполняем перевод монет и денег
        seller_tokens = Tokens.objects.get(id=order.user)
        seller_tokens.CLT += total_price
        seller_tokens.save()

        user_tokens.CLT -= total_price
        user_tokens.NBM += order.amount
        user_tokens.save()

    # Помечаем ордер выполненным
    order.is_fulfilled = True
    order.save()

    messages.success(request, 'Операция выполнена успешно.')
    return redirect('marketplace')



def get_candlestick_data(request):
    """
    Возвращает данные для свечного графика.
    """
    # Пример генерации данных графика (в реальном случае используйте данные из базы)
    start_time = datetime.now() - timedelta(hours=5)
    data = []
    for i in range(5):  # 5 свечей (можно увеличить)
        open_price = random.uniform(100, 150)
        close_price = random.uniform(100, 150)
        high_price = max(open_price, close_price, random.uniform(150, 200))
        low_price = min(open_price, close_price, random.uniform(50, 100))
        data.append({
            't': (start_time + timedelta(hours=i)).isoformat(),
            'o': round(open_price, 2),
            'h': round(high_price, 2),
            'l': round(low_price, 2),
            'c': round(close_price, 2)
        })

    return JsonResponse(data, safe=False)