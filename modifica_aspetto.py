from pathlib import Path
import shutil

file = Path("app_finanziaria.py")
backup = Path("app_finanziaria_BACKUP_INDENTAZIONE.py")

shutil.copy2(file, backup)

text = file.read_text(encoding="utf-8")

old = '''if score is None:
    st.write(
        "Non ci sono dati sufficienti per formulare "
        "un giudizio sul contesto."
    )

        "Non ci sono dati sufficienti per formulare "
        "un giudizio sul contesto."
    )
'''

new = '''if score is None:
    st.write(
        "Non ci sono dati sufficienti per formulare "
        "un giudizio sul contesto."
    )
'''

if old not in text:
    raise SystemExit("ERRORE: duplicazione non trovata.")

text = text.replace(old, new, 1)

file.write_text(text, encoding="utf-8")

print("Correzione indentazione completata.")
print("Backup creato:", backup)