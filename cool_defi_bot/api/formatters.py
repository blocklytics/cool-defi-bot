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
# NOTE This is the previous version - non-pythonic
#     platform_emoji = config.EMOJIS['platforms']
#     days7 = annualized_returns.get('D7_net_annualized')
#     days30 = annualized_returns.get('D30_net_annualized')
#     days90 = annualized_returns.get('D90_net_annualized')
#     platform = token_data.get('platform', '')
#     baseSymbol = str(token_data.get('baseSymbol', 'ETH'))
#     tokenSymbol = str(token_data.get('tokenSymbol', '???'))
#
#     header = f"<b>{platform_emoji[platform.lower()]} {baseSymbol}-{tokenSymbol} {platform.capitalize()} Pool</b>"
#     formatted_response = f"""
# {header}
# Liquidity: <b>${to_metric_prefix(token_data['usdLiquidity'])}</b>
# Volume (24h): <b>{'$' + to_metric_prefix(token_data['usdVolume']) if (token_data['usdVolume'] or token_data['usdVolume'] == 0) else 'n/a'}</b>
# Price: <b>${to_metric_prefix(token_data['usdPrice'])}</b>
#
# Annualized returns in ETH, if you joined:
#   • 7 days ago: <b>{str(round(days7, 1)) + '%' if (days7 or days7 == 0) else 'n/a'} {to_emoji(days7)}</b>
#   • 30 days ago: <b>{str(round(days30, 1)) + '%' if (days30 or days30 == 0) else 'n/a'} {to_emoji(days30)}</b>
#   • 90 days ago: <b>{str(round(days90, 1)) + '%' if (days90 or days90 == 0) else 'n/a'} {to_emoji(days90)}</b>
# """

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
    formatted_response = f"""
{header}
Liquidity: <b>${to_metric_prefix(token_data['usdLiquidity'])}</b>
Volume (24h): <b>{'$' + to_metric_prefix(token_data['usdVolume']) if token_data['usdVolume'] is not None else 'n/a'}</b>
Price: <b>${to_metric_prefix(token_data['usdPrice'])}</b>

Annualized returns in ETH, if you joined:
{fomatted_returns}
"""
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
    # TODO - Combine TKN & PLATFORM to make POOL
    baseTokens = [row['baseSymbol'] for row in data]
    # TODO - include baseToken in pool column
    # {platform} {baseToken}-{token} Pool

    headers = ['TKN', 'PLATFORM', 'LIQ']
    tokens = [row.get('tokenSymbol', row['tokenName']) for row in data]  # If there is no symbol that token's name
    platforms = [row['platform'] for row in data]
    liquidities = [to_metric_prefix(row['usdLiquidity']) for row in data]
    # Column width is equal to the width of the longest string in it (including headers)
    max_tkn_len = max([len(token) for token in tokens] + [len(headers[0])])
    max_plat_len = max([len(platform) for platform in platforms] + [len(headers[1])])
    max_liq_len = max([len(liquidity) for liquidity in liquidities] + [len(headers[2])])

    deepest_table = []
    for i in range(len(data)):
        # Data
        num = i + 1  # Row number
        tkn = tokens[i]
        plat = platforms[i].capitalize()
        liq = liquidities[i]
        # Space
        num_space = (len(str(len(data))) - len(str(num))) * ' '
        plat_space = (max_plat_len - len(plat))*' '
        tkn_space = (max_tkn_len - len(tkn))*' '
        liq_space = (max_liq_len - len(str(liq)))*' '

        output_row = f"{num}{num_space} {tkn}{tkn_space} {plat}{plat_space} {liq_space}${liq}"
        deepest_table.append(output_row)

    deepest_table_str = "\n".join(deepest_table)
    # All columns except for the last one are left-aligned, last on is right-aligned
    column_names = f"#{(len(str(len(data))) - len('#'))*' '} " \
                   f"{headers[0]} {(max_tkn_len - len(headers[0]))*' '} " \
                   f"{headers[1]} {(max_plat_len - len(headers[1]) + 1)*' '} " \
                   f"{(max_liq_len - len(headers[2]))*' '}{headers[2]}\n"
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
    msg = f"""
<b>{emojis.get(aggregator, '')} {aggregator.capitalize()} price</b>
Send: <b>{round_sig(data['from_amount'])} {data['from_token']}</b>
Receive: <b>{round_sig(data['to_amount'])} {data['to_token']}</b>
Rate: <b>{round_sig(data['rate'])} {data['to_token']}/{data['from_token']}</b>

Trade routing
{platform_perc}
"""
    return msg
