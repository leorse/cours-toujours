import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def verify():
    print("--- Starting Verification ---")
    session = requests.Session()

    # 1. Test Non-Admin Access
    print("\n1. Testing Non-Admin Access...")
    username = "TestUser_Normal"
    # Try to login/create
    resp = session.post(f"{BASE_URL}/users/", data={"username": username}, allow_redirects=False)
    
    # Try to access debug
    resp = session.get(f"{BASE_URL}/debug", allow_redirects=False)
    if resp.status_code in [303, 307] and resp.headers['Location'] == "/":
        print("✅ Non-admin redirected to /")
    else:
        print(f"❌ Non-admin access failed check. Status: {resp.status_code}, Location: {resp.headers.get('Location')}")

    # 2. Test Admin Access
    print("\n2. Testing Admin Access...")
    session_admin = requests.Session()
    username_admin = "_ADMIN"
    resp = session_admin.post(f"{BASE_URL}/users/", data={"username": username_admin}, allow_redirects=False)
    
    # Test Root Debug Redirect
    resp = session_admin.get(f"{BASE_URL}/debug", allow_redirects=False)
    if resp.status_code in [303, 307] and "/debug/stats" in resp.headers['Location']:
        print("✅ Admin redirected to /debug/stats")
    else:
        print(f"❌ Admin root redirect failed. Status: {resp.status_code}, Location: {resp.headers.get('Location')}")

    # Test Pages
    pages = [
        ("/debug/stats", "Statistiques"),
        ("/debug/exercises", "Exercices"),
        ("/debug/dialogues", "Dialogues"),
        ("/debug/animations", "Tests des Animations")
    ]

    for url_suffix, keyword in pages:
        resp = session_admin.get(f"{BASE_URL}{url_suffix}")
        if resp.status_code == 200 and keyword in resp.text:
            print(f"✅ {url_suffix} loaded correctly.")
        else:
            print(f"❌ {url_suffix} failed. Status: {resp.status_code}, Keyword '{keyword}' found: {keyword in resp.text}")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"Verification crashed: {e}")
