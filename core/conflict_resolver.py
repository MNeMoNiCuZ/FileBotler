import os

def detect_conflicts(changes):
    conflicts = []
    for change in changes:
        if change[0] in ["move", "copy"]:
            _, (src, dst) = change
            if os.path.exists(dst):
                conflicts.append((src, dst))
    return conflicts

def resolve_conflicts(changes):
    conflicts = detect_conflicts(changes)
    
    if conflicts:
        print("\nFile conflicts detected:")
        for src, dst in conflicts:
            print(f"{src} -> {dst} (already exists)")
        
        while True:
            choice = input("\nHow would you like to resolve these conflicts?\n"
                           "1. Abort operation\n"
                           "2. Add numbers to conflicting files\n"
                           "3. Overwrite existing files\n"
                           "Enter your choice (1/2/3): ")
            if choice in ['1', '2', '3']:
                break
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        if choice == '1':
            return None
        elif choice == '2':
            return resolve_conflicts_with_numbers(changes)
        else:
            return changes  # Proceed with overwriting
    
    return changes

def resolve_conflicts_with_numbers(changes):
    new_changes = []
    for change in changes:
        if change[0] in ["move", "copy"]:
            op, (src, dst) = change
            base, ext = os.path.splitext(dst)
            counter = 1
            while os.path.exists(dst):
                dst = f"{base}_{counter}{ext}"
                counter += 1
            new_changes.append((op, (src, dst)))
        else:
            new_changes.append(change)
    return new_changes