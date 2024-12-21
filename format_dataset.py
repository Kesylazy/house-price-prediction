import json
import sys

# -------------------- CONSTANTS -------------------- #
INPUT_FILE = "dataset.json"
OUTPUT_FILE = "formatted_dataset.json"

# -------------------- FUNCTION TO FORMAT JSON -------------------- #
def format_json_file(input_path, output_path):
    """
    Reads a raw JSON file, corrects its structure, and saves it as a formatted JSON file.
    Args:
        input_path (str): Path to the input JSON file.
        output_path (str): Path to save the formatted JSON file.
    """
    try:
        # Legge il contenuto grezzo del file
        with open(input_path, "r", encoding="utf-8") as file:
            raw_content = file.read()

        # Corregge la struttura del JSON
        corrected_content = "[" + raw_content.replace("}{", "},{") + "]"

        # Tenta di convertire in JSON
        data = json.loads(corrected_content)

        # Salva il JSON formattato
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"✅ File JSON formattato correttamente e salvato in: {output_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Errore nel formato JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ File non trovato: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore inaspettato: {e}")
        sys.exit(1)

# -------------------- ENTRY POINT -------------------- #
if __name__ == "__main__":
    print(f"🔄 Formattazione del file JSON: {INPUT_FILE}")
    format_json_file(INPUT_FILE, OUTPUT_FILE)
