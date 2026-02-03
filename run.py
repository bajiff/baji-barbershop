from app import create_app

# Panggil fungsi pabrik aplikasi
app = create_app()

if __name__ == '__main__':
    # Debug=True artinya server akan restart otomatis kalau ada perubahan kode
    app.run(debug=True)