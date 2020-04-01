"""
Functions providing formatted response to user arguments.
Miha Lotric 2019
"""
from cool_defi_bot.api.custom_exceptions import *
from cool_defi_bot.api.getters import *
from cool_defi_bot.api.helpers import api_call, could_float
from cool_defi_bot.api.formatters import *
import cool_defi_bot.config as config
from dotenv import load_dotenv


load_dotenv()  # Load keys from .env file
POOLS_KEY = os.getenv("POOLS_KEY")  # Blocklytics pools API key


def get_pool(request):
    """Return pool info for a specific token.
    Args:
        request [list]: Args specifying user's request.
    Returns:
        tuple: HTML-formatted message and an ethereum address of the requested token.
    """
    # Check formatting
    if 0 < len(request) < 3:
        days = '1' if len(request) == 1 else request[1]  # Default num of days ago is one
        token = str(request[0])
    else:
        raise FormatError("<b>Please check the formatting.</b>\nTry it:\n<code>/pools dai</code>")
    if not days.isdigit() or int(days) < 1:
        raise FormatError("You must enter an integer for days ago.")
    # Get data
    token_data = get_token_pool(token)
    address = token_data['exchange']
    if not address:
        raise DataError('<b>No results found</b>\nTry a different symbol.')
    annualized_returns = get_token_annualized(address, days)
    annualized_returns = annualized_returns[0] if len(annualized_returns) else {}
    # Format the data
    formatted_response = format_annualized_returns(token_data, annualized_returns)
    return formatted_response, address


def get_deepest():
    """Return tokens with largest liquidities.
    Returns:
        str: HTML-formatted message.
    """
    url = config.URLS['deepest']
    api_params = {'limit': 5,
                  'orderBy': 'usdLiquidity',
                  'direction': 'desc',
                  'key': POOLS_KEY
                  }
    response = api_call(url, params=api_params)
    formatted_response = format_deepest(response['results'])
    return formatted_response


def get_aggregator_offer(order, aggregator):
    """"Return price and platform routing for exchange aggregators.
        Args:
            request [list]: Args specifying user's request.
            aggregator [str]: Which aggregator to use.
        Returns:
            str: HTML-formatted message.
    """
    aggregator_fun = {"dexag": get_dexag_offer,
                      "oneinch": get_1inch_offer,
                      "paraswap": get_paraswap_offer,
                      "zerox": get_0x_offer} # TODO move to config?
    two_way = config.AGGREGATOR_PREFERENCES[aggregator]['two_way']
    default_token = config.AGGREGATOR_PREFERENCES[aggregator]['default_token']
    params = get_formatted_input(order, two_way=two_way, default_token=default_token)
    result = aggregator_fun[aggregator](params)
    formatted = format_offer(result)
    return formatted


def get_formatted_input(order, two_way=False, default_token='ETH'):
    """Check if passed arguments are valid and return them formatted.

    Args:
        order [list]: Args specifying user's request.
        two_way [bool]: Can order be made with specifying to_amount instead of from_amount.
    Returns:
        dict: Request with the following keys:
                toToken [str]: Buying token's symbol.
                fromToken [str]: Selling token's symbol. Default is ETH (or WETH).
                toAmount [float/bool]: If user specifies amount of tokens he wants to buy is then it is a number,
                                           otherwise None.
                fromAmount [float/bool]: If user specifies amount of tokens he wants to sell then it is a that
                                             number. If the doesn't and amount of tokens he wants to buy isn't either it
                                             is 1. Otherwise None.

              Example of return for input ['REP', '2', 'DAI']:
                {'toToken': 'DAI',
                 'fromToken': 'REP',
                 'toAmount': 2,
                 'fromAmount': None
                 }
              Example of return for input ['DAI']:
                {'toToken': 'ETH',
                 'fromToken': 'DAI',
                 'toAmount': None,
                 'fromAmount': 1
                 }

    Function first checks if the types of the arguments passed match any of the options. Those options are:
        ['DAI'] = 'How many DAI can 1 ETH buy?'
            1 ETH -> ? DAI
        ['2', 'DAI'] = 'How many DAI can 2 ETH buy?'
            2 ETH -> ? DAI
        ['DAI', 'REP'] = 'How many REP can 1 DAI buy?'
            1 REP -> ? DAI
        ['2', 'REP', 'DAI'] = 'How many DAI can 2 REP buy?'
            2 REP -> ? DAI
        ['DAI', '2', 'ETH'] = 'How many DAI do I need to buy 2 ETH?'
            ? DAI -> 2 ETH
    """
    # 'S' stands for string - token
    # 'F' stands for a float - amount
    orders = {'SFS': ['fromToken', 'toAmount', 'toToken'],
              'FSS': ['fromAmount', 'fromToken', 'toToken'],
              'FS': ['toAmount', 'toToken'],
              'SS': ['fromToken', 'toToken'],
              'S': ['toToken']
              }
    types = ''.join([('F' if could_float(arg) else 'S') for arg in order])
    meaning = orders.get(types)
    reverse = 1 if types == 'SFS' else 0
    if not meaning or (reverse and not two_way):
        raise FormatError('Format not supported')
    order_dict = dict([(meaning[i], order[i].upper()) for i in range(len(order))])
    if not (order_dict.get('toAmount') or order_dict.get('fromAmount')):
        order_dict['fromAmount'] = 1  # Default value is 1 if no amount specified
    elif (float(order_dict.get('toAmount', 1)) <= 0) or (float(order_dict.get('fromAmount', 1)) <= 0):
        # Check if  toAmount or fromAmount is negative
        raise DataError('<b>Amount needs to be positive</b>')
    order_dict['fromAmount'] = float(order_dict['fromAmount']) if order_dict.get('fromAmount') else None
    order_dict['toAmount'] = float(order_dict['toAmount']) if order_dict.get('toAmount') else None
    order_dict['fromToken'] = order_dict.get('fromToken', default_token)  # Default token is if no selling token
    # Buying and selling token can't be the same
    if order_dict['fromToken'] == order_dict['toToken']: raise DataError('Invalid token combination')

    return order_dict


