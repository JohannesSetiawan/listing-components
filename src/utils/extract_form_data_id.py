import json

def extract_form_data_ids(obj, form_data_ids=None):
    """
    Recursively extract all form_data_id values from a nested JSON structure.
    
    Args:
        obj: The object to search (dict, list, or primitive)
        form_data_ids: Set to store unique form_data_id values
    
    Returns:
        Set of unique form_data_id values
    """
    if form_data_ids is None:
        form_data_ids = set()
    
    if isinstance(obj, dict):
        # Check if current dict has form_data_id key
        if 'form_data_id' in obj:
            value = obj['form_data_id']
            # Only add non-empty strings
            if value and isinstance(value, str) and value.strip():
                form_data_ids.add(value)
        
        # Recursively check all values in the dictionary
        for value in obj.values():
            extract_form_data_ids(value, form_data_ids)
    
    elif isinstance(obj, list):
        # Recursively check all items in the list
        for item in obj:
            extract_form_data_ids(item, form_data_ids)
    
    return form_data_ids


def main():
    # Read the component.json file
    with open('component.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Read the indexed-data-managers.json file for id to tablegroup_id mapping
    with open('indexed-data-managers.json', 'r', encoding='utf-8') as f:
        id_to_tablegroup = json.load(f)
    
    # Extract unique form_data_id values
    form_data_ids = extract_form_data_ids(data)
    
    # Sort for consistent output
    sorted_ids = sorted(form_data_ids)
    
    # Print results with URLs
    print(f"Found {len(sorted_ids)} unique form_data_id values:\n")
    
    not_found = []
    for form_id in sorted_ids:
        if form_id in id_to_tablegroup:
            tablegroup_id = id_to_tablegroup[form_id]
            url = f"- https://studio-uat2.smart-cimb.com/#/form-data/table/{tablegroup_id}/{form_id} "
            print(url)
        else:
            not_found.append(form_id)
    
    # Print any IDs not found in the index
    if not_found:
        print(f"\n\nWarning: {len(not_found)} form_data_id(s) not found in indexed-data-managers.json:")
        for form_id in not_found:
            print(f"  - {form_id}")


if __name__ == "__main__":
    main()
