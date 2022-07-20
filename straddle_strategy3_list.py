
NF_LOT_SIZE = 50
BNF_LOT_SIZE = 25
FNF_LOT_SIZE = 40

CORE_STRATEGY_WITH_HEDGE_LOTS = 5 # QTY - 2 HEDGE - 2
CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS = 6 # QTY - 2 HEDGE - 3

OTHER_STRATEGY_WITH_HEDGE_LOTS = 3 # QTY - 1 HEDGE - 3
OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS = 3 # QTY - 1 HEDGE - 3
OTHER_LTD_QTY_WITH_HEDGE_LOTS = 2 # QTY - 1 HEDGE - 2

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THRUSDAY = 4
FRIDAY = 5

FAR_TO_EXPIRY_TARGET_PRICE = 0.4
NEAR_TO_EXPIRY_TARGET_PRICE = 0.3

NRML_DAYS = [THRUSDAY]

INSTRUMENT_NF = 'NIFTY'
INSTRUMENT_BNF = 'BANKNIFTY'
INSTRUMENT_FNF = 'FINNIFTY'

# margin required for MONDAY = 1835000.0
# margin required for TUESDAY = 1800000.0
# margin required for WEDNESDAY = 1800000.0
# margin required for THRUSDAY = 2070000.0
# margin required for FRIDAY = 1890000.0

# DEFAULT SL NIFTY = 0.25
# DEFAULT SL BANKNIFTY = 0.2

trades_list = [
    {
        'strategy_name': 'NF_09_16_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [9, 16, 0],
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 15, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        }, {
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 15, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }, {
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 45, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'BNF_09_16_expiry_straddle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [9, 16, 0],
        'sl_percent': 0.2,
        'strangle': False,
        'execution_days': [{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [11, 44, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }, {
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [11, 44, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'NF_09_16_expiry_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [9, 16, 0],
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [12, 44, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'BNF_09_20_straddle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [9, 19, 54],
        'strangle': False,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [14, 54, 54],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        # Updated from execute to watchlist
        'strategy_name': 'NF_09_40_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [9, 39, 52],
        'sl_percent': 0.35,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 48, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'NF_09_40_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [9, 39, 52],
        'sl_percent': 0.35,
        'strangle': True,
        'strike_distance': 100,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 8, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'BNF_10_05_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [10, 5, 0],
        'sl_percent': 0.2,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 5, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 45, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_WITH_HEDGE_LOTS,
            'exit_time': [15, 5, 4],
        }],
    },
    {
        'strategy_name': 'NF_10_45_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [10, 44, 52],
        'sl_percent': 0.28,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'use_hedge': True,
            # Updated quantity multiplier & lot type to match margin
            'quantity': 4 * NF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'use_hedge': True,
            # Updated quantity multiplier & lot type to match margin
            'quantity': 2 * NF_LOT_SIZE * OTHER_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 40, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 10, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'BNF_11_15_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [11, 15, 0],
        'sl_percent': 0.18,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'use_hedge': True,
            'quantity': 2 * BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 0, 4],
            'use_hedge': True,
            # removed quantity multiplier of 1.5 as backtest was not found great for Friday
            'quantity': BNF_LOT_SIZE * OTHER_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'NF_11_30_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_NF,
        'entry_time': [11, 29, 52],
        'sl_percent': 0.25,
        'strangle': True,
        'strike_distance': 50,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 47, 4],
            'use_hedge': True,
            'quantity': NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 17, 4],
            'use_hedge': True,
            'quantity': 2 * NF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        'strategy_name': 'BNF_11_45_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [11, 44, 54],
        'sl_percent': 0.20,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 42, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 12, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * CORE_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        # Core staregy downgraded to avoid margin shortfall
        'strategy_name': 'BNF_13_20_strangle_watchlist',
        'strategy_type': 'add_to_watchlist',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [13, 20, 0],
        'sl_percent': 0.25,
        'strangle': True,
        'execution_days': [{
            'day': MONDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': WEDNESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': THRUSDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 48, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_EXPIRY_STRATEGY_WITH_HEDGE_LOTS,
        }],
    },
    {
        # Making it short straddle instead of watchlist
        'strategy_name': '13_20_strangle_execute',
        'strategy_type': 'short_straddle',
        'instrument_type': INSTRUMENT_BNF,
        'entry_time': [13, 21, 0],
        'sl_percent': 0.25,
        'strangle': True,
        'execution_days': [{
            'day': TUESDAY,
            'target_percent': NEAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        },{
            'day': FRIDAY,
            'target_percent': FAR_TO_EXPIRY_TARGET_PRICE,
            'exit_time': [15, 18, 4],
            'use_hedge': True,
            'quantity': BNF_LOT_SIZE * OTHER_LTD_QTY_WITH_HEDGE_LOTS,
        }],
    }
]
