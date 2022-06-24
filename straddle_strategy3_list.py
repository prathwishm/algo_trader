
NF_LOT_SIZE = 50
BNF_LOT_SIZE = 25

CORE_STRATEGY_LOT_MULTIPLIER = 2
EXPIRY_STRATEGY_LOT_MULTIPLIER = 1
OTHER_STRATEGY_LOT_MULTIPLIER = 1

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THRUSDAY = 4
FRIDAY = 5


trades_list = [
    {
        'strategy_name': '9_16_strangle',
        'strategy_type': 'add_nf_strangle_to_watchlist',
        'entry_time': [9, 16, 0],
        'quantity': NF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 15, 4],
            'quantity_multiplier': 1
        }, {
            'day': WEDNESDAY,
            'exit_time': [15, 15, 4],
            'quantity_multiplier': 1
        }, {
            'day': THRUSDAY,
            'exit_time': [15, 15, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'bnf_9_16_expiry_strangle',
        'strategy_type': 'short_bnf_straddle',
        'entry_time': [9, 16, 0],
        'exit_time': [11, 44, 4],
        'quantity': BNF_LOT_SIZE * EXPIRY_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': MONDAY,
            'quantity_multiplier': 1
        }, {
            'day': WEDNESDAY,
            'exit_time': [11, 44, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_9_16_expiry_strangle',
        'strategy_type': 'short_nifty_straddle',
        'entry_time': [9, 16, 0],
        'quantity': NF_LOT_SIZE * EXPIRY_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.2,
        'strangle': False,
        'execution_days': [{
            'day': THRUSDAY,
            'exit_time': [12, 44, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '9_20_straddle',
        'strategy_type': 'add_bnf_straddle_to_watchlist',
        'entry_time': [9, 19, 54],
        'quantity': BNF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [14, 54, 54],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [14, 54, 54],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [14, 54, 54],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [14, 54, 54],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [14, 54, 54],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_9_40_strangle',
        'strategy_type': 'short_nifty_straddle',
        'entry_time': [9, 39, 52],
        'quantity': NF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.35,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 8, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 8, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 8, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 8, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 8, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '10_05_strangle',
        'strategy_type': 'add_bnf_strangle_to_watchlist',
        'entry_time': [10, 5, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.2,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 5, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 5, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 5, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 5, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 5, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_10_45_strangle',
        'strategy_type': 'short_nifty_straddle',
        'entry_time': [10, 44, 52],
        'quantity': NF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.28,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 10, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 10, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 10, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 10, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 10, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '11_15_strangle',
        'strategy_type': 'add_bnf_strangle_to_watchlist',
        'entry_time': [11, 15, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.18,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 0, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 0, 4],
            'quantity_multiplier': 2
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 0, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 0, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 0, 4],
            'quantity_multiplier': 2
        }],
    },
    {
        'strategy_name': 'nf_11_30_strangle',
        'strategy_type': 'short_nifty_straddle',
        'entry_time': [11, 29, 52],
        'quantity': NF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 17, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 17, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 17, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 17, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 17, 4],
            'quantity_multiplier': 2
        }],
    },
    {
        'strategy_name': '11_45_strangle',
        'strategy_type': 'add_bnf_strangle_to_watchlist',
        'entry_time': [11, 44, 54],
        'quantity': BNF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.20,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 12, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 12, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 12, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 12, 4],
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'exit_time': [15, 12, 4],
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '13_20_strangle',
        'strategy_type': 'add_bnf_strangle_to_watchlist',
        'entry_time': [13, 20, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'execution_days': [{
            'day': MONDAY,
            'exit_time': [15, 18, 4],
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'exit_time': [15, 18, 4],
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'exit_time': [15, 18, 4],
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'exit_time': [15, 18, 4],
            'quantity_multiplier': 1
        }],
    },
]
