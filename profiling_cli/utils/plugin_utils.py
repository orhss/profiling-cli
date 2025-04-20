from typing import Any


def parse_line_profiler_output(output_text: str) -> tuple:
    """
    Parses the output from line_profiler and returns the raw function text and structured data.

    :param output_text: The raw text output from line_profiler
    :return (function_texts, profile_data) where:
            - function_texts (list): List of raw function texts with proper indentation
            - profile_data (list): List of dictionaries, one per profiled function
    """
    # Split the output into sections per function
    lines = output_text.strip().split('\n')

    # Extract metadata (total time, file path)
    metadata = {}
    for line in lines:
        if line.startswith('Total time:'):
            metadata['total_time'] = line.split(':', 1)[1].strip()
        elif line.startswith('File:'):
            metadata['file'] = line.split(':', 1)[1].strip()

    # Split into function sections
    function_sections = []
    current_section = []
    function_headers = []

    # Check if this is a standard line_profiler output or a different format
    is_standard_format = any(line.startswith('Function:') for line in lines)

    if is_standard_format:
        # Standard format with "Function:" headers
        for line in lines:
            if line.startswith('Function:'):
                if current_section:
                    function_sections.append(current_section)
                current_section = [line]
                function_headers.append(line)
            else:
                current_section.append(line)
    else:
        # Alternative format with "Function N:" headers
        for i, line in enumerate(lines):
            if line.startswith('Function ') and ':' in line:
                if current_section:
                    function_sections.append(current_section)
                current_section = [line]
                function_headers.append(line)
            else:
                current_section.append(line)

    # Add the last section if not empty
    if current_section:
        function_sections.append(current_section)

    function_texts = []
    profile_data = []

    for section_idx, section in enumerate(function_sections):
        if not section:
            continue

        # Extract function name and line number based on format
        func_line = section[0]
        func_name = ""
        line_num = 0

        if is_standard_format:
            # Standard format: "Function: xyz at line N"
            try:
                func_parts = func_line.split('Function:')
                if len(func_parts) < 2:
                    continue

                name_line_parts = func_parts[1].split('at line')
                if len(name_line_parts) < 2:
                    continue

                func_name = name_line_parts[0].strip()
                line_num = int(name_line_parts[1].strip())
            except (ValueError, IndexError):
                continue
        else:
            # Alternative format: "Function N: xyz"
            try:
                # Extract the line number from the first data line
                for data_line in section[1:]:
                    if data_line.strip() and data_line.lstrip()[0].isdigit():
                        line_num = int(data_line.lstrip().split()[0])
                        break

                # Extract function name if present
                if "(" in func_line and ")" in func_line:
                    func_name = func_line.split("(")[1].split(")")[0]
                else:
                    func_name = f"function_{section_idx + 1}"
            except Exception:
                func_name = f"function_{section_idx + 1}"

        function_info = {
            'function_name': func_name,
            'line_number': line_num,
            'file': metadata.get('file', ''),
            'total_time': metadata.get('total_time', ''),
            'lines': []
        }

        # Process the code lines
        raw_function_lines = []

        # Skip the header line
        for i in range(1, len(section)):
            line = section[i]
            if not line.strip():
                continue

            # Check if this is a data line (has a line number at the beginning)
            try:
                line_parts = line.lstrip().split()
                if not line_parts or not line_parts[0].isdigit():
                    continue

                line_number = int(line_parts[0])

                # Extract code with indentation using our specialized function
                code_with_indent, indentation = extract_code_from_profiler_line(line)

                # Extract profile metrics
                hits = None
                time_value = None
                per_hit = None
                percent_time = None

                # Try to extract metrics if available
                if len(line_parts) > 1 and line_parts[1].isdigit():
                    hits = int(line_parts[1])

                if len(line_parts) > 2 and is_float(line_parts[2]):
                    time_value = float(line_parts[2])

                if len(line_parts) > 3 and is_float(line_parts[3]):
                    per_hit = float(line_parts[3])

                if len(line_parts) > 4 and is_float(line_parts[4]):
                    percent_time = float(line_parts[4])

                # Add to the profile data
                line_info = {
                    'line_number': line_number,
                    'hits': hits,
                    'time': time_value,
                    'per_hit': per_hit,
                    'percent_time': percent_time,
                    'code': code_with_indent.strip(),
                    'indentation': indentation
                }

                function_info['lines'].append(line_info)
                raw_function_lines.append(code_with_indent)

            except Exception as e:
                print(f"Error processing line: {line}")
                print(f"Error details: {e}")
                continue

        # Join the raw function lines with proper indentation
        function_text = '\n'.join(raw_function_lines)
        function_texts.append(function_text)
        profile_data.append(function_info)

    return function_texts, profile_data


def extract_code_from_profiler_line(line: str) -> tuple:
    """
    Extract the code portion and its indentation from a line profiler output line.

    :param line: A line profiler output from line_profiler
    :return: Tuple (code_with_indentation, indentation_level)
    """
    import re

    # First, check if line is empty or doesn't contain any content
    if not line or not line.strip():
        return "", 0

    # Split the line into parts
    parts = line.lstrip().split()
    if not parts:
        return "", 0

    # Make sure it's a line number line
    if not parts[0].isdigit():
        return line.strip(), 0

    # Pattern 1: Look for where the code starts after % Time column (standard format)
    # This looks for the first occurrence of multiple spaces after the percentage column
    pattern1 = r'^\s*\d+\s+(?:\d+|\s+)\s+(?:\d+\.\d+|\s+)\s+(?:\d+\.\d+|\s+)\s+(?:\d+\.\d+|\s+)(\s{2,}.*$)'
    match1 = re.search(pattern1, line)

    if match1:
        code_part = match1.group(1)
        return code_part, len(code_part) - len(code_part.lstrip())

    # Pattern 2: Look for indented Python code after metrics
    # This checks for common Python indentation patterns
    pattern2 = r'^\s*\d+.*?(\s{2,}[a-zA-Z_][a-zA-Z0-9_]*.*$)'
    match2 = re.search(pattern2, line)

    if match2:
        code_part = match2.group(1)
        return code_part, len(code_part) - len(code_part.lstrip())

    # Pattern 3: Just look for any indentation after numbers
    pattern3 = r'^\s*\d+.*?(\s{2,}\S.*$)'
    match3 = re.search(pattern3, line)

    if match3:
        code_part = match3.group(1)
        return code_part, len(code_part) - len(code_part.lstrip())

    # Fallback: Just extract everything after the line number and any metrics
    # First, extract the line number
    line_num = parts[0]
    line_without_num = line[line.find(line_num) + len(line_num):]

    # Try to skip past any metrics (numbers with decimal points)
    remaining_parts = line_without_num.split()
    skip_count = 0

    for part in remaining_parts:
        if is_float(part) or part.isdigit() or part == "":
            skip_count += 1
        else:
            break

    if skip_count > 0 and skip_count < len(remaining_parts):
        # Find the position after the metrics
        pos = 0
        for i in range(skip_count):
            if i < len(remaining_parts):
                next_pos = line_without_num.find(remaining_parts[i], pos) + len(remaining_parts[i])
                if next_pos > pos:
                    pos = next_pos

        if pos < len(line_without_num):
            code_part = line_without_num[pos:]
            # Find first non-whitespace character
            match = re.search(r'(\s*\S.*$)', code_part)
            if match:
                code_part = match.group(1)
                return code_part, len(code_part) - len(code_part.lstrip())

    # Last resort: return a default result
    return line.strip(), 0


def is_float(value: Any) -> bool:
    """Check if a string can be converted to a float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
