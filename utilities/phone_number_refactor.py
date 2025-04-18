def convert_to_standard_format(phone_number):
    # Remove any non-digit characters
    cleaned_number = ''.join(filter(str.isdigit, phone_number))

    # Check if the number starts with '0', and prepend '255' if necessary
    if cleaned_number.startswith('0'):
        cleaned_number = '255' + cleaned_number[1:]

    return cleaned_number


def determine_provider(phone_number):
    # Extract the prefix (first 5 digits) from the cleaned phone number
    cleaned_phone_number = convert_to_standard_format(phone_number)
    prefix = cleaned_phone_number[:5]
    print(prefix)
    if prefix in ["25571", "25565", "25567"]:
        return "Tigo"
    elif prefix in ["25574", "25575", "25576"]:
        return "Mpesa"
    elif prefix in ["25578", "25568", "25569"]:
        return "Airtel"
    elif prefix in ["25561", "25562"]:
        return "Halopesa"
    else:
        return "Azampesa"
