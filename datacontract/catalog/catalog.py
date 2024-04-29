from dataclasses import dataclass

from jinja2 import PackageLoader, Environment, select_autoescape
import pytz
from datetime import datetime

from datacontract.export.html_export import get_version
from datacontract.data_contract import DataContract
from datacontract.model.data_contract_specification import DataContractSpecification


def create_data_contract_html(contracts, file, path):
    data_contract = DataContract(data_contract_file=f"{file.absolute()}", inline_definitions=True)
    html = data_contract.export(export_format="html")
    spec = data_contract.get_data_contract_specification()
    # html_filename = f"dc-{spec.id}-{spec.info.version}.html"
    file_without_suffix = file.name.removesuffix(".yaml").removesuffix(".yml")
    html_filename = f"{file_without_suffix}.html"
    html_filepath = path / html_filename
    with open(html_filepath, "w") as f:
        f.write(html)
    contracts.append(DataContractView(
        html_filepath=html_filepath,
        html_filename=html_filename,
        spec=spec,
    ))
    print(f"Created {html_filepath}")


@dataclass
class DataContractView:
    """Class for keeping track of an item in inventory."""
    html_filepath: str
    html_filename: str
    spec: DataContractSpecification


def create_index_html(contracts, path):
    index_filepath = path / "index.html"
    with open(index_filepath, "w") as f:
        # Load templates from templates folder
        package_loader = PackageLoader("datacontract", "templates")
        env = Environment(
            loader=package_loader,
            autoescape=select_autoescape(
                enabled_extensions="html",
                default_for_string=True,
            ),
        )

        # Load the required template
        template = env.get_template("index.html")

        style_content, _, _ = package_loader.get_source(env, "style/output.css")

        tz = pytz.timezone('UTC')
        now = datetime.now(tz)
        formatted_date = now.strftime('%d %b %Y %H:%M:%S UTC')
        datacontract_cli_version = get_version()

        # Render the template with necessary data
        html_string = template.render(
            style=style_content,
            formatted_date=formatted_date,
            datacontract_cli_version=datacontract_cli_version,
            contracts=contracts,
            contracts_size=len(contracts),
        )
        f.write(html_string)
    print(f"Created {index_filepath}")