import glob

for filepath in glob.glob('**/*.py', recursive=True):
    if 'venv' in filepath or '.buildozer' in filepath:
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    for line in lines:
        # Se la riga crea un Button con background_color ma senza background_normal
        if 'Button(' in line and 'background_color' in line and 'background_normal' not in line:
            line = line.replace('background_color', "background_normal='', background_color")
            modified = True
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"[OK] Aggiornato file: {filepath}")

print("Patch completata con successo!")
