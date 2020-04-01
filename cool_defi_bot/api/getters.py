"""
Functions that fetch and manipulate data into common schemas.
Miha Lotric, Dec 2019
"""
import os
from cool_defi_bot.api.custom_exceptions import DataError, APIError
from dotenv import load_dotenv
from cool_defi_bot.api.helpers import api_call
from cool_defi_bot import config


load_dotenv()  # Load keys from .env file
POOLS_KEY = os.getenv("POOLS_KEY")  # Blocklytics pools API key


def get_token_pool(token):
    """Return pool data for a specific token.
    Args:
        token [str]: Token symbol.
    Returns:
        dict: Token data. With keys: base, baseLiquidity, baseName, basePrice, baseSymbol, baseVolume, exchange,
              factory, ownershipToken, platform, timestamp, token, tokenLiquidity, tokenName, tokenSymbol, tokenVolume,
              usdLiquidity, usdPrice, usdVolume.
    """
    url = config.URLS['pools_exchanges']
    response = api_call(url, {'key': POOLS_KEY})
    if not response:
        raise APIError('<b Unavailable</b>\nPlease try again later')
    # TODO should this really be a list? - there are some tokens with the same name
    exchanges = [row for row in response['results'] if str(row.get('tokenSymbol', '')).lower() == str(token).lower()]
    if len(exchanges) == 0:
        raise DataError("Try a different symbol.")
    return exchanges[0]  # Returning only the first result among all tokens with the same symbol


def get_token_annualized(address, days):
    """Return annualized returns for a specific token.
    Args:
        days [int]: Days ago for which to display annualized returns.
        address [str]: Ethereum token address.
    Return:
        dict: Annualized returns for a specified token.
              key [str]: Days annualized.
              value [str]: Annualized returns.
    """
    url = f"{config.URLS['annualized_returns']}/{address}"
    response = api_call(url, params={'daysBack': days, 'key': POOLS_KEY})
    # if type(response) == dict and response.get('code') == 5:  TODO Is this useful?
    #     raise APIError('<b Unavailable</b>\nPlease try again later')
    return response


def get_dexag_offer(user_params):
    """Return dexag offer for the best price based on a user order.

    Args:
        user_params [dict]: User request, formatted the following way:
                                fromToken [str]: Symbol for the token user is buying.
                                toToken [str]: Symbol for the token user is selling.
                                fromAmount [float/bool]: Amount of token user is buying.
                                                             If toAmount is specified it is None.
                                toAmount [float/int/bool]: Amount of token user is selling.
                                                           If fromAmount is specified it is None.

    Returns:
        dict: Processed user request containing amount user wants to buy/sell, price and aggregators with specified
              percentages to get the best price. Formatted the following way:
                  from_token [str]: Symbol for the token user is buying.
                  to_token [str]: Symbol for the token user is selling.
                  from_amount [float]: Amount of token user is buying.
                  to_amount [float]: Amount of token user is selling.
                  rate [float]: Price between tokens (to_token / from_token).
                  exchanges [dict]: What percentage of token amount should be swapped at which exchange.
                                    key: Name of the exchange.
                                    value: Percentage.
                  aggregator [str]: Name of the aggregator offering this price - 'dex.ag'.
    """
    # 'PREPARE FOR REQUEST CALL'
    api_params = {'from': user_params['fromToken'],
                  'to': user_params['toToken'],
                  'dex': 'ag'
                  }
    selling = user_params['fromAmount']
    if selling:
        api_params.update({'fromAmount': user_params['fromAmount']})
    else:
        api_params.update({'toAmount': user_params['toAmount']})

    # 'REQUEST CALL'
    url = config.URLS['aggregators']['dexag']['offer']
    response = api_call(url, api_params)
    if response.get('error'):
        raise DataError('<b>Token not found</b>\nPlease try another symbol')

    # 'FORMAT IT'
    relative_rate = float(response['price'])
    if selling:
        from_amount = user_params['fromAmount']
        to_amount = user_params['fromAmount'] * relative_rate
        rate = relative_rate
    else:
        from_amount = user_params['toAmount'] * relative_rate
        to_amount = user_params['toAmount']
        rate = 1/relative_rate
    # This is a general format that is passed to the formatting function.
    data = {'from_token': user_params['fromToken'],
            'to_token': user_params['toToken'],
            'from_amount': from_amount,
            'to_amount': to_amount,
            'rate': rate,
            'exchanges': response['liquidity'],
            'aggregator': 'dexag'
            }

    return data


