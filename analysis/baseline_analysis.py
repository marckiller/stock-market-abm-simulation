import argparse
import os
import random
import sys
import tempfile
import warnings

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', tempfile.gettempdir())
warnings.filterwarnings('ignore', category=FutureWarning)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.simulation.simulation import Simulation


def build_config(seed, max_time, scenario):
    rng = np.random.default_rng(seed)
    if scenario not in {'only_zi', 'mixed'}:
        raise ValueError(f'Unknown scenario: {scenario}')
    agents = []
    agent_id = 1
    for _ in range(60):
        agents.append({
            'id': agent_id,
            'type': 'zero_intelligence',
            'cash': 100000,
            'max_order_size': 1,
            'limit_order_rate': 0.92,
            'market_order_rate': 0.03,
            'cancellation_rate': 0.05,
            'activation_rate': rng.uniform(0.10, 0.24),
        })
        agent_id += 1
    for _ in range(10):
        agents.append({
            'id': agent_id,
            'type': 'zero_intelligence',
            'cash': 100000,
            'max_order_size': 1,
            'limit_order_rate': 0.30,
            'market_order_rate': 0.60,
            'cancellation_rate': 0.10,
            'activation_rate': rng.uniform(0.03, 0.08),
        })
        agent_id += 1
    if scenario == 'mixed':
        for window in [10, 20, 50, 100]:
            agents.append({
                'id': agent_id,
                'type': 'chartist',
                'cash': 100000,
                'activation_rate': rng.uniform(0.02, 0.06),
                'max_order_size': 1,
                'window': window,
                'threshold': 0.05,
            })
            agent_id += 1
        fundamentalist_groups = [
            {'center': 99.7, 'std': 0.25, 'count': 15},
            {'center': 100.0, 'std': 0.20, 'count': 20},
            {'center': 100.3, 'std': 0.25, 'count': 15},
        ]
        for group in fundamentalist_groups:
            for _ in range(group['count']):
                agents.append({
                    'id': agent_id,
                    'type': 'fundamentalist',
                    'cash': 100000,
                    'fundamental_value': rng.normal(group['center'], group['std']),
                    'activation_rate': rng.uniform(0.03, 0.10),
                    'max_order_size': 1,
                })
                agent_id += 1
    return {
        'market': {
            'ohlcv_periods': [1000],
            'store_tick_data': False,
            'max_ticks': 1000,
        },
        'agents': agents,
        'time_step': 1,
        'max_time': max_time,

    }


def extract_transaction_prices(events, burn_in):
    rows = []
    for event in events:
        if event['event_type'] != 'transaction':
            continue
        if event['timestamp'] < burn_in:
            continue
        rows.append({
            'sequence': event['sequence'],
            'time': event['timestamp'],
            'price': event['price'],
            'quantity': event['quantity'],
            'buyer_id': event['buyer_id'],
            'seller_id': event['seller_id'],
        })
    return pd.DataFrame(rows)


def add_returns(price_path):
    price_path = price_path.copy()
    price_path['log_price'] = np.log(price_path['price'])
    price_path['log_return'] = price_path['log_price'].diff()
    return price_path


def build_return_price_path(transaction_prices, interval):
    if interval <= 1:
        return transaction_prices.copy()

    price_path = transaction_prices.copy()
    price_path['bar'] = price_path['time'] // interval
    return (
        price_path
        .groupby('bar', as_index=False)
        .agg({
            'sequence': 'last',
            'time': 'last',
            'price': 'last',
            'quantity': 'sum',
            'buyer_id': 'last',
            'seller_id': 'last',
        })
        .drop(columns=['bar'])
    )


def build_price_plot_path(transaction_prices, interval):
    if interval <= 1:
        return transaction_prices.copy()

    price_path = transaction_prices.copy()
    price_path['bar'] = price_path['time'] // interval
    price_path['price_volume'] = price_path['price'] * price_path['quantity']
    grouped = (
        price_path
        .groupby('bar', as_index=False)
        .agg({
            'sequence': 'last',
            'time': 'last',
            'price_volume': 'sum',
            'quantity': 'sum',
            'buyer_id': 'last',
            'seller_id': 'last',
        })
    )
    grouped['price'] = grouped['price_volume'] / grouped['quantity']
    return grouped.drop(columns=['bar', 'price_volume'])


def autocorrelation(values, max_lag):
    series = pd.Series(values).dropna()
    rows = []
    for lag in range(1, max_lag + 1):
        rows.append({'lag': lag, 'autocorrelation': series.autocorr(lag)})
    return pd.DataFrame(rows)


def compute_summary(price_path):
    returns = price_path['log_return'].dropna()
    if returns.empty:
        return {
            'num_price_observations': len(price_path),
            'num_returns': 0,
            'mean_return': np.nan,
            'std_return': np.nan,
            'return_autocorr_lag_1': np.nan,
            'abs_return_autocorr_lag_1': np.nan,
            'excess_kurtosis': np.nan,
            'tail_ratio_3_sigma': np.nan,
        }

    std_return = returns.std(ddof=1)
    z_returns = (returns - returns.mean()) / std_return if std_return > 0 else returns * np.nan
    empirical_tail = (z_returns.abs() > 3).mean()
    normal_tail = 2 * (1 - stats.norm.cdf(3))

    return {
        'num_price_observations': len(price_path),
        'num_returns': len(returns),
        'mean_return': returns.mean(),
        'std_return': std_return,
        'return_autocorr_lag_1': returns.autocorr(1),
        'abs_return_autocorr_lag_1': returns.abs().autocorr(1),
        'excess_kurtosis': stats.kurtosis(returns, fisher=True, bias=False),
        'tail_ratio_3_sigma': empirical_tail / normal_tail if normal_tail > 0 else np.nan,
    }


