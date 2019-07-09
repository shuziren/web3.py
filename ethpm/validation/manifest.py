import json
from typing import Any, Dict, List, Set

from jsonschema import ValidationError as jsonValidationError, validate

from ethpm import SPEC_DIR, V2_PACKAGES_DIR
from ethpm.exceptions import ValidationError

MANIFEST_SCHEMA_PATH = SPEC_DIR / "package.spec.json"

META_FIELDS = {
    "license": str,
    "authors": list,
    "description": str,
    "keywords": list,
    "links": dict,
}


def validate_meta_object(meta: Dict[str, Any], allow_extra_meta_fields: bool) -> None:
    """
    Validates that every key is one of `META_FIELDS` and has a value of the expected type.
    """
    for key, value in meta.items():
        if key in META_FIELDS:
            if type(value) is not META_FIELDS[key]:
                raise ValidationError(
                    f"Values for {key} are expected to have the type {META_FIELDS[key]}, "
                    f"instead got {type(value)}."
                )
        elif allow_extra_meta_fields:
            if key[:2] != "x-":
                raise ValidationError(
                    "Undefined meta fields need to begin with 'x-', "
                    f"{key} is not a valid undefined meta field."
                )
        else:
            raise ValidationError(
                f"{key} is not a permitted meta field. To allow undefined fields, "
                "set `allow_extra_meta_fields` to True."
            )


def _load_schema_data() -> Dict[str, Any]:
    with open(MANIFEST_SCHEMA_PATH) as schema:
        return json.load(schema)


def extract_contract_types_from_deployments(deployment_data: List[Any]) -> Set[str]:
    contract_types = set(
        deployment["contract_type"]
        for chain_deployments in deployment_data
        for deployment in chain_deployments.values()
    )
    return contract_types


def validate_manifest_against_schema(manifest: Dict[str, Any]) -> None:
    """
    Load and validate manifest against schema
    located at MANIFEST_SCHEMA_PATH.
    """
    schema_data = _load_schema_data()
    try:
        validate(manifest, schema_data)
    except jsonValidationError as e:
        raise ValidationError(
            f"Manifest invalid for schema version {schema_data['version']}. "
            f"Reason: {e.message}"
        )


def check_for_deployments(manifest: Dict[str, Any]) -> bool:
    if "deployments" not in manifest or not manifest["deployments"]:
        return False
    return True


def validate_build_dependencies_are_present(manifest: Dict[str, Any]) -> None:
    if "build_dependencies" not in manifest:
        raise ValidationError("Manifest doesn't have any build dependencies.")

    if not manifest["build_dependencies"]:
        raise ValidationError("Manifest's build dependencies key is empty.")


def validate_manifest_deployments(manifest: Dict[str, Any]) -> None:
    """
    Validate that a manifest's deployments contracts reference existing contract_types.
    """
    if set(("contract_types", "deployments")).issubset(manifest):
        all_contract_types = list(manifest["contract_types"].keys())
        all_deployments = list(manifest["deployments"].values())
        all_deployment_names = extract_contract_types_from_deployments(all_deployments)
        missing_contract_types = set(all_deployment_names).difference(
            all_contract_types
        )
        if missing_contract_types:
            raise ValidationError(
                f"Manifest missing references to contracts: {missing_contract_types}."
            )


def validate_manifest_exists(manifest_id: str) -> None:
    """
    Validate that manifest with manifest_id exists in V2_PACKAGES_DIR
    """
    if not (V2_PACKAGES_DIR / manifest_id).is_file():
        raise ValidationError(
            f"Manifest not found in V2_PACKAGES_DIR with id: {manifest_id}"
        )


def validate_raw_manifest_format(raw_manifest: str) -> None:
    """
    Raise a ValidationError if a manifest ...
    - is not tightly packed (i.e. no linebreaks or extra whitespace)
    - does not have alphabetically sorted keys
    - has duplicate keys
    - is not UTF-8 encoded
    - has a trailing newline
    """
    try:
        manifest_dict = json.loads(raw_manifest, encoding="UTF-8")
    except json.JSONDecodeError as err:
        raise json.JSONDecodeError(
            "Failed to load package data. File is not a valid JSON document.",
            err.doc,
            err.pos,
        )
    compact_manifest = json.dumps(manifest_dict, sort_keys=True, separators=(",", ":"))
    if raw_manifest != compact_manifest:
        raise ValidationError(
            "The manifest appears to be malformed. Please ensure that it conforms to the "
            "EthPM-Spec for document format. "
            "http://ethpm.github.io/ethpm-spec/package-spec.html#document-format "
        )
