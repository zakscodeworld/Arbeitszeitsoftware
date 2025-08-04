import requests
import json
import sys
from datetime import datetime

print("API-Diagnose-Tool für BBQ GmbH Zeiterfassung")
print("============================================")

# API-Basis-URL
API_BASE = "http://localhost:8000/api/v1"

# Test-Token (muss angepasst werden mit einem gültigen Token)
token = input("Bitte geben Sie Ihren Zugriffstoken ein (oder drücken Sie Enter für einen anonymen Test): ")

# Headers für API-Anfragen
headers = {
    "Content-Type": "application/json"
}

if token:
    headers["Authorization"] = f"Bearer {token}"

def test_endpoint(endpoint, method="GET", data=None):
    """Testet einen API-Endpunkt und gibt Details zurück"""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\nTeste {method} {url}")
    
    try:
        start_time = datetime.now()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        print(f"Status: {response.status_code} {response.reason}")
        print(f"Zeit: {duration_ms}ms")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                json_data = response.json()
                if isinstance(json_data, list):
                    print(f"Anzahl der Datensätze: {len(json_data)}")
                    if len(json_data) > 0:
                        print(f"Beispieleintrag: {json.dumps(json_data[0], indent=2, ensure_ascii=False)[:200]}...")
                else:
                    print(f"Antwort: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}...")
                return True, json_data
            except Exception as e:
                print(f"Fehler beim Parsen der JSON-Antwort: {e}")
                return False, None
        else:
            try:
                error_data = response.json()
                print(f"Fehlerantwort: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Fehlerantwort: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"Fehler bei der Anfrage: {str(e)}")
        return False, None

def run_diagnostics():
    """Führt alle Diagnosetests durch"""
    results = {}
    
    # Test 1: API-Verfügbarkeit
    print("\n=== Test 1: API-Verfügbarkeit ===")
    results["api_status"] = test_endpoint("/")
    
    # Test 2: Benutzerinformationen (wenn eingeloggt)
    if token:
        print("\n=== Test 2: Benutzerinformationen ===")
        success, user_data = test_endpoint("/users/me")
        results["user_info"] = success
        
        if success and user_data:
            role_id = user_data.get("rolle_id")
            role_name = user_data.get("rolle", {}).get("name", "Unbekannt")
            print(f"Angemeldeter Benutzer: {user_data.get('username', 'Unbekannt')}")
            print(f"Rolle: {role_name} (ID: {role_id})")
            
            # Prüfe, ob der Benutzer Administrator ist
            is_admin = role_id == 1 or role_name.lower() == "administrator"
            print(f"Administrator-Rechte: {'Ja' if is_admin else 'Nein'}")
            
            if is_admin:
                # Test 3: Benutzerliste (nur für Administratoren)
                print("\n=== Test 3: Benutzerliste abrufen ===")
                success, users_data = test_endpoint("/users/")
                results["users_list"] = success
                
                if success and isinstance(users_data, list):
                    print(f"Benutzerliste erfolgreich abgerufen: {len(users_data)} Benutzer gefunden")
                
                # Test 4: Rollenliste 
                print("\n=== Test 4: Rollenliste abrufen ===")
                success, roles_data = test_endpoint("/roles/")
                results["roles_list"] = success
                
                if success and isinstance(roles_data, list):
                    print(f"Rollenliste erfolgreich abgerufen: {len(roles_data)} Rollen gefunden")
    else:
        print("\nKeine Authentifizierung - überspringe Benutzer- und Rollentests")
    
    # Zusammenfassung
    print("\n=== Diagnoseergebnis ===")
    all_success = all([r[0] for r in results.values() if r is not None])
    
    if all_success:
        print("✅ Alle Tests erfolgreich durchgeführt!")
    else:
        print("❌ Einige Tests sind fehlgeschlagen:")
        for test, (success, _) in results.items():
            print(f" - {test}: {'✅ Erfolg' if success else '❌ Fehler'}")
    
    return results

if __name__ == "__main__":
    run_diagnostics()
