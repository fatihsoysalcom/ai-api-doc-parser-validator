import re

# --- 1. Simulate the actual API definition (the "source of truth") ---
# In a real scenario, this would come from code annotations, OpenAPI spec, etc.
actual_api_definition = {
    "path": "/users/{id}",
    "method": "GET",
    "parameters": [
        {"name": "id", "type": "integer", "required": True},
        {"name": "token", "type": "string", "required": False}
    ],
    "responses": {
        200: {"description": "User details"},
        404: {"description": "User not found"}
    }
}

# --- 2. Simulate AI-generated documentation (as a simplified string) ---
# The AI would typically generate natural language, which a more complex parser
# would then convert. Here, we use a structured string for simplicity.
ai_generated_doc_correct = "API_DOC: GET /users/{id} PARAMS: id:integer:required token:string:optional"
ai_generated_doc_incorrect_method = "API_DOC: POST /users/{id} PARAMS: id:integer:required token:string:optional"
ai_generated_doc_incorrect_param_type = "API_DOC: GET /users/{id} PARAMS: id:string:required token:string:optional"
ai_generated_doc_incorrect_param_missing = "API_DOC: GET /users/{id} PARAMS: id:integer:required"


# --- 3. Implement a simple parser for the AI-generated documentation string ---
# This parser extracts structured data from the AI-generated string.
def parse_ai_doc(doc_string):
    """
    Parses a simplified AI-generated documentation string into a structured dictionary.
    Expected format: "API_DOC: METHOD PATH PARAMS: param1_name:type:required param2_name:type:optional"
    """
    match = re.match(r"API_DOC: (\w+) (\S+) PARAMS: (.*)", doc_string)
    if not match:
        return None

    method, path, params_str = match.groups()
    parsed_params = []
    if params_str:
        for param_entry in params_str.split():
            parts = param_entry.split(':')
            if len(parts) == 3:
                name, p_type, required_str = parts
                parsed_params.append({
                    "name": name,
                    "type": p_type,
                    "required": (required_str == "required")
                })
    return {
        "path": path,
        "method": method,
        "parameters": parsed_params
    }

# --- 4. Implement a validator to compare parsed doc with actual API definition ---
# This function performs the "reality check" mentioned in the article.
def validate_documentation(parsed_doc, actual_api):
    """
    Validates parsed AI-generated documentation against the actual API definition.
    Returns a list of errors found.
    """
    errors = []

    # Validate method
    if parsed_doc["method"] != actual_api["method"]:
        errors.append(f"Method mismatch: Doc says '{parsed_doc['method']}', Actual is '{actual_api['method']}'")

    # Validate path
    if parsed_doc["path"] != actual_api["path"]:
        errors.append(f"Path mismatch: Doc says '{parsed_doc['path']}', Actual is '{actual_api['path']}'")

    # Validate parameters
    actual_params_map = {p["name"]: p for p in actual_api["parameters"]}
    parsed_params_map = {p["name"]: p for p in parsed_doc["parameters"]}

    # Check for parameters present in actual API but missing in doc or with mismatches
    for param_name, actual_param in actual_params_map.items():
        if param_name not in parsed_params_map:
            errors.append(f"Parameter '{param_name}' missing in documentation.")
        else:
            parsed_param = parsed_params_map[param_name]
            if parsed_param["type"] != actual_param["type"]:
                errors.append(f"Parameter '{param_name}' type mismatch: Doc says '{parsed_param['type']}', Actual is '{actual_param['type']}'")
            if parsed_param["required"] != actual_param["required"]:
                errors.append(f"Parameter '{param_name}' required status mismatch: Doc says '{parsed_param['required']}', Actual is '{actual_param['required']}'")

    # Check for parameters present in doc but not in actual API (extra params)
    for param_name in parsed_params_map:
        if param_name not in actual_params_map:
            errors.append(f"Extra parameter '{param_name}' found in documentation, not in actual API.")

    return errors

# --- 5. Demonstrate the process with various test cases ---
print("--- Actual API Definition (Source of Truth) ---")
print(actual_api_definition)
print("\n" + "="*60 + "\n")

def run_test_case(description, ai_doc_string):
    print(f"--- Testing: {description} ---")
    print(f"AI Doc String: {ai_doc_string}")
    parsed_doc = parse_ai_doc(ai_doc_string)
    if parsed_doc:
        print(f"Parsed Doc: {parsed_doc}")
        validation_errors = validate_documentation(parsed_doc, actual_api_definition)
        if not validation_errors:
            print("Validation Result: SUCCESS! Documentation matches actual API.")
        else:
            print("Validation Result: FAILED!")
            for error in validation_errors:
                print(f"- {error}")
    else:
        print("Parsing failed for AI-generated documentation.")
    print("\n" + "="*60 + "\n")

run_test_case("Correct AI-Generated Documentation", ai_generated_doc_correct)
run_test_case("AI-Generated Documentation with Incorrect Method", ai_generated_doc_incorrect_method)
run_test_case("AI-Generated Documentation with Incorrect Parameter Type", ai_generated_doc_incorrect_param_type)
run_test_case("AI-Generated Documentation with Missing Required Parameter", ai_generated_doc_incorrect_param_missing)
