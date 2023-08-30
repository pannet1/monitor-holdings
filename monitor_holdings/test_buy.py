# pytest
from toolkit.currency import round_to_paise


def calc_target(ltp, perc, maxim):
    resistance = round_to_paise(ltp, perc)
    target = round_to_paise(ltp, maxim)
    return max(resistance, target)


def test_calc_target_higher_than_ltp():
    ltp = 100  # Replace with a suitable ltp value
    perc = 2  # Replace with a suitable percentage value
    maxim = 1

    target = calc_target(ltp, perc, maxim)
    assert target >= ltp, f"Target ({target}) is not higher than ltp ({ltp})"
    assert maxim > perc, f"Maximum {maxim} is not hihger than perc {perc}"
