"""
Functions that format the final bot response text.
Miha Lotric, Dec 2019
"""
from cool_defi_bot.api.helpers import to_emoji, to_metric_prefix, round_sig
import cool_defi_bot.config as config


def format_annualized_returns(token_data, annualized_returns):
    """Return formatted pools data.
    Args:
        token_data [dict]: Pool data for a token. That data is 'base', 'baseLiquidity', 'baseName', 'basePrice',
                           'baseSymbol', 'baseVolume', 'exchange', 'factory', 'ownershipToken', 'platform', 'timestamp',
                           'token', 'tokenLiquidity', 'tokenName', 'tokenSymbol', 'tokenVolume', 'usdLiquidity',
                           'usdPrice', 'usdVolume'.
        annualized_returns [dict]: Token annualized returns.
    Returns:
        str: HTML-formatted response.
    """
    platform_emoji = config.EMOJIS['platforms']
    platform = token_data.get('platform', '')
    base_symbol = str(token_data.get('baseSymbol', 'ETH'))
    token_symbol = str(token_data.get('tokenSymbol', '???'))
    possible_days = ('7', '30', '90')
    bydays = dict([(day, annualized_returns.get(f'D{day}_net_annualized')) for day in possible_days])

    header = f"<b>{platform_emoji[platform.lower()]} {base_symbol}-{token_symbol} {platform.capitalize()} Pool</b>"
    fomatted_returns = '\n'.join([f"\t• {d} days ago: <b>"
                                  f"{str(round(bydays[d], 1)) + '%' if bydays[d] is not None else 'n/a'} "
                                  f"{to_emoji(bydays[d])}</b>"
                                  for d in possible_days])

    volume = '$' + to_metric_prefix(token_data['usdVolume']) if token_data['usdVolume'] is not None else 'n/a'
    formatted_response = f"{header}\n" \
                         f"Liquidity: <b>${to_metric_prefix(token_data['usdLiquidity'])}</b>\n" \
                         f"Volume (24h): <b>{volume}</b>\n" \
                         f"Price: <b>${to_metric_prefix(token_data['usdPrice'])}</b>\n\n" \
                         f"Annualized returns in ETH, if you joined:\n" \
                         f"{fomatted_returns}"

    return formatted_response


def format_deepest(data):
    """Return formatted deepest tokens by liquidity and their data
    Args:
        data [list]: Top tokens by liquidity with their data. That data being 'base', 'baseLiquidity', 'baseName',
                     'basePrice', 'baseSymbol', 'baseVolume', 'exchange', 'factory', 'ownershipToken', 'platform',
                     'timestamp', 'token', 'tokenLiquidity', 'tokenName', 'tokenSymbol', 'tokenVolume', 'usdLiquidity',
                     'usdPrice', 'usdVolume'.
    Returns:
        str: HTML-formatted response.
    """
    headers = ['#', 'POOL', 'LIQ']
    tokens = [row.get('tokenSymbol', row['tokenName']) for row in data]  # If there is no symbol that token's name
    base_tokens = [row['baseSymbol'] for row in data]
    platforms = [row['platform'] for row in data]
    pools = [f"{platforms[i].capitalize()} {base_tokens[i]}-{tokens[i]}" for i in range(len(data))]
    liquidities = [to_metric_prefix(row['usdLiquidity']) for row in data]
    # Column width is equal to the width of the longest string in it (including headers)
    max_pool_len = max([len(pool) for pool in pools] + [len(headers[1])])
    max_liq_len = max([len(liquidity) for liquidity in liquidities] + [len(headers[2])])

    deepest_table = []
    for i in range(len(data)):
        # Data
        num = i + 1  # Row number
        pool = pools[i]  # {platform} {base token}-{token}
        liq = liquidities[i]
        # Space
        num_space = (len(str(len(data))) - len(str(num))) * ' '
        pool_space = (max_pool_len - len(str(pool)))*' '
        liq_space = (max_liq_len - len(str(liq)))*' '

        output_row = f"{num}{num_space} {pool}{pool_space} {liq_space}${liq}"
        deepest_table.append(output_row)

    deepest_table_str = "\n".join(deepest_table)
    # All columns except for the last one are left-aligned, last on is right-aligned
    column_names = f"{headers[0]}{(len(str(len(data))) - len(headers[0]))*' '} " \
                   f"{headers[1]}{(max_pool_len - len(headers[1]))*' '} " \
                   f"{(max_liq_len - len(headers[2])+1)*' '}{headers[2]}\n"
    coated = "<code>" + column_names + deepest_table_str + "</code>"

    return coated


def format_offer(data):
    """Return formatted aggregator offer.
     Args:
        data [dict]: Aggregator offer.
    Returns:
        str: HTML-formatted response.
    """
    emojis = config.EMOJIS['aggregators']
    aggregator = data.get('aggregator', '')
    platform_perc = '\n'.join([('  • ' + str(int(perc)) + '%' + ' ' + platform.capitalize())
                               for platform, perc in data['exchanges'].items()])
    msg = f"<b>{emojis.get(aggregator, '')} {aggregator.capitalize()} price</b>\n" \
          f"Send: <b>{round_sig(data['from_amount'])} {data['from_token']}</b>\n" \
          f"Receive: <b>{round_sig(data['to_amount'])} {data['to_token']}</b>\n" \
          f"Rate: <b>{round_sig(data['rate'])} {data['to_token']}/{data['from_token']}</b>\n\n" \
          "Trade routing\n" \
          f"{platform_perc}"

    return msg