def write_summary(summary, path):
    with open(path, 'w') as file:
        for key, value in summary.items():
            file.write(f'{key}: {value}\n')


def plot_price_path(price_plot_path, output_dir):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        price_plot_path['time'],
        price_plot_path['price'],
        linewidth=1.0,
        color='#1f77b4',
        label='Interval VWAP',
    )

    rolling_price = price_plot_path['price'].rolling(window=12, min_periods=1).mean()
    ax.plot(
        price_plot_path['time'],
        rolling_price,
        linewidth=1.6,
        color='black',
        label='Rolling mean',
    )

    ax.set_title('Price Path')
    ax.set_xlabel('Simulation time')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'price_path.png'), dpi=150)
    plt.close(fig)


def plot_returns(price_path, output_dir):
    returns = price_path['log_return'].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(price_path.loc[returns.index, 'time'], returns, linewidth=0.9)
    ax.set_title('Log Returns')
    ax.set_xlabel('Simulation time')
    ax.set_ylabel('Log return')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'log_returns.png'), dpi=150)
    plt.close(fig)


def plot_return_distribution(price_path, output_dir):
    returns = price_path['log_return'].dropna()
    if returns.empty:
        return

    mean = returns.mean()
    std = returns.std(ddof=1)
    if std <= 0:
        return

    absolute_standardized_returns = np.sort(np.abs((returns - mean) / std))
    ccdf = 1.0 - np.arange(1, len(absolute_standardized_returns) + 1) / len(absolute_standardized_returns)
    normal_ccdf = 2 * (1 - stats.norm.cdf(absolute_standardized_returns))

    positive = ccdf > 0

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        absolute_standardized_returns[positive],
        ccdf[positive],
        linewidth=1.5,
        label='Simulated returns'
    )
    ax.plot(
        absolute_standardized_returns[positive],
        normal_ccdf[positive],
        linewidth=1.5,
        label='Normal reference'
    )

    ax.set_yscale('log')
    ax.set_title('Log Return Tail CCDF')
    ax.set_xlabel('|standardized log return|')
    ax.set_ylabel('P(|R| > x)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'return_distribution.png'), dpi=150)
    plt.close(fig)


def plot_abs_return_autocorrelation(price_path, output_dir, max_lag):
    returns = price_path['log_return'].dropna().abs()
    autocorr = autocorrelation(returns, max_lag=max_lag)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(autocorr['lag'], autocorr['autocorrelation'], width=0.8)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_title('Absolute Return Autocorrelation')
    ax.set_xlabel('Lag')
    ax.set_ylabel('Autocorrelation')
    ax.grid(True, axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'abs_return_autocorrelation.png'), dpi=150)
    plt.close(fig)

    return autocorr


def run_analysis(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    simulation = Simulation(build_config(args.seed, args.max_time, args.scenario))
    simulation.run()

    events = simulation.market.get_event_log()
    price_path = extract_transaction_prices(events, args.burn_in)
    if price_path.empty:
        raise RuntimeError('No transactions were generated; cannot analyze a price path.')

    transaction_prices = add_returns(price_path)
    return_price_path = add_returns(build_return_price_path(price_path, args.return_interval))
    price_plot_path = build_price_plot_path(price_path, args.price_interval)
    summary = compute_summary(return_price_path)
    autocorr = plot_abs_return_autocorrelation(return_price_path, args.output_dir, args.max_lag)

    transaction_prices.to_csv(os.path.join(args.output_dir, 'transaction_price_path.csv'), index=False)
    return_price_path.to_csv(os.path.join(args.output_dir, 'return_price_path.csv'), index=False)
    price_plot_path.to_csv(os.path.join(args.output_dir, 'price_plot_path.csv'), index=False)
    autocorr.to_csv(os.path.join(args.output_dir, 'abs_return_autocorrelation.csv'), index=False)
    write_summary(summary, os.path.join(args.output_dir, 'summary.txt'))
    simulation.market.event_logger.to_jsonl(os.path.join(args.output_dir, 'events.jsonl'))

    plot_price_path(price_plot_path, args.output_dir)
    plot_returns(return_price_path, args.output_dir)
    plot_return_distribution(return_price_path, args.output_dir)

    print(f'events: {len(events)}')
    print(f'scenario: {args.scenario}')
    print(f'burn_in: {args.burn_in}')
    print(f'transactions: {len(transaction_prices)}')
    print(f'return_interval: {args.return_interval}')
    print(f'price_interval: {args.price_interval}')
    print(f'return_observations: {len(return_price_path)}')
    print(f'output_dir: {args.output_dir}')
    print(f'excess_kurtosis: {summary["excess_kurtosis"]}')
    print(f'abs_return_autocorr_lag_1: {summary["abs_return_autocorr_lag_1"]}')
    print(f'tail_ratio_3_sigma: {summary["tail_ratio_3_sigma"]}')


def parse_args():
    parser = argparse.ArgumentParser(description='Run baseline analysis from logged market events.')
    parser.add_argument('--scenario', choices=['only_zi', 'mixed'], default='mixed')
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--max-time', type=int, default=50000)
    parser.add_argument('--burn-in', type=int, default=1000)
    parser.add_argument('--return-interval', type=int, default=10)
    parser.add_argument('--price-interval', type=int, default=100)
    parser.add_argument('--max-lag', type=int, default=50)
    parser.add_argument('--output-dir', default=os.path.join('analysis', 'output'))
    return parser.parse_args()


if __name__ == '__main__':
    run_analysis(parse_args())
