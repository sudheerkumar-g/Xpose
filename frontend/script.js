// DOM Elements
const imageUpload = document.getElementById('imageUpload');
const uploadText = document.getElementById('uploadText');
const previewImage = document.getElementById('previewImage');
const analyzeButton = document.getElementById('analyzeButton');
const resultText = document.getElementById('resultText');

// Event Listener for Image Upload
imageUpload.addEventListener('change', function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImage.src = e.target.result;
      previewImage.style.display = 'block';
      uploadText.innerText = 'Change Image';
      analyzeButton.disabled = false;
    };
    reader.readAsDataURL(file);
  }
});

// Single Event Listener for Analyze Button
analyzeButton.addEventListener('click', async function () {
  const file = imageUpload.files[0];
  if (!file) {
    alert('Please upload an image first.');
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.innerText = 'Analyzing...';
  resultText.innerText = 'Processing...';

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://127.0.0.1:8000/analyze/', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    resultText.innerText = `Result: ${data.result}`;
  } catch (error) {
    resultText.innerText = 'Error analyzing image.';
    console.error(error);
  }

  analyzeButton.disabled = false;
  analyzeButton.innerText = 'Analyze Image';
});
