pipeline {
    agent any

    stages {
        stage('1. Persiapan (Checkout & Clean)') {
            steps {
                // Matikan proses app.py lama agar port 5001 kosong
                // '|| true' artinya jangan error kalau tidak ada proses yang jalan
                sh 'pkill -f app.py || true'
                echo 'Proses lama dimatikan. Mengambil kode baru...'
                
                // Mengambil kode terbaru dari GitHub (otomatis dilakukan Jenkins)
            }
        }

        stage('2. Install Library') {
            steps {
                echo 'Menginstall library Python...'
                // Install library yang ada di requirements.txt
                // Menggunakan --break-system-packages jika di Ubuntu terbaru, atau virtualenv (opsional)
                sh 'pip3 install -r requirements.txt || pip install -r requirements.txt'
            }
        }

        stage('3. Deploy (Jalankan Bot)') {
            steps {
                echo 'Menjalankan Bidan Citra...'
                script {
                    // Jalankan app.py di background (nohup)
                    // Log output disimpan di server_log.txt
                    sh 'nohup python3 app.py > server_log.txt 2>&1 &'
                }
                echo 'Bot berhasil dijalankan di background!'
            }
        }
    }
}