def get_1inch_offer(user_params):
    """Return 1inch offer for the best price based on a user order.

        Args:
            user_params [dict]: User request, formatted the following way:
                                    fromToken [str]: Symbol for the token user is buying.
                                    toToken [str]: Symbol for the token user is selling.
                                    fromAmount [float/bool]: Amount of token user is buying.
                                                                 If toAmount is specified it is None.
                                    toAmount [float/int/bool]: Amount of token user is selling.
                                                               If fromAmount is specified it is None.

        Returns:
            dict: Processed user request containing amount user wants to buy/sell, price and aggregators with specified
                  percentages to get the best price. Formatted the following way:
                      from_token [str]: Symbol for the token user is buying.
                      to_token [str]: Symbol for the token user is selling.
                      from_amount [float]: Amount of token user is buying.
                      to_amount [float]: Amount of token user is selling.
                      rate [float]: Price between tokens (to_token / from_token).
                      exchanges [dict]: What percentage of token amount should be swapped at which exchange.
                                        key: Name of the exchange.
                                        value: Percentage.
                      aggregator [str]: Name of the aggregator offering this price - '1inch'.
    """
    # 'GET TOKEN INFO'
    url = config.URLS['aggregators']['oneinch']['tokens']
    tokens = api_call(url)
    # Capitalize keys in token dict in order to find them
    tokens = dict([(symbol.upper(), data) for symbol, data in tokens.items()])
    from_token_data = tokens.get(user_params['fromToken'])
    to_token_data = tokens.get(user_params['toToken'])
    if not (from_token_data and to_token_data):
        raise DataError('<b>Token not found</b>\nPlease try another symbol')

    # 'PREPARE FOR REQUEST CALL'
    api_params = {'fromTokenSymbol': user_params['fromToken'],
                  'toTokenSymbol': user_params['toToken'],
                  'amount': int(user_params['fromAmount'] * 10**(from_token_data['decimals'])),
                  'slippage': 0.1
                  }

    # 'REQUEST CALL'
    url = config.URLS['aggregators']['oneinch']['offer']
    response = api_call(url, api_params)
    # Checking if there is problem with API call
    if response.get('message'):  # TODO Is this needed?
        raise APIError('<b>API Error</b>\nPlease try again later')
    if (int(response['toTokenAmount']) == 0) and (user_params['fromAmount'] != 0):
        # 1inch tokens displays more tokens than it can actually offer
        raise DataError("<b>Token not found</b>\nPlease try another symbol")

    # 'FORMAT IT'
    exchanges = dict([(exchange['name'], exchange['part'])
                      for exchange in response['exchanges']
                      if exchange['part'] != 0
                      ])
    # This is a general format that is passed to the formatting function.
    data = {'from_token': user_params['fromToken'],
            'to_token': user_params['toToken'],
            'from_amount': user_params.get('fromAmount'),
            'to_amount': int(response['toTokenAmount']) * 10**(-to_token_data['decimals']),
            'rate': int(response['toTokenAmount']) / int(response['fromTokenAmount']),
            'exchanges': exchanges,
            'aggregator': '1inch'
            }

    return data


def get_paraswap_offer(user_params):
    """Return paraswap offer for the best price based on a user order.

        Args:
            user_params [dict]: User request, formatted the following way:
                                    fromToken [str]: Symbol for the token user is buying.
                                    toToken [str]: Symbol for the token user is selling.
                                    fromAmount [float/bool]: Amount of token user is buying.
                                                                 If toAmount is specified it is None.
                                    toAmount [float/int/bool]: Amount of token user is selling.
                                                               If fromAmount is specified it is None.

        Returns:
            dict: Processed user request containing amount user wants to buy/sell, price and aggregators with specified
                  percentages to get the best price. Formatted the following way:
                      from_token [str]: Symbol for the token user is buying.
                      to_token [str]: Symbol for the token user is selling.
                      from_amount [float]: Amount of token user is buying.
                      to_amount [float]: Amount of token user is selling.
                      rate [float]: Price between tokens (to_token / from_token).
                      exchanges [dict]: What percentage of token amount should be swapped at which exchange.
                                        key: Name of the exchange.
                                        value: Percentage.
                      aggregator [str]: Name of the aggregator offering this price - 'paraswap'.
    """
    'GET TOKEN INFO'
    url = config.URLS['aggregators']['paraswap']['tokens']
    tokens = api_call(url)['tokens']  # Get all tokens paraswap can offer
    # Search through list of token data until from-token and to-token are found
    count = 0
    for token_data in tokens:
        if count == 2:
            break
        elif token_data['symbol'].upper() == user_params['fromToken'].upper():
            from_address = token_data['address']
            from_decimals = token_data['decimals']
            count += 1
        elif token_data['symbol'].upper() == user_params['toToken'].upper():
            to_address = token_data['address']
            to_decimals = token_data['decimals']
            count += 1
    else:
        raise DataError("<b>Token not found</b>\nPlease try another symbol")

    # 'PREPARE FOR REQUEST CALL'
    amount = user_params['fromAmount'] * 10**from_decimals

    # 'REQUEST CALL'
    url = f"{config.URLS['aggregators']['paraswap']['offer']}/{from_address}/{to_address}/{amount}"
    response = api_call(url)

    # 'FORMAT IT'
    result_amount = int(response['priceRoute']['amount']) * 10**-to_decimals
    rate = result_amount / user_params['fromAmount']
    exchanges = dict([(platform['exchange'], platform['percent']) for platform in response['priceRoute']['bestRoute']])
    # This is a general format that is passed to the formatting function.
    data = {'from_token': user_params['fromToken'],
            'to_token': user_params['toToken'],
            'from_amount': user_params['fromAmount'],
            'to_amount': result_amount,
            'rate': rate,
            'exchanges': exchanges,
            'aggregator': 'paraswap'
            }

    return data


