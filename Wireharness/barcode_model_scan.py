# barcode_model_scan.py

def sanitize_barcode_input(input_text, output_text):

    # Find the position of '$' and truncate the string if it exists
    if "$" in input_text:
        sanitized_text = input_text.split("$")[0]

    else:
        sanitized_text = input_text

    # Optionally assign sanitized text to the output variable
    if isinstance(output_text, list):
        output_text.clear()
        output_text.append(sanitized_text)

    return sanitized_text
