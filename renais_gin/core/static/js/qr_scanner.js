// This script uses the jsQR library for QR code scanning.
// Include jsQR library in your static files or use a CDN.

// We'll assume we are including jsQR via CDN for now.

document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('qr-video');
    const startScannerButton = document.getElementById('start-scanner');
    const stopScannerButton = document.getElementById('stop-scanner');
    const qrResult = document.getElementById('qr-result');
    const bottleIdSpan = document.getElementById('bottle-id');
    const registerBottleButton = document.getElementById('register-bottle');
    let scanning = false;
    let stream = null;

    // Check if the browser supports the mediaDevices API
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        startScannerButton.addEventListener('click', startScanner);
        stopScannerButton.addEventListener('click', stopScanner);
    } else {
        startScannerButton.disabled = true;
        startScannerButton.textContent = 'Scanner not supported';
    }

    function startScanner() {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
            .then(function(s) {
                stream = s;
                video.srcObject = stream;
                video.play();
                scanning = true;
                startScannerButton.style.display = 'none';
                stopScannerButton.style.display = 'inline-block';
                requestAnimationFrame(scanQR);
            })
            .catch(function(err) {
                console.error('Error accessing camera: ', err);
                alert('Cannot access camera: ' + err.message);
            });
    }

    function stopScanner() {
        scanning = false;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
        startScannerButton.style.display = 'inline-block';
        stopScannerButton.style.display = 'none';
    }

    function scanQR() {
        if (!scanning) return;

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            if (code) {
                // Found a QR code
                const bottleId = code.data;
                bottleIdSpan.textContent = bottleId;
                qrResult.style.display = 'block';
                stopScanner();
                // Set the bottle ID in the manual form as well
                document.getElementById('bottle_id').value = bottleId;
            }
        }
        requestAnimationFrame(scanQR);
    }

    registerBottleButton.addEventListener('click', function() {
        const bottleId = bottleIdSpan.textContent;
        registerBottle(bottleId);
    });

    function registerBottle(bottleId) {
        // We'll use the manual form to submit the bottle ID
        document.getElementById('bottle_id').value = bottleId;
        document.getElementById('manual-form').submit();
    }
});