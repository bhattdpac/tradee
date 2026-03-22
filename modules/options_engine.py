# This module will contain the logic for the Options Intelligence Engine.
import pandas as pd

def find_option_walls(calls: pd.DataFrame, puts: pd.DataFrame, min_oi_threshold=100):
    """
    Finds the strike prices with the highest open interest (Put/Call Walls).

    :param calls: DataFrame containing call options data.
    :param puts: DataFrame containing put options data.
    :param min_oi_threshold: Minimum Open Interest to consider a strike.
    :return: A dictionary containing the call wall and put wall info, or None.
    """
    if calls.empty or puts.empty:
        return None

    # Filter out strikes with very low open interest to avoid noise
    calls_filtered = calls[calls['openInterest'] >= min_oi_threshold]
    puts_filtered = puts[puts['openInterest'] >= min_oi_threshold]

    if calls_filtered.empty or puts_filtered.empty:
        return None

    # Find the strike with the maximum open interest
    call_wall_strike = calls_filtered.loc[calls_filtered['openInterest'].idxmax()]
    put_wall_strike = puts_filtered.loc[puts_filtered['openInterest'].idxmax()]

    walls = {
        "call_wall": {
            "strike": call_wall_strike['strike'],
            "oi": int(call_wall_strike['openInterest'])
        },
        "put_wall": {
            "strike": put_wall_strike['strike'],
            "oi": int(put_wall_strike['openInterest'])
        }
    }

    return walls