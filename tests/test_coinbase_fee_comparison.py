from __future__ import annotations

import unittest

from scripts.run_coinbase_fee_comparison import annualized_return, buy_hold_net_return


class CoinbaseFeeComparisonTests(unittest.TestCase):
    def test_buy_hold_applies_fee_to_purchase_and_sale(self) -> None:
        net_return = buy_hold_net_return(gross_return=1.0, fee_rate=0.006)
        self.assertAlmostEqual(net_return, 2.0 * 0.994**2 - 1.0)

    def test_annualized_return_uses_crypto_calendar(self) -> None:
        self.assertAlmostEqual(annualized_return(total_return=1.0, observations=366), 1.0)


if __name__ == "__main__":
    unittest.main()
