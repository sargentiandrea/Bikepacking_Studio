import os

# File e cartelle da ignorare durante la scansione
IGNORE_DIRS = {'.git', '.idea', '.vscode', 'venv', 'env'}
IGNORE_FILES = {'.DS_Store', 'project_structure.txt'}

def build_tree(dir_path, prefix=""):
    """
    Scansiona ricorsivamente la cartella e genera la struttura ad albero formattata.
    """
    entries = sorted(os.listdir(dir_path))
    
    # Filtra cartelle/file ignorati
    entries = [
        e for e in entries 
        if e not in IGNORE_FILES and e not in IGNORE_DIRS
    ]
    
    tree_str = ""
    count = len(entries)
    
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == count - 1)
        
        # Indicatori grafici per l'albero
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "
        
        tree_str += f"{prefix}{connector}{entry}\n"
        
        if os.path.isdir(path):
            tree_str += build_tree(path, prefix + child_prefix)
            
    return tree_str

def main():
    # Ottieni la radice del progetto (dove si trova questo script)
    project_root = os.path.dirname(os.path.abspath(__file__))
    project_name = os.path.basename(project_root)
    output_filename = "project_structure.txt"
    
    # Intestazione dell'albero
    header = f"{project_name}/\n│\n"
    tree_content = build_tree(project_root)
    full_output = header + tree_content
    
    # Scrittura nel file TXT
    output_path = os.path.join(project_root, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print(f"✅ Struttura del progetto esportata con successo in: {output_filename}")

if __name__ == "__main__":
    main()