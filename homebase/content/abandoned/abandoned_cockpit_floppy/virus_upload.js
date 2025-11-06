document.addEventListener('DOMContentLoaded', () => {
    const progressBar = document.getElementById('progressBar');
    const timeRemainingDisplay = document.getElementById('timeRemaining');
    const DURATION_MINUTES = 1;
    const DURATION_SECONDS = DURATION_MINUTES * 60;
    const UPDATE_INTERVAL_MS = 1000; // Update every 1 second
    let timeElapsed = 0;

    // Function to update the progress bar and timer
    function updateProgress() {
        if (timeElapsed >= DURATION_SECONDS) {
            // The danger has happened! Stop the interval and finalize.
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            timeRemainingDisplay.textContent = '00:00';
            document.querySelector('h1').textContent = '💥 UPLOAD COMPLETE 💥';
            document.querySelector('.warning-glow').textContent = 'STATUS: ISS RIDDLE TAKEOVER COMPLETE';
            return;
        }

        // 1. Update Progress Bar
        const percentage = (timeElapsed / DURATION_SECONDS) * 100;
        progressBar.style.width = percentage + '%';

        // 2. Update Countdown Timer
        const secondsRemaining = DURATION_SECONDS - timeElapsed;
        const minutes = Math.floor(secondsRemaining / 60);
        const seconds = secondsRemaining % 60;
        
        // Format to MM:SS
        const formattedTime = 
            String(minutes).padStart(2, '0') + ':' + 
            String(seconds).padStart(2, '0');
        
        timeRemainingDisplay.textContent = formattedTime;

        // Increment for the next interval
        timeElapsed++;
    }

    // Start the progress update interval
    const progressInterval = setInterval(updateProgress, UPDATE_INTERVAL_MS);

    // Run once immediately to set the initial state (10:00 and 0%)
    updateProgress();
});