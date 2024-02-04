import random
import string

def read_file_to_array(path):
    """
    Lee un archivo de texto desde la ruta dada, convierte cada línea a minúsculas 
    y elimina los saltos de línea, luego devuelve un array de estas líneas.

    :param path: Ruta del archivo de texto a leer.
    :return: Array de líneas en minúsculas y sin saltos de línea del archivo.
    """
    try:
        with open(path, 'r') as file:
            return [line.strip().lower() for line in file]
    except Exception as e:
        return str(e)


def generate_random_id(length=12):
    # Define the characters that can be used in the ID
    characters = string.ascii_letters + string.digits  # This includes both letters and numbers

    # Generate a random string of the specified length
    random_id = ''.join(random.choice(characters) for _ in range(length))
    
    return random_id