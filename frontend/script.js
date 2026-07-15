const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');
const promptChips = document.querySelectorAll('.prompt-chip');

const API_URL = window.location.origin.startsWith('http')
  ? '/chat'
  : 'http://127.0.0.1:8000/chat';

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function createMessage(text, sender) {
  const message = document.createElement('div');
  message.className = `message ${sender}`;
  message.textContent = text;
  chatWindow.appendChild(message);
  scrollToBottom();
  return message;
}

function createTypingIndicator() {
  const message = document.createElement('div');
  message.className = 'message bot typing';
  message.innerHTML = '<span></span><span></span><span></span>';
  chatWindow.appendChild(message);
  scrollToBottom();
  return message;
}

function clearChat() {
  chatWindow.innerHTML = '';
}

async function sendMessage(question) {
  const trimmed = question.trim();
  if (!trimmed) return;

  createMessage(trimmed, 'user');
  input.value = '';
  input.focus();

  const typing = createTypingIndicator();
  form.querySelector('button').disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: trimmed }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    typing.remove();
    createMessage(data.response ?? 'I could not generate a response.', 'bot');
  } catch (error) {
    typing.remove();
    createMessage(
      'Sorry — the banking assistant could not reach the backend right now. Please make sure the FastAPI server is running.',
      'system'
    );
    console.error(error);
  } finally {
    form.querySelector('button').disabled = false;
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

promptChips.forEach((chip) => {
  chip.addEventListener('click', () => {
    sendMessage(chip.dataset.prompt || chip.textContent || '');
  });
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    clearChat();
  }
});

clearChat();
createMessage('Namaste! Welcome to NYC Tekpair Bharat support. Ask anything about failed UPI payments, RuPay/Visa cards, or account queries.', 'bot');

// Sidebar Offers Carousel Auto-Rotation Script
const slides = document.querySelectorAll('.carousel-slide');
const dots = document.querySelectorAll('.carousel-dots .dot');
let currentSlide = 0;

function showSlide(index) {
  if (slides.length === 0) return;
  slides[currentSlide].classList.remove('active');
  dots[currentSlide].classList.remove('active');
  currentSlide = (index + slides.length) % slides.length;
  slides[currentSlide].classList.add('active');
  dots[currentSlide].classList.add('active');
}

function autoSlide() {
  showSlide(currentSlide + 1);
}

if (slides.length > 0) {
  let slideInterval = setInterval(autoSlide, 5000);
  dots.forEach((dot, idx) => {
    dot.addEventListener('click', () => {
      clearInterval(slideInterval);
      showSlide(idx);
      slideInterval = setInterval(autoSlide, 5000);
    });
  });
}
