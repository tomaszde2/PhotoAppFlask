from app import create_app

# Wywołujemy funkcję fabryki, która składa całą naszą aplikację w jedną całość
app = create_app()

if __name__ == '__main__':
    # Tryb debug=True sprawia, że serwer sam się zrestartuje,
    # gdy wprowadzisz jakieś zmiany w plikach Pythona, i pokaże ewentualne błędy w przeglądarce.
    app.run(host='0.0.0.0', port=5000, debug=True)