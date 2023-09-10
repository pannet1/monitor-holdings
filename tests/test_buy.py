import sys

# add the directory of the import file
curr_path = "/home/pannet1/Programs/py/holdings/monitor-holdings/monitor_holdings/"
sys.path.append(curr_path)

if True:
    # just to avoid import to be moved to the top by code formatters
    from buy import calc_target


def test_calc_target():
    ltp = 100  # Replace with a suitable ltp value
    perc = 2  # Replace with a suitable percentage value
    target = calc_target(ltp, perc)
    assert target >= ltp, f"Target ({target}) is not higher than ltp ({ltp})"
