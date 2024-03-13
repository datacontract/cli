import avro.schema

from datacontract.model.data_contract_specification import \
    DataContractSpecification, Model, Field


def import_avro(data_contract_specification: DataContractSpecification, source: str):

    if data_contract_specification.models is None:
        data_contract_specification.models = {}
    avro_schema = avro.schema.parse(open(source, "rb").read())

    # type record is being used for both the table and the object types in data contract
    # -> CONSTRAINT: one table per .avsc input, all nested records are interpreted as objects
    fields = import_record_fields(avro_schema.fields)

    data_contract_specification.models[avro_schema.name] = Model(
        type="table",
        fields=fields,
        description=avro_schema.doc,
    )

    return data_contract_specification


def import_record_fields(record_fields):

    imported_fields = {}
    for field in record_fields:
        if field.type.type == "record":
            imported_fields[field.name] = Field()
            imported_fields[field.name].type = "object"
            imported_fields[field.name].description = field.type.doc
            imported_fields[field.name].fields = import_record_fields(field.type.fields)
        else:
            imported_fields[field.name] = Field()
            imported_fields[field.name].type = map_type_from_avro(field.type.type)
            imported_fields[field.name].description = field.doc
    return imported_fields


def map_type_from_avro(avro_type_str: str):
    # TODO: ambiguous mapping in the export
    if avro_type_str is None:
        return None
    if avro_type_str == "null":
        return "null"
    elif avro_type_str == "string":
        return "string"
    elif avro_type_str == "bytes":
        return "binary"
    elif avro_type_str == "double":
        return "double"
    elif avro_type_str == "int":
        return "int"
    elif avro_type_str == "long":
        return "long"
    elif avro_type_str == "boolean":
        return "boolean"
    elif avro_type_str == "array":
        return "array"
    else:
        return "variant"
