"""Reject skips and unrelated failures when comparing baseline and fixed SQL drivers."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
TEST_NAME = "Utf8ParameterTests.VarCharUtf8ByteBoundaryRoundTrip"
ERROR = "Data type 0xA7 has an invalid data length or metadata length"


def verify(path, expectation, exit_code):
    """Check real TRX results so setup/build errors cannot masquerade as reproduction."""
    tree = ET.parse(path)
    results = tree.findall(".//t:UnitTestResult", NS)
    if len(results) != 6 or any(TEST_NAME not in result.get("testName", "") for result in results):
        raise ValueError("Expected exactly the six UTF-8 database cases; missing, skipped or unexpected tests are a failure.")
    outcomes = [result.get("outcome") for result in results]
    if expectation == "fixed":
        if exit_code != 0 or outcomes != ["Passed"] * 6:
            raise ValueError("The fixed driver must pass all six cases with no skips or runner errors.")
        return "PASS: fixed driver passed all six real SQL Server round-trip cases."
    if exit_code != 1 or outcomes != ["Failed"] * 6:
        raise ValueError("The baseline must fail all six cases with the expected test-failure exit code.")
    for result in results:
        message = result.findtext("t:Output/t:ErrorInfo/t:Message", default="", namespaces=NS)
        if "SqlException" not in message or ERROR not in message:
            raise ValueError("A baseline failure was not the expected SQL Server TDS metadata error.")
    return "PASS: unpatched driver reproduced the SQL Server TDS metadata error in all six cases (expected failures)."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trx", type=Path, required=True)
    parser.add_argument("--expect", choices=("baseline", "fixed"), required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()
    try:
        print(verify(args.trx, args.expect, args.exit_code))
    except (OSError, ET.ParseError, ValueError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