def get_0x_offer(user_params):
    """Return dexag offer for the best price based on a user order.

    Args:
        user_params [dict]: User request, formatted the following way:
                                fromToken [str]: Symbol for the token user is buying.
                                toToken [str]: Symbol for the token user is selling.
                                fromAmount [float/bool]: Amount of token user is buying.
                                                             If toAmount is specified it is None.
                                toAmount [float/int/bool]: Amount of token user is selling.
                                                           If fromAmount is specified it is None.

    Returns:
        dict: Processed user request containing amount user wants to buy/sell, price and aggregators with specified
              percentages to get the best price. Formatted the following way:
                  from_token [str]: Symbol for the token user is buying.
                  to_token [str]: Symbol for the token user is selling.
                  from_amount [float]: Amount of token user is buying.
                  to_amount [float]: Amount of token user is selling.
                  rate [float]: Price between tokens (to_token / from_token).
                  exchanges [dict]: What percentage of token amount should be swapped at which exchange.
                                    key: Name of the exchange.
                                    value: Percentage.
                  aggregator [str]: Name of the aggregator offering this price - '0x'.
    """
    # 'GET TOKEN INFO'
    url = config.URLS['aggregators']['zerox']['tokens']
    tokens = api_call(url)['records']
    # Search through list of token data until from-token and to-token are found
    count = 0
    for token_data in tokens:
        if count == 2:
            break
        elif token_data['symbol'].upper() == user_params['fromToken'].upper():
            from_address = token_data['address']
            from_decimals = token_data['decimals']
            count += 1
        elif token_data['symbol'].upper() == user_params['toToken'].upper():
            to_address = token_data['address']
            to_decimals = token_data['decimals']
            count += 1
    else:
        raise DataError("<b>Token not found</b>\nPlease try another symbol")
                  
    # 'PREPARE FOR REQUEST CALL'
    api_params = {'buyToken': user_params['fromToken'],
                  'sellToken': user_params['toToken'],
                  }
    selling = user_params['fromAmount']
    if selling:
        api_params.update({'buyAmount': int(user_params['fromAmount'] * 10**from_decimals)})
    else:
        api_params.update({'sellAmount': int(user_params['toAmount'] * 10**to_decimals)})

    # 'REQUEST CALL'
    url = config.URLS['aggregators']['zerox']['offer']
    response = api_call(url, api_params)
    # TODO - error code?

    # 'FORMAT IT'
    relative_rate = float(response['price'])
    if selling:
        from_amount = user_params['fromAmount']
        to_amount = user_params['fromAmount'] * relative_rate
        rate = relative_rate
    else:
        from_amount = user_params['toAmount'] * relative_rate
        to_amount = user_params['toAmount']
        rate = 1/relative_rate
    exchanges = dict([(platform['name'], float(platform['proportion'])*100)for platform in response['sources']])
    # This is a general format that is passed to the formatting function.
    data = {'from_token': user_params['fromToken'],
            'to_token': user_params['toToken'],
            'from_amount': from_amount,
            'to_amount': to_amount,
            'rate': rate,
            'exchanges': exchanges,
            'aggregator': '0x'
            }

    return data
