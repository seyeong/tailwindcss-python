import sys
from unittest import mock

import tailwind


@mock.patch("tailwind.call", return_value=0)
@mock.patch.object(sys, "argv", ["somebin", "build", "-h"])
def test_main(fake_call):
    exit_code = tailwind.main()
    assert exit_code == 0
    fake_call.assert_called_once_with([tailwind.TAILWIND_BIN, "build", "-h"])
