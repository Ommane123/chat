import os

def set_streamlit_theme(theme_choice):
    """
    Update .streamlit/config.toml to set the theme base to light or dark.
    theme_choice should be 'Light' or 'Dark'.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    streamlit_dir = os.path.join(base_dir, ".streamlit")
    config_path = os.path.join(streamlit_dir, "config.toml")

    # Create .streamlit directory if it doesn't exist
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)

    lines = []
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            lines = f.readlines()

    # Find [theme] section and base
    theme_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("[theme]"):
            theme_idx = i
            break

    new_base_line = f'base = "{ "light" if theme_choice == "Light" else "dark" }"\n'

    if theme_idx == -1:
        # Append theme section
        lines.append("\n[theme]\n")
        lines.append(new_base_line)
    else:
        # Try to find base inside theme section
        base_updated = False
        for i in range(theme_idx + 1, len(lines)):
            if lines[i].strip().startswith("["):
                # Another section starts
                break
            if lines[i].strip().startswith("base"):
                lines[i] = new_base_line
                base_updated = True
                break
        
        if not base_updated:
            lines.insert(theme_idx + 1, new_base_line)

    try:
        with open(config_path, "w") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error saving theme: {e}")
        return False

