from math import floor
from straddle_strategy3_list import trades_list, INSTRUMENT_BNF, INSTRUMENT_FNF, INSTRUMENT_NF

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THRUSDAY = 4
FRIDAY = 5

def get_required_margin(each_order, has_hedges):

    if each_order['instrument_type'] == INSTRUMENT_NF:
        if each_order['strategy_type'] == 'add_to_watchlist':
            return 40000 if has_hedges else 100000
        elif each_order['strategy_type'] == 'short_straddle':
            return 60000 if has_hedges else 120000
        else:
            print(f"UNKNOWN strategy type {each_order['strategy_type']}")

    elif each_order['instrument_type'] == INSTRUMENT_BNF:
        if each_order['strategy_type'] == 'add_to_watchlist':
            return 45000 if has_hedges else 140000
        elif each_order['strategy_type'] == 'short_straddle':
            return 60000 if has_hedges else 160000
        else:
            print(f"UNKNOWN strategy type {each_order['strategy_type']}")
            return 0
    
    elif each_order['instrument_type'] == INSTRUMENT_FNF:
        if each_order['strategy_type'] == 'add_to_watchlist':
            return 52000 if has_hedges else 105000
        elif each_order['strategy_type'] == 'short_straddle':
            return 67000 if has_hedges else 120000
        else:
            print(f"UNKNOWN strategy type {each_order['strategy_type']}")
            return 0

def calculate_margin():
    peak_margin = {
        MONDAY: 0,
        TUESDAY: 0,
        WEDNESDAY: 0,
        THRUSDAY: 0,
        FRIDAY: 0,
    }
    exitable_orders = {
        MONDAY: [],
        TUESDAY: [],
        WEDNESDAY: [],
        THRUSDAY: [],
        FRIDAY: [],
    }
    executed_orders = {
        MONDAY: {
            'strategy_list' : "",
            'count': 0,
        },
        TUESDAY: {
            'strategy_list' : "",
            'count': 0,
        },
        WEDNESDAY: {
            'strategy_list' : "",
            'count': 0,
        },
        THRUSDAY: {
            'strategy_list' : "",
            'count': 0,
        },
        FRIDAY: {
            'strategy_list' : "",
            'count': 0,
        },
    }
    for each_order in trades_list:
        for each_day in each_order['execution_days']:
            given_day = each_day['day']
            has_hedges = each_day['use_hedge']

            for exit_order in exitable_orders[given_day]:
                if (exit_order['exit_time'][0] < each_order['entry_time'][0]) or (exit_order['exit_time'][0] == each_order['entry_time'][0] and exit_order['exit_time'][1] < each_order['entry_time'][1]):
                    peak_margin[given_day] = peak_margin[given_day] - exit_order['margin_required']
                    exitable_orders[given_day].remove(exit_order)

            margin_required = get_required_margin(each_order, has_hedges)
            lot_size = 50 if each_order['instrument_type'] == 'NIFTY' else 25
            quantity = each_day['quantity'] / lot_size
            peak_margin[given_day] = peak_margin[given_day] + (margin_required * quantity)

            executed_orders[given_day]['strategy_list'] += f"\n# {each_order['strategy_name']} - {each_order['entry_time'][0]}:{each_order['entry_time'][1]} - {floor(margin_required * quantity)} - {floor(peak_margin[given_day])}"
            executed_orders[given_day]['count'] += + 1

            if 'exit_time' in each_day:
                exitable_orders[given_day].append({
                    'exit_time': each_day['exit_time'],
                    'margin_required': margin_required * quantity
                })

    print(f"# margin required for MONDAY = {peak_margin[MONDAY]}")
    print(f"# MONDAY TRADES = {executed_orders[MONDAY]['count']} {executed_orders[MONDAY]['strategy_list']}")
    print('\n################################\n')

    print(f"# margin required for TUESDAY = {peak_margin[TUESDAY]}")
    print(f"# TUESDAY TRADES = {executed_orders[TUESDAY]['count']} {executed_orders[TUESDAY]['strategy_list']}")
    print('\n################################\n')
    
    print(f"# margin required for WEDNESDAY = {peak_margin[WEDNESDAY]}")
    print(f"# WEDNESDAY TRADES = {executed_orders[WEDNESDAY]['count']} {executed_orders[WEDNESDAY]['strategy_list']}")
    print('\n################################\n')

    print(f"# margin required for THRUSDAY = {peak_margin[THRUSDAY]}")
    print(f"# THRUSDAY TRADES = {executed_orders[THRUSDAY]['count']} {executed_orders[THRUSDAY]['strategy_list']}")
    print('\n################################\n')

    print(f"# margin required for FRIDAY = {peak_margin[FRIDAY]}")
    print(f"# FRIDAY TRADES = {executed_orders[FRIDAY]['count']} {executed_orders[FRIDAY]['strategy_list']}")
    print('\n################################\n')

    print(f"# margin required for MONDAY = {peak_margin[MONDAY]}")
    print(f"# margin required for TUESDAY = {peak_margin[TUESDAY]}")
    print(f"# margin required for WEDNESDAY = {peak_margin[WEDNESDAY]}")
    print(f"# margin required for THRUSDAY = {peak_margin[THRUSDAY]}")
    print(f"# margin required for FRIDAY = {peak_margin[FRIDAY]}\n")

calculate_margin()
