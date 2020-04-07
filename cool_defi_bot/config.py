EMOJIS = {
    'platforms': {
        'uniswap': '🦄',
        'bancor': '☝'
    },
    'aggregators': {
        'oneinch': '🏴‍☠',
        'dexag': '🍇',
        'paraswap': '🔷',
        '0x': '⚫'
    }
}

COMMANDS = ['/pools',
            '/deepest',
            '/start',
            '/help',
            '/feedback',
            '/1inch',
            '/dexag',
            '/paraswap',
            '/0x'
            ]

URLS = {
    'pools_exchanges': 'https://api.blocklytics.org/pools/v0/exchanges',
    'annualized_returns': 'http://api.blocklytics.org/uniswap/v1/returns',
    'deepest': 'https://api.blocklytics.org/pools/v0/exchanges',
    'analytics': 'https://www.google-analytics.com/collect',
    'slack_api': 'https://slack.com/api/chat.postMessage',
    'pools_token_site': 'https://pools.fyi/#/returns',
    'pools_site': 'https://pools.fyi',
    'aggregators': {
        'oneinch': {
            'offer': 'https://api.1inch.exchange/v1.1/quote',
            'tokens': 'https://api.1inch.exchange/v1.1/tokens',
            'site': 'https://1inch.exchange'
        },
        'dexag': {
            'offer': 'https://api-v2.dex.ag/price',
            'site': 'https://dex.ag'
        },
        'paraswap': {
            'offer': 'https://paraswap.io/api/v1/prices/networkID',
            'tokens': 'https://paraswap.io/api/v1/tokens/networkID',
            'site': 'https://paraswap.io'
        },
        'zerox': {
            'offer': 'https://api.0x.org/swap/v0/quote',
            'tokens': 'https://api.0x.org/swap/v0/tokens',
            'site': 'https://0x.org'
        }
    }
}

AGGREGATOR_PREFERENCES = {
    'oneinch': {
        'two_way': False,
        'default_token': 'ETH'
    },
    'paraswap': {
        'two_way': False,
        'default_token': 'ETH'
    },
    'dexag': {
        'two_way': True,
        'default_token': 'ETH'
    },
    'zerox': {
        'two_way': True,
        'default_token': 'WETH'
    }
}
