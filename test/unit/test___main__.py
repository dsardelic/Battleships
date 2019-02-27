import unittest.mock

import battleships.__main__
import params


class TestMain(unittest.TestCase):
    @unittest.mock.patch.object(battleships.__main__, "__name__", "__main__")
    @unittest.mock.patch("battleships.__main__.puzzle")
    def test_run(self, mock_puzzle):
        battleships.__main__.run()
        mock_puzzle.Puzzle.run.assert_called_once()

        mock_puzzle.reset_mock()
        mock_puzzle.Puzzle.run.side_effect = Exception
        with unittest.mock.patch("battleships.__main__.sys") as mock_sys:
            battleships.__main__.run()
            mock_puzzle.Puzzle.run.assert_called_once()
            mock_sys.exit.assert_called_once_with(params.FAILURE_EXIT_CODE)
