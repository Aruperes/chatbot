pipeline {
    agent any

    stages {
        stage('1. Persiapan (Checkout & Clean)') {
            steps {
                // Matikan proses app.py lama agar port 5001 kosong
                // '|| true' artinya jangan error kalau tidak ada proses yang jalan
                sh 'pkill -f app.py || true'
                echo 'Proses lama dimatikan. Mengambil kode baru...'
                
                // (Jenkins otomatis mengambil kode terbaru dari GitHub di sini)
            }
        }

        stage('2. Install Library') {
            steps {
                echo 'Menginstall library Python...'
                
                // --- BAGIAN YANG DIMODIFIKASI ---
                // Menambahkan --break-system-packages agar diizinkan oleh sistem VPS
                // Menambahkan --ignore-installed untuk mengatasi error "Cannot uninstall... installed by debian"
                sh 'pip3 install -r requirements.txt --break-system-packages --ignore-installed'
            }
        }

        stage('3. Deploy (Jalankan Bot)') {
            steps {
                echo 'Menjalankan Bidan Citra...'
                script {
                    // Jalankan app.py di background (nohup)
                    // Log output disimpan di server_log.txt untuk debugging
                    sh 'nohup python3 app.py > server_log.txt 2>&1 &'
                }
                echo 'Bot berhasil dijalankan di background!'
            }
        }
    }
}