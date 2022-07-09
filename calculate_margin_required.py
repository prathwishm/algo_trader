from straddle_strategy3_list import trades_list, NF_LOT_SIZE, BNF_LOT_SIZE

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THRUSDAY = 4
FRIDAY = 5

def get_required_margin(each_order, has_hedges):

    if each_order['instrument_type'] == 'NIFTY':
        if each_order['strategy_type'] == 'add_to_watchlist':
            return 40000 if has_hedges else 100000
        elif each_order['strategy_type'] == 'short_straddle':
            return 60000 if has_hedges else 120000
        else:
            print(f"UNKNOWN strategy type {each_order['strategy_type']}")

    elif each_order['instrument_type'] == 'BANKNIFTY':
        if each_order['strategy_type'] == 'add_to_watchlist':
            return 45000 if has_hedges else 140000
        elif each_order['strategy_type'] == 'short_straddle':
            return 60000 if has_hedges else 160000
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
    for each_order in trades_list:
        for each_day in each_order['execution_days']:
            given_day = each_day['day']
            has_hedges = False if 'hedge_multiplier' not in each_day else True
            hedge_multiplier = 1 if 'hedge_multiplier' not in each_day else each_day['hedge_multiplier']

            for exit_order in exitable_orders[given_day]:
                if (exit_order['exit_time'][0] < each_order['entry_time'][0]) or (exit_order['exit_time'][0] == each_order['entry_time'][0] and exit_order['exit_time'][1] < each_order['entry_time'][1]):
                    peak_margin[given_day] = peak_margin[given_day] - exit_order['margin_required']
                    exitable_orders[given_day].remove(exit_order)

            margin_required = get_required_margin(each_order, has_hedges)
            lot_size = 50 if each_order['instrument_type'] == 'NIFTY' else 25
            quantity = (each_order['quantity'] * each_day['quantity_multiplier'] * hedge_multiplier) / lot_size
            peak_margin[given_day] = peak_margin[given_day] + (margin_required * quantity)

            if 'exit_time' in each_day:
                exitable_orders[given_day].append({
                    'exit_time': each_day['exit_time'],
                    'margin_required': margin_required * quantity
                })

    print(f"margin required for MONDAY = {peak_margin[MONDAY]}")
    print(f"margin required for TUESDAY = {peak_margin[TUESDAY]}")
    print(f"margin required for WEDNESDAY = {peak_margin[WEDNESDAY]}")
    print(f"margin required for THRUSDAY = {peak_margin[THRUSDAY]}")
    print(f"margin required for FRIDAY = {peak_margin[FRIDAY]}")

calculate_margin()