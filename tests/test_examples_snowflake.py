import logging
import os

import pytest
from dotenv import load_dotenv

from datacontract.data_contract import DataContract

logging.basicConfig(level=logging.INFO, force=True)

datacontract = "examples/snowflake/datacontract.yaml"


@pytest.mark.skipif(os.environ.get("DATACONTRACT_SNOWFLAKE_USERNAME") is None, reason="Requires DATACONTRACT_SNOWFLAKE_USERNAME to be set")
def test_examples_snowflake():
    load_dotenv(override=True)
    # os.environ['DATACONTRACT_SNOWFLAKE_USERNAME'] = "xxx"
    # os.environ['DATACONTRACT_SNOWFLAKE_PASSWORD'] = "xxx"
    # os.environ['DATACONTRACT_SNOWFLAKE_ROLE'] = "xxx"
    # os.environ['DATACONTRACT_SNOWFLAKE_WAREHOUSE'] = "COMPUTE_WH"
    data_contract = DataContract(data_contract_file=datacontract)

    run = data_contract.test()

    print(run)
    assert run.result == "passed"
    assert all(check.result == "passed" for check in run.checks)
