import sys
import re

class TonyPytony:
    """
    Motore di esecuzione per il linguaggio TonyPYtony.
    Gestisce l'allocazione delle variabili, la valutazione delle espressioni
    e l'output dei dati tramite un interprete basato su stringhe.
    """

    def __init__(self):
        # Registro di memoria locale per le variabili del programma
        self.variables = {}

    def run_line(self, line):
        """
        Analizza ed esegue una singola riga di codice TonyPYtony.
        """
        line = line.strip()
        
        # Ignora righe vuote e commenti (prefissi con //)
        if not line or line.startswith("//"):
            return

        # --- Gestione Comando 'urla' (Standard Output) ---
        if line.startswith("urla "):
            # Estrazione del valore dopo la parola chiave 'urla'
            val = line[5:].strip()
            print(self.get_value(val))

        # --- Gestione Comando 'bomboroide' (Assegnazione Variabili) ---
        elif line.startswith("bomboroide "):
            # Utilizzo di espressioni regolari per validare il formato: bomboroide x = y
            match = re.match(r"bomboroide (.+) = (.+)", line)
            if match:
                var_name, var_expr = match.groups()
                # Valutazione dell'espressione e memorizzazione nel registro
                self.variables[var_name.strip()] = self.evaluate_expression(var_expr.strip())

    def get_value(self, token):
        """
        Risolve un token restituendo un intero, una stringa o il valore di una variabile.
        """
        token = token.strip()
        
        # Gestione delle stringhe letterali (es. "testo")
        if token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        
        # Gestione dei valori numerici interi
        if token.isdigit():
            return int(token)
        
        # Risoluzione della variabile dal registro o restituzione errore di runtime
        return self.variables.get(token, f"Runtime Error: {token} non è stato definito nel contesto.")

    def evaluate_expression(self, expr):
        """
        Valuta espressioni aritmetiche semplici o concatenazioni.
        Implementa l'operatore 'movimento' per la somma/unione.
        """
        # Verifica la presenza dell'operatore binario 'movimento'
        if " movimento " in expr:
            parts = expr.split(" movimento ")
            val1 = self.get_value(parts[0])
            val2 = self.get_value(parts[1])
            
            # Esegue l'operazione se entrambi i valori sono validi
            try:
                return val1 + val2
            except TypeError:
                return f"Runtime Error: Impossibile eseguire 'movimento' tra {type(val1)} e {type(val2)}"
        
        # Se non ci sono operatori, risolve il valore singolo
        return self.get_value(expr)

def main():
    """
    Punto di ingresso dell'interprete via CLI (Command Line Interface).
    """
    # Verifica la presenza dell'argomento obbligatorio (file sorgente)
    if len(sys.argv) < 2:
        print("TonyPytony Engine v1.0")
        print("Utilizzo: tony <percorso_file.ptny>")
        return

    interpreter = TonyPytony()
    filename = sys.argv[1]

    try:
        # Lettura sequenziale del file sorgente
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                try:
                    interpreter.run_line(line)
                except Exception as e:
                    print(f"Errore alla riga {line_number}: {e}")
                    
    except FileNotFoundError:
        print(f"Errore di Sistema: Il file '{filename}' non è stato trovato.")
    except PermissionError:
        print(f"Errore di Sistema: Permessi insufficienti per leggere '{filename}'.")

if __name__ == "__main__":
    main()
