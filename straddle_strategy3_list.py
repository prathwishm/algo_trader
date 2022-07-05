
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

FAR_TO_EXPIRY_TARGET_PRICE = 0.35
NEAR_TO_EXPIRY_TARGET_PRICE = 0.25

# NIFTY Margin: 1L, 1.2L
# BNF 1.4 , (2.3L)1.7
# MONDAY: 1*2 + 1.4*2 + 1.2 + 1.7 + 1.2*2 + 1.4 + 1.2 + 1.4 + 1.7 = 15.8
# TUESDAY: 1.4*2 + 1.2 + 1.7 + 1.2*2 + 1.4*2 + 1.2 + 1.7 = 13.8
# WEDNESDAY: 1*2 + 1.4*1 + 1.4*2 + 1.2 + 1.4 + 1.2*2 + 1.4 + 1.2 + 1.4 = 16.6
# THRUSDAY: 1*2 + 1.7 + 1.2 + 1.4*2 + 1.2 + 1.4 + 1.2*2 + 1.4 + 1.2 + 1.4 = 16.7
# FRIDAY: 1.4*2 + 1.2 + 1.4 + 1.2*2 + 1.4 + 1.2*2 + 1.7 = 13.3
trades_list = [
    {
        'strategy_name': '9_16_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'NIFTY',
        'entry_time': [9, 16, 0],
        'quantity': NF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 15, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }, {
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 15, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }, {
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 15, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'bnf_9_16_expiry_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [9, 16, 0],
        'quantity': BNF_LOT_SIZE * EXPIRY_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [11, 44, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }, {
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [11, 44, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_9_16_expiry_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'NIFTY',
        'entry_time': [9, 16, 0],
        'quantity': NF_LOT_SIZE * EXPIRY_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.2,
        'strangle': False,
        'execution_days': [{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [12, 44, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '9_20_straddle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [9, 19, 54],
        'quantity': BNF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'strangle': False,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_9_40_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'NIFTY',
        'entry_time': [9, 39, 52],
        'quantity': NF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.35,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '10_05_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [10, 5, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.2,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': 'nf_10_45_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'NIFTY',
        'entry_time': [10, 44, 52],
        'quantity': NF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.28,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '11_15_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [11, 15, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.18,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 2
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 2
        }],
    },
    {
        'strategy_name': 'nf_11_30_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'NIFTY',
        'entry_time': [11, 29, 52],
        'quantity': NF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 2
        }],
    },
    {
        'strategy_name': '11_45_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [11, 44, 54],
        'quantity': BNF_LOT_SIZE * CORE_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.20,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'hedge_multiplier': 2,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '13_20_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [13, 20, 0],
        'quantity': BNF_LOT_SIZE * EXPIRY_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }],
    },
    {
        'strategy_name': '13_20_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': 'BANKNIFTY',
        'entry_time': [13, 21, 0],
        'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_LOT_MULTIPLIER,
        'sl_percent': 0.25,
        'strangle': True,
        'execution_days': [{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'hedge_multiplier': 3,
            'quantity_multiplier': 1
        }],
    },
]
