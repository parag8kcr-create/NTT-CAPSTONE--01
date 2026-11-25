import sys
import re
from pathlib import Path

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    **{f"R{i}": i for i in range(16)},
    "SCREEN": 16384,
    "KBD": 24576,
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

SYMBOL_PATTERN = r"[A-Za-z_.$:][\w.$:]*"


def error(line_number, message):
    raise ValueError(f"Line {line_number}: {message}")


def clean_lines(path):
    result = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.split("//")[0].strip()

        if line:
            result.append(
                (line_number, re.sub(r"\s+", "", line))
            )

    return result


def assemble(source):
    symbols = PREDEFINED.copy()
    defined_labels = set()
    instructions = []
    rom_address = 0

    for line_number, line in source:
        if line.startswith("(") or line.endswith(")"):
            if not (line.startswith("(") and line.endswith(")")):
                error(line_number, "Invalid label declaration")

            label = line[1:-1]

            if not re.fullmatch(SYMBOL_PATTERN, label):
                error(line_number, f"Invalid label '{label}'")

            if label in defined_labels:
                print(
                    f"Warning: Line {line_number}: duplicate label '({label})' "
                    f"(already defined at ROM {symbols[label]})."
                )
            elif label in PREDEFINED:
                print(
                    f"Warning: Line {line_number}: label '({label})' matches "
                    f"predefined symbol (keeping {symbols[label]})."
                )
            else:
                defined_labels.add(label)
                symbols[label] = rom_address
        else:
            instructions.append((line_number, line))
            rom_address += 1

    machine_code = []
    next_variable = 16

    for line_number, line in instructions:
        if line.startswith("@"):
            value = line[1:]

            if not value:
                error(line_number, "Missing A-instruction address or symbol")

            if value.isdigit():
                address = int(value)
            elif re.fullmatch(SYMBOL_PATTERN, value):
                if value not in symbols:
                    symbols[value] = next_variable
                    next_variable += 1
                address = symbols[value]
            else:
                error(line_number, f"Invalid symbol '{value}'")

            if not 0 <= address <= 32767:
                error(line_number, f"Address out of range: {address}")

            machine_code.append(f"{address:016b}")
            continue

        if line.count("=") > 1 or line.count(";") > 1:
            error(line_number, f"Invalid instruction '{line}'")

        if ";" in line:
            instruction, jump = line.split(";")
        else:
            instruction, jump = line, ""

        if "=" in instruction:
            dest, comp = instruction.split("=")
        else:
            dest, comp = "", instruction

        aliases = {
            "A+D": "D+A",
            "M+D": "D+M",
            "A&D": "D&A",
            "M&D": "D&M",
            "A|D": "D|A",
            "M|D": "D|M",
        }
        comp = aliases.get(comp, comp)

        if comp not in COMP:
            error(line_number, f"Invalid comp mnemonic '{comp}'")

        if dest not in DEST:
            error(line_number, f"Invalid dest mnemonic '{dest}'")

        if jump not in JUMP:
            error(line_number, f"Invalid jump mnemonic '{jump}'")

        machine_code.append(
            "111" + COMP[comp] + DEST[dest] + JUMP[jump]
        )

    return machine_code


def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.is_file():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    try:
        source = clean_lines(input_path)
        machine_code = assemble(source)

        output_path = input_path.with_suffix(".hack")
        output_path.write_text(
            "\n".join(machine_code) + "\n" if machine_code else "",
            encoding="utf-8",
        )

        print("Assembly successful!")
        print(f"Output: {output_path}")
        print(f"Total instructions: {len(machine_code)}")

    except (ValueError, OSError) as exc:
        print(f"Assembly error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()