def mining_income(user_hashrate, network_hashrate, reward_per_block, block_time, simulation_duration_hours):
    """
    Симулятор майнинга для подсчета дохода.

    :param user_hashrate: хэшрейт пользователя в MH/s
    :param network_hashrate: хэшрейт сети в MH/s
    :param reward_per_block: вознаграждение за блок в криптовалюте (например, в ETH или BTC)
    :param block_time: время нахождения блока (в секундах)
    :param simulation_duration_hours: продолжительность симуляции в часах
    :return: расчетный доход
    """
    # Преобразование времени в секунды
    simulation_duration_seconds = simulation_duration_hours * 3600

    # Доля хэшрейта пользователя от общего хэшрейта сети
    user_share = user_hashrate / network_hashrate

    # Количество блоков, найденных за время симуляции
    blocks_found = simulation_duration_seconds / block_time

    # Доход пользователя
    user_income = user_share * blocks_found * reward_per_block

    return user_income