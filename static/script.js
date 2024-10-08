// Preview the selected video file
document.getElementById('video-input').addEventListener('change', function() {
    const videoFile = this.files[0];
    const videoPreview = document.getElementById('video-preview');
    const convertButton = document.getElementById('convert-button');

    if (videoFile) {
        const videoURL = URL.createObjectURL(videoFile);
        videoPreview.src = videoURL;
        videoPreview.style.display = 'block'; // Show the video
        convertButton.style.display = 'block'; // Ensure the convert button is visible
    } else {
        videoPreview.style.display = 'none'; // Hide the video if no file is selected
    }
});

// Handle form submission and audio output
document.getElementById('conversion-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const loadingAnimation = document.getElementById('loading-animation');
    loadingAnimation.style.display = 'block'; // Show loading animation

    fetch(this.action, {
        method: this.method,
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        loadingAnimation.style.display = 'none';

        if (data.audio_url) {  // Ensure to check if audio_url exists in the response
            document.getElementById('audio-output').style.display = 'block';
            document.getElementById('audio-source').src = data.audio_url; // Set audio source to the received URL
            document.getElementById('output-audio').load(); // Load the new audio source
        } else {
            alert(`Error: ${data.error}`); // Alert any error message from the backend
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loadingAnimation.style.display = 'none';
        alert('An error occurred during conversion.');
    });
});

// About section functionality
document.addEventListener('DOMContentLoaded', () => {
    const aboutLink = document.getElementById('about-link');
    const aboutSection = document.getElementById('about-section');
    const closeButton = document.querySelector('.close-button');

    aboutLink.addEventListener('click', () => {
        aboutSection.style.display = 'block'; // Show the about section
    });

    closeButton.addEventListener('click', () => {
        aboutSection.style.display = 'none'; // Hide the about section
    });
});
