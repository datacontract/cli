from typer.testing import CliRunner
from datacontract.export.avro_idl_converter import model_to_avro_idl_ir,\
    AvroPrimitiveType, AvroFieldType, AvroModelType,\
    AvroIDLProtocol, to_avro_idl
from datacontract.lint.resolve import resolve_data_contract_from_location
from datacontract.cli import app
from textwrap import dedent

def test_ir():
    contract = resolve_data_contract_from_location("examples/lint/valid_datacontract_references.yaml",
                                                   inline_definitions=True)
    expected = AvroIDLProtocol(
        name="OrdersLatest",
        description="Successful customer orders in the webshop.\n"
        "All orders since 2020-01-01.\n"
        "Orders with their line items are in their current state (no history included).\n",
        model_types=[
            AvroModelType(
                "orders",
                "One record per order. Includes cancelled and deleted orders.",
                [AvroFieldType(
                    "order_id",
                    "An internal ID that identifies an order in the online shop.",
                    type=AvroPrimitiveType.string)]),
        ])
    assert model_to_avro_idl_ir(contract) == expected

def test_avro_idl_str():
    contract = resolve_data_contract_from_location("examples/lint/valid_datacontract_references.yaml",
                                                   inline_definitions=True)
    expected = dedent(
        """
          /** Successful customer orders in the webshop.
          All orders since 2020-01-01.
          Orders with their line items are in their current state (no history included).
           */
          protocol OrdersLatest {
              /** One record per order. Includes cancelled and deleted orders. */
              record orders {
                  /** An internal ID that identifies an order in the online shop. */
                  string order_id;
              }
          }
        """).strip()
    assert to_avro_idl(contract).strip() == expected

def test_avro_idl_cli_export():
    runner = CliRunner()
    result = runner.invoke(app, [
        "export",
        "./examples/lint/valid_datacontract_references.yaml",
        "--format", "avro-idl"
    ])
    if result.exit_code:
        print(result.output)
    assert result.exit_code == 0